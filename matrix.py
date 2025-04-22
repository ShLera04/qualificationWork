def calculate_matrix(x, y, v, a12):
    a21 = (v * (y - x) + a12 * x * (1 - y)) / (y * (1 - x))
    a11 = (v - a12 * (1 - y)) / y
    a22 = (v - a12 * x) / (1 - x)
    return [[a11, a12], [a21, a22]]

# Ввод данных
x = float(input("Введите x: "))
y = float(input("Введите y: "))
v = float(input("Введите v: "))
a12 = float(input("Введите a12: "))

matrix = calculate_matrix(x, y, v, a12)

# Вывод с округлением до 10 знаков после запятой
for row in matrix:
    print(round(row[0], 10), round(row[1], 10))