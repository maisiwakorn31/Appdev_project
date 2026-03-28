import sqlite3
import os

def get_db():
    if os.name == "nt":
        db_path = "users.db"
    else:
        db_path = "/tmp/users.db"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()


    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        detail TEXT,
        image TEXT,
        location TEXT,
        reporter_name TEXT,
        phone TEXT,
        status TEXT DEFAULT 'รอดำเนินการ',
        note TEXT,
        category TEXT DEFAULT 'อื่นๆ',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("SELECT * FROM users WHERE phone='0999999999'")
    if not cur.fetchone():
            cur.execute("""
            INSERT INTO users (fullname, phone, password, role)
            VALUES (?, ?, ?, ?)
            """, ("Admin", "0999999999", "1234", "admin"))

    conn.commit()
    conn.close()
