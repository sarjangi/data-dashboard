# test file with intentional vulnerability for pipeline testing
import sqlite3

def get_user(username):
    conn = sqlite3.connect("app.db")
    # TODO [CWE-89]: Use parameterized queries to prevent injection.
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return conn.execute(query).fetchall()
