from flask import Flask, render_template, session, redirect, url_for,request
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def init_db():
    conn = sqlite3.connect("users.db")
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

    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template("index.html")



@app.route('/login', methods=["GET","POST"])
def login():

    if request.method == "POST":

        phone = request.form["phone"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        cur.execute(
        "SELECT * FROM users WHERE phone=? AND password=?",
        (phone,password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["role"] = user[4]
            return redirect("/")

        return render_template("auth.html", error="เบอร์โทรหรือรหัสผ่านไม่ถูกต้อง")

    return render_template("auth.html")

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            return "รหัสผ่านไม่ตรงกัน"

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        cur.execute(
        "INSERT INTO users (fullname, phone, password) VALUES (?,?,?)",
        (fullname, phone, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("auth.html")

@app.route("/report")
def report():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("report.html")


@app.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for("home")) 


if __name__ == "__main__":
    init_db()
    app.run(debug=True)