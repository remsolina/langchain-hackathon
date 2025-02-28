# utils/db_connection.py

import pymysql
import os

def get_mysql_connection():
    """
    Returns a MySQL connection using environment variables or local config.
    """
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "fill in your password here"),
        database=os.getenv("MYSQL_DB", "mentee_db"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

def get_mentee_data(mentee_id: int):
    """
    Fetch mentee data from the 'mentees' table by ID.
    Expects columns: background, experience, learning_style, availability, personality, unit_needs
    """
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT background, experience, learning_style, availability,
                       personality, unit_needs
                FROM mentees
                WHERE id = %s
            """
            cursor.execute(sql, (mentee_id,))
            result = cursor.fetchone()
            return result
    finally:
        conn.close()
