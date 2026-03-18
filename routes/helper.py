from flask import session
from database import get_db


def is_admin():
    if "user_id" not in session:
        return False
    conn = get_db()
    user = conn.execute(
        "SELECT role FROM users WHERE id=?", (session["user_id"],)
    ).fetchone()
    conn.close()
    return user and user["role"] == "admin"
