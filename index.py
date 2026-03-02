from flask import Flask,request,render_template,redirect, session
import sqlite3


app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("mydatabases.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL,
    Password TEXT NOT NULL,
    Role TEXT DEFAULT 'user'
    );
    """)
    
    conn.commit()
    conn.close()



@app.route('/')
def home():
    return render_template("index.html")

@app.route('/report')
def report():
    if 'user' not in session:
        return redirect('/login')
    return render_template("report.html")

@app.route('/login')
def login():

    return render_template("login.html")



if __name__ == "__main__":
    init_db()
    app.run(debug=True)