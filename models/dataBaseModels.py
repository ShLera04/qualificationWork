import psycopg2
from psycopg2 import sql
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

DB_CONFIG = {
    'dbname': config.get('database', 'dbname'),
    'user': config.get('database', 'user'),
    'password': config.get('database', 'password'),
    'host': config.get('database', 'host')
}

conn = psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host']
    )
conn.autocommit = True
conn.cursor().execute("SET client_encoding TO 'UTF8'")
conn.autocommit = False