from flask import Blueprint, jsonify, request
import numpy as np
from controllers.authentication import login_required
from scipy.optimize import linprog
algo_bp = Blueprint('algorithms', __name__)

def is_saddle_point(matrix, row, col):
    element = matrix[row][col]
    if element != min(matrix[row]):
        return False
    if element != max(matrix[i][col] for i in range(len(matrix))):
        return False
    return True

def find_saddle_points(matrix, output_type='tuple'):
    saddle_points = []
    if not matrix:
        return saddle_points
    
    row_min = [min(row) for row in matrix]
    col_max = [max(col) for col in zip(*matrix)]
    
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == row_min[i] and matrix[i][j] == col_max[j]:
                saddle_points.append((i, j) if output_type == 'tuple' else [i, j])
    
    return saddle_points

def find_saddle_points_for_both(matrix_a, matrix_b):
    return {
        "matrix_a": find_saddle_points(matrix_a, 'tuple'),
        "matrix_b": find_saddle_points(matrix_b, 'tuple')}

def is_pareto_optimal(matrix_a, matrix_b):
    pareto_optimal_points = []
    n = len(matrix_a)
    m = len(matrix_a[0])

    for i in range(n):
        for j in range(m):
            current_a = matrix_a[i][j]
            current_b = matrix_b[i][j]
            is_optimal = True
            for x in range(n):
                for y in range(m):
                    if (matrix_a[x][y] >= current_a and
                        matrix_b[x][y] >= current_b and
                        (matrix_a[x][y] > current_a or matrix_b[x][y] > current_b)):
                        is_optimal = False
                        break
                if not is_optimal:
                    break
            if is_optimal:
                pareto_optimal_points.append((i, j, current_a, current_b))

    return pareto_optimal_points

def is_nash_equilibrium(matrix_a, matrix_b):
    nash_points = []
    n = len(matrix_a)
    m = len(matrix_a[0])

    for i in range(n):
        for j in range(m):
            current_a = matrix_a[i][j]
            current_b = matrix_b[i][j]
            is_nash = True

            for k in range(n):
                if matrix_a[k][j] > current_a:
                    is_nash = False
                    break

            if is_nash:
                for l in range(m):
                    if matrix_b[i][l] > current_b:
                        is_nash = False
                        break

            if is_nash:
                nash_points.append((i, j, current_a, current_b))

    return nash_points

def generate_matrix_with_saddle_points(rows, cols, saddle_points_count, max_attempts=100):
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        matrix = np.random.randint(0, 100, size=(rows, cols)).tolist()

        current_saddle_points = find_saddle_points(matrix, 'list')
        while len(current_saddle_points) < saddle_points_count:
            i, j = np.random.randint(0, rows), np.random.randint(0, cols)
            matrix[i] = [max(x, matrix[i][j]) for x in matrix[i]]
            for row in matrix:
                row[j] = min(row[j], matrix[i][j])
            current_saddle_points = find_saddle_points(matrix)

        while len(current_saddle_points) > saddle_points_count:
            idx = np.random.randint(0, len(current_saddle_points))
            i, j = current_saddle_points[idx]
            matrix[i][j] = np.random.randint(0, 100)
            current_saddle_points = find_saddle_points(matrix)

        if len(current_saddle_points) == saddle_points_count:
            return {
                "matrix": matrix,
                "saddle_points": current_saddle_points,
                "rows": rows,
                "cols": cols,
                "k": saddle_points_count
            }

    raise ValueError("Не удалось сгенерировать матрицу с заданным количеством седловых точек")
    
@algo_bp.route('/generate_saddle_matrix', methods=['POST'])
@login_required
def generate_saddle_matrix():
    try:
        data = request.get_json()
        rows = int(data['rows'])
        cols = int(data['cols'])
        k = int(data['k'])
        
        if k > rows * cols:
            return jsonify({"error": f"Количество седловых точек не может превышать {rows * cols}"}), 400
        
        result = generate_matrix_with_saddle_points(rows, cols, k)
        return jsonify(result)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@algo_bp.route('/calculate_mixed_matrix', methods=['POST'])
@login_required
def calculate_mixed_matrix():
    try:
        data = request.get_json()
        x = float(data['x'])
        y = float(data['y'])
        v = float(data['v'])
        a12 = float(data['a12'])

        if not (0 <= x <= 1) or not (0 <= y <= 1):
            return jsonify({'error': 'Стратегии должны быть в диапазоне [0, 1]'}), 400

        if y == 0 or (1 - x) == 0:
            return jsonify({'error': 'Недопустимые значения для расчета'}), 400

        a21 = (v * (y - x) + a12 * x * (1 - y)) / (y * (1 - x))
        a11 = (v - a12 * (1 - y)) / y
        a22 = (v - a12 * x) / (1 - x)

        matrix = [
            [round(a11, 10), round(a12, 10)],
            [round(a21, 10), round(a22, 10)]
        ]

        return jsonify({'matrix': matrix})

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

def remove_dominated_strategies(matrix):
    matrix = np.array(matrix, dtype=float)
    changed = True
    removed_rows = []
    removed_cols = []

    while changed:
        changed = False
        m, n = matrix.shape

        # Проверка доминирования по строкам (для первого игрока)
        for i in range(m):
            if i in removed_rows:
                continue
            for k in range(m):
                if k == i or k in removed_rows:
                    continue
                if np.all(matrix[i] <= matrix[k]):
                    removed_rows.append(i)
                    changed = True
                    break

        # Проверка доминирования по столбцам (для второго игрока)
        for j in range(n):
            if j in removed_cols:
                continue
            for l in range(n):
                if l == j or l in removed_cols:
                    continue
                if np.all(matrix[:,j] >= matrix[:,l]):
                    removed_cols.append(j)
                    changed = True
                    break

    # Создаем уменьшенную матрицу
    remaining_rows = [i for i in range(matrix.shape[0]) if i not in removed_rows]
    remaining_cols = [j for j in range(matrix.shape[1]) if j not in removed_cols]
    reduced_matrix = matrix[np.ix_(remaining_rows, remaining_cols)]

    return reduced_matrix, removed_rows, remaining_rows, removed_cols, remaining_cols

def solve_game(payoff_matrix):
    """Основная функция решения игры"""
    if not payoff_matrix:
        return None

    # 1. Удаление доминируемых стратегий
    reduced_matrix, removed_rows, remaining_rows, removed_cols, remaining_cols = remove_dominated_strategies(payoff_matrix)

    matrix = np.array(reduced_matrix, dtype=float)
    m, n = matrix.shape

    # 2. Поиск решения в чистых стратегиях
    row_mins = np.min(matrix, axis=1)
    v_lower = np.max(row_mins)
    col_maxs = np.max(matrix, axis=0)
    v_upper = np.min(col_maxs)

    if v_lower == v_upper:
        i = np.where(row_mins == v_lower)[0][0]
        j = np.where(col_maxs == v_upper)[0][0]

        # Восстанавливаем индексы исходной матрицы
        orig_i = remaining_rows[i]
        orig_j = remaining_cols[j]

        p_star = np.zeros(len(payoff_matrix))
        p_star[orig_i] = 1.0
        q_star = np.zeros(len(payoff_matrix[0]))
        q_star[orig_j] = 1.0

        return {
            'saddle_point': (orig_i, orig_j),
            'p_star': p_star.tolist(),
            'q_star': q_star.tolist(),
            'v': float(v_lower),
            'method': 'чистые стратегии'
        }

    # 3. Решение в смешанных стратегиях
    # Проверка на отрицательные значения
    min_val = np.min(matrix)
    if min_val < 0:
        matrix = matrix - min_val + 1

    # Решение для первого игрока
    c = np.ones(m)
    A_ub = -matrix.T
    b_ub = -np.ones(n)
    bounds = [(0, None) for _ in range(m)]
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if not res.success:
        raise ValueError("Не удалось найти решение для первого игрока")

    y = res.x
    sum_y = np.sum(y)
    v = 1 / sum_y
    p_star_reduced = y * v

    # Решение для второго игрока
    c = np.ones(n)
    A_ub = matrix
    b_ub = np.ones(m)
    bounds = [(0, None) for _ in range(n)]
    res = linprog(-c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if not res.success:
        raise ValueError("Не удалось найти решение для второго игрока")

    x = res.x
    q_star_reduced = x * v

    # Корректировка цены игры если было смещение
    if min_val < 0:
        v = v + min_val - 1

    # Восстанавливаем стратегии для исходной матрицы
    p_star = np.zeros(len(payoff_matrix))
    for idx, prob in enumerate(p_star_reduced):
        p_star[remaining_rows[idx]] = prob

    q_star = np.zeros(len(payoff_matrix[0]))
    for idx, prob in enumerate(q_star_reduced):
        q_star[remaining_cols[idx]] = prob

    return {
        'saddle_point': None,
        'p_star': p_star.tolist(),
        'q_star': q_star.tolist(),
        'v': float(v),
        'method': 'смешанные стратегии'
    }

@algo_bp.route('/solve_antagonistic_game', methods=['POST'])
@login_required
def solve_antagonistic_game():
    try:
        data = request.get_json()
        matrix = data['matrix']

        solution = solve_game(matrix)

        return jsonify({
            "solution": solution,
            "message": "Решение антагонистической игры найдено"
        })
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@algo_bp.route('/saddle_points', methods=['POST'])
@login_required
def saddle_points():
    data = request.get_json()
    matrix_a = data['matrix_a']
    matrix_b = data['matrix_b']
    result = find_saddle_points_for_both(matrix_a, matrix_b)
    return jsonify(result)

@algo_bp.route('/pareto_optimal', methods=['POST'])
@login_required
def pareto_optimal():
    data = request.get_json()
    matrix_a = data['matrix_a']
    matrix_b = data['matrix_b']
    result = is_pareto_optimal(matrix_a, matrix_b)
    return jsonify(result)

@algo_bp.route('/nash_equilibrium', methods=['POST'])
@login_required
def nash_equilibrium():
    data = request.get_json()
    matrix_a = data['matrix_a']
    matrix_b = data['matrix_b']
    result = is_nash_equilibrium(matrix_a, matrix_b)
    if result:
        return jsonify(result)
    else:
        return jsonify([])