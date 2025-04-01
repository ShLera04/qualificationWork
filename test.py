import numpy as np

def generate_matrix_with_saddle_points(rows, cols, saddle_points):
    # Шаг 1: Генерация случайной матрицы
    matrix = np.random.randint(0, 100, size=(rows, cols))

    # Шаг 2: Поиск седловых точек
    def find_saddle_points(matrix):
        saddle_points = []
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if matrix[i, j] == np.min(matrix[i, :]) and matrix[i, j] == np.max(matrix[:, j]):
                    saddle_points.append((i, j))
        return saddle_points

    # Шаг 3: Обеспечение нужного количества седловых точек
    current_saddle_points = find_saddle_points(matrix)
    while len(current_saddle_points) < saddle_points:
        # Случайный выбор позиции для изменения
        i, j = np.random.randint(0, rows), np.random.randint(0, cols)
        # Изменение элемента для создания седловой точки
        matrix[i, :] = np.maximum(matrix[i, :], matrix[i, j])
        matrix[:, j] = np.minimum(matrix[:, j], matrix[i, j])
        current_saddle_points = find_saddle_points(matrix)

    # Шаг 4: Удаление лишних седловых точек, если их больше, чем нужно
    while len(current_saddle_points) > saddle_points:
        # Случайный выбор седловой точки для удаления
        i, j = current_saddle_points[np.random.randint(0, len(current_saddle_points))]
        # Изменение элемента, чтобы удалить седловую точку
        matrix[i, j] = np.random.randint(0, 100)
        current_saddle_points = find_saddle_points(matrix)

    # Шаг 5: Проверка и корректировка, если количество седловых точек изменилось
    if len(current_saddle_points) != saddle_points:
        return generate_matrix_with_saddle_points(rows, cols, saddle_points)

    return matrix, current_saddle_points

# Пример использования
rows, cols, saddle_points = 2, 2, 1
matrix, saddle_points_positions = generate_matrix_with_saddle_points(rows, cols, saddle_points)
print("Матрица:")
print(matrix)
print("Седловые точки:")
print(saddle_points_positions)
