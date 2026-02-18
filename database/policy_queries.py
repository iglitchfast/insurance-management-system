from database.connection import get_connection


def get_all_policies():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT policy_id, policy_name, base_premium 
        FROM POLICIES
    """)
    policies = cursor.fetchall()
    cursor.close()
    conn.close()
    return policies


def add_policy(policy_name, base_premium):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO POLICIES (policy_name, base_premium)
    VALUES (%s, %s)
    """
    cursor.execute(query, (policy_name, base_premium))
    conn.commit()
    cursor.close()
    conn.close()

def delete_policy(policy_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM POLICIES WHERE policy_id = %s", (policy_id,))
    conn.commit()
    cursor.close()
    conn.close()


def purchase_policy(user_id, policy_id, start_date):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO USER_POLICIES (user_id, policy_id, start_date)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (user_id, policy_id, start_date))
    conn.commit()
    cursor.close()
    conn.close()


def get_user_policies(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT 
        up.purchase_id,
        p.policy_name,
        p.base_premium,
        up.start_date
    FROM USER_POLICIES up
    JOIN POLICIES p ON up.policy_id = p.policy_id
    WHERE up.user_id = %s
    """
    cursor.execute(query, (user_id,))
    policies = cursor.fetchall()
    cursor.close()
    conn.close()
    return policies