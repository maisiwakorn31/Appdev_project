import sqlite3
import os

def get_db():
    db_path = os.path.join("/tmp", "users.db")  # 🔥 ตรงนี้แหละ
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

    conn.commit()
    conn.close()
