from database.connection import get_connection
from utils.hash_utils import hash_password


def verify_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    query = """
    SELECT user_id, username, role
    FROM USERS
    WHERE username = %s AND password = %s AND role = %s
    """

    cursor.execute(query, (username, hashed_password, role))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT user_id, username, role FROM USERS"
    cursor.execute(query)

    users = cursor.fetchall()

    cursor.close()
    conn.close()
    return users


def add_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    query = """
    INSERT INTO USERS (username, password, role)
    VALUES (%s, %s, %s)
    """

    cursor.execute(query, (username, hashed_password, role))
    conn.commit()
    cursor.close()
    conn.close()


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT user_id, username, role FROM USERS WHERE user_id = %s"
    cursor.execute(query, (user_id,))

    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user
