from flask import Blueprint, jsonify, request
import numpy as np
from controllers.authentication import login_required
algo_bp = Blueprint('algorithms', __name__)

def is_saddle_point(matrix, row, col):
    element = matrix[row][col]
    if element != min(matrix[row]):
        return False
    if element != max(matrix[i][col] for i in range(len(matrix))):
        return False
    return True

def find_saddle_points(matrix, output_type='tuple'):
    """Универсальная функция с выбором формата вывода"""
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
        "matrix_b": find_saddle_points(matrix_b, 'tuple')
    }

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
            return jsonify({
                "error": f"Количество седловых точек не может превышать {rows * cols}"
            }), 400
        
        result = generate_matrix_with_saddle_points(rows, cols, k)
        return jsonify(result)
    except ValueError as ve:
        return jsonify({
            "error": str(ve)
        }), 500
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
    
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