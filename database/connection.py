import pymysql
from config.db_config import db_config


def get_connection():
    return pymysql.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        autocommit=False,
        cursorclass=pymysql.cursors.Cursor
    )
