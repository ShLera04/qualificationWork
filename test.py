# import numpy as np
# import random

# def generate_game_matrix(v, x, y, num_saddle_points=0):
#     """
#     Генерирует матрицу 2x2, удовлетворяющую условиям смешанных стратегий.
    
#     Параметры:
#     - v: цена игры
#     - x: вероятность выбора первой строки игроком A (x^* = (x, 1-x))
#     - y: вероятность выбора первого столбца игроком B (y^* = (y, 1-y))
#     - num_saddle_points: количество седловых точек (0, 1 или 2)
    
#     Возвращает:
#     - Матрицу 2x2 в виде списка списков
#     """
#     # Проверка корректности входных данных
#     if not (0 <= x <= 1 and 0 <= y <= 1):
#         raise ValueError("x и y должны быть в диапазоне [0, 1]")
#     if num_saddle_points not in [0, 1, 2]:
#         raise ValueError("Количество седловых точек должно быть 0, 1 или 2")
    
#     # Генерация матрицы с учетом условий
#     while True:
#         # Случайно генерируем элементы матрицы в разумных пределах
#         a11 = random.uniform(v - 2, v + 2)
#         a12 = random.uniform(v - 2, v + 2)
#         a21 = random.uniform(v - 2, v + 2)
#         a22 = random.uniform(v - 2, v + 2)
        
#         matrix = [[a11, a12], [a21, a22]]
        
#         # Проверяем условия для смешанных стратегий
#         cond1 = a11*y + a12*(1-y) <= v  # M(1, y^*) <= v
#         cond2 = a21*y + a22*(1-y) <= v  # M(2, y^*) <= v
#         cond3 = a11*x + a21*(1-x) >= v  # M(x^*, 1) >= v
#         cond4 = a12*x + a22*(1-x) >= v  # M(x^*, 2) >= v
        
#         if not (cond1 and cond2 and cond3 and cond4):
#             continue
        
#         # Проверяем количество седловых точек
#         saddle_points = 0
#         min_row1 = min(a11, a12)
#         min_row2 = min(a21, a22)
#         max_col1 = max(a11, a21)
#         max_col2 = max(a12, a22)
        
#         if a11 == min_row1 and a11 == max_col1:
#             saddle_points += 1
#         if a12 == min_row1 and a12 == max_col2:
#             saddle_points += 1
#         if a21 == min_row2 and a21 == max_col1:
#             saddle_points += 1
#         if a22 == min_row2 and a22 == max_col2:
#             saddle_points += 1
        
#         if saddle_points == num_saddle_points:
#             return matrix

# # Пример использования
# if __name__ == "__main__":
#     print("Генератор матрицы 2x2 для игры в смешанных стратегиях")
    
#     # Ввод данных от пользователя
#     v = float(input("Введите цену игры (v): "))
#     x = float(input("Введите x (вероятность выбора первой строки игроком A, 0 <= x <= 1): "))
#     y = float(input("Введите y (вероятность выбора первого столбца игроком B, 0 <= y <= 1): "))
#     num_saddle = int(input("Введите количество седловых точек (0, 1 или 2): "))
    
#     # Генерация матрицы
#     try:
#         matrix = generate_game_matrix(v, x, y, num_saddle)
#         print("\nСгенерированная матрица:")
#         print(f"[{matrix[0][0]:.2f}, {matrix[0][1]:.2f}]")
#         print(f"[{matrix[1][0]:.2f}, {matrix[1][1]:.2f}]")
#     except ValueError as e:
#         print(f"Ошибка: {e}")
import numpy as np

def input_matrix():
    print("Введите элементы матрицы 2x2:")
    matrix = []
    for i in range(2):
        row = list(map(float, input(f"Строка {i+1} (два числа через пробел): ").split()))
        matrix.append(row)
    return matrix

def find_mixed_strategy_saddle_point(matrix):
    a11, a12, a21, a22 = matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1]
    
    denominator = (a11 + a22 - a12 - a21)
    if denominator != 0:
        x = (a22 - a21) / denominator
    else:
        x = 0.5 
    
    if denominator != 0:
        y = (a22 - a12) / denominator
    else:
        y = 0.5 
    
    x = max(0, min(1, x))
    y = max(0, min(1, y))
    
    v = x * y * a11 + x * (1 - y) * a12 + (1 - x) * y * a21 + (1 - x) * (1 - y) * a22
    
    M1y = y * a11 + (1 - y) * a12  
    M2y = y * a21 + (1 - y) * a22  
    Mx1 = x * a11 + (1 - x) * a21  
    Mx2 = x * a12 + (1 - x) * a22  
    
    is_saddle = (M1y <= v + 1e-10) and (M2y <= v + 1e-10) and (Mx1 >= v - 1e-10) and (Mx2 >= v - 1e-10)
    
    return {
        'matrix': matrix,
        'x_star': (x, 1 - x),
        'y_star': (y, 1 - y),
        'game_value': v,
        'is_saddle': is_saddle,
        'M1y': M1y,
        'M2y': M2y,
        'Mx1': Mx1,
        'Mx2': Mx2,
    }

def print_results(result):
    print("\nРезультаты:")
    print("Матрица игры:")
    for row in result['matrix']:
        print(row)
    print("\nОптимальная стратегия игрока 1 (x^*):", result['x_star'])
    print("Оптимальная стратегия игрока 2 (y^*):", result['y_star'])
    print("Цена игры (v):", result['game_value'])
    print("\nПроверка условий седловой точки в смешанных стратегиях:")
    print(f"M(1, y^*) = {result['M1y']} <= v = {result['game_value']}? {result['M1y'] <= result['game_value'] + 1e-10}")
    print(f"M(2, y^*) = {result['M2y']} <= v = {result['game_value']}? {result['M2y'] <= result['game_value'] + 1e-10}")
    print(f"M(x^*, 1) = {result['Mx1']} >= v = {result['game_value']}? {result['Mx1'] >= result['game_value'] - 1e-10}")
    print(f"M(x^*, 2) = {result['Mx2']} >= v = {result['game_value']}? {result['Mx2'] >= result['game_value'] - 1e-10}")
    print("\nЯвляется ли седловой точкой в смешанных стратегиях?", result['is_saddle'])

def main():
    matrix = input_matrix()
    result = find_mixed_strategy_saddle_point(matrix)
    print_results(result)

if __name__ == "__main__":
    main()


# import numpy as np
# from scipy.optimize import linprog

# def input_matrix():
#     print("Введите размер матрицы (строки столбцы):")
#     m, n = map(int, input().split())
#     print(f"Введите матрицу {m}x{n} (по одной строке за раз):")
#     return np.array([list(map(float, input().split())) for _ in range(m)])

# def solve_player(A, player=1):
#     m, n = A.shape
#     if player == 1:  # Игрок 1 максимизирует минимальный выигрыш
#         c = [0]*m + [-1]  # Цель: max v (минимизируем -v)
#         A_ub = np.hstack((-A.T, np.ones((n,1))))  # Ограничения: A.T*x ≥ v
#     else:  # Игрок 2 минимизирует максимальный проигрыш
#         c = [0]*n + [1]   # Цель: min v
#         A_ub = np.hstack((A, -np.ones((m,1))))   # Ограничения: A*y ≤ v
    
#     b_ub = [0]*(n if player == 1 else m)
#     A_eq = [[1]*m + [0] if player == 1 else [1]*n + [0]]  # Сумма вероятностей = 1
#     b_eq = [1]
#     bounds = [(0,None)]*(m if player == 1 else n) + [(None,None)]  # v может быть любым
    
#     res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
#     return res.x[:-1], res.x[-1]

# def main():
#     A = input_matrix()
#     x, v1 = solve_player(A, player=1)
#     y, v2 = solve_player(A, player=2)
    
#     if not np.isclose(v1, v2):
#         print("Нет решения в смешанных стратегиях!")
#         return
    
#     # Проверка условий седловой точки
#     check1 = all(A @ y <= v1 + 1e-10)  # M(i,y) ≤ v
#     check2 = all(x @ A >= v1 - 1e-10)   # M(x,j) ≥ v
    
#     print("\nРезультаты:")
#     print(f"Стратегия игрока 1 (x): {np.round(x, 4)}")
#     print(f"Стратегия игрока 2 (y): {np.round(y, 4)}")
#     print(f"Цена игры: {v1:.4f}")
#     print(f"Является седловой точкой: {'Да' if check1 and check2 else 'Нет'}")

# if __name__ == "__main__":
#     main()