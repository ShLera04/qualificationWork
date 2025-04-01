import psycopg2
from psycopg2 import pool
from flask import Flask

app = Flask(__name__)

class DatabaseConnection:
    def __init__(self):
        self.connection_pool = None

    def init_db(self):
        # Создание пула подключений
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # минимальное количество подключений
            20,  # максимальное количество подключений
            user="username",
            password="password",
            host="localhost",
            port="5432",
            database="dbname"
        )

        if self.connection_pool:
            print("Connection pool created successfully")

    def get_connection(self):
        # Получение подключения из пула
        return self.connection_pool.getconn()

    def release_connection(self, connection):
        # Возврат подключения в пул
        self.connection_pool.putconn(connection)

    def close_all_connections(self):
        # Закрытие всех подключений в пуле
        self.connection_pool.closeall()

# Пример использования
if __name__ == '__main__':
    db_connection = DatabaseConnection()
    db_connection.init_db()

    # Пример получения подключения
    conn = db_connection.get_connection()
    if conn:
        print("Successfully connected to the database")
        db_connection.release_connection(conn)

    app.run(debug=True)
