from flask import Flask, render_template, session, redirect, url_for,request
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"


UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


@app.route('/')
def home():

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    # ปัญหาทั้งหมด
    cur.execute("SELECT COUNT(*) FROM reports")
    total = cur.fetchone()[0]

    # รอดำเนินการ
    cur.execute("SELECT COUNT(*) FROM reports WHERE status='รอดำเนินการ'")
    pending = cur.fetchone()[0]

    # กำลังดำเนินการ
    cur.execute("SELECT COUNT(*) FROM reports WHERE status='กำลังดำเนินการ'")
    processing = cur.fetchone()[0]

    # แก้ไขแล้ว
    cur.execute("SELECT COUNT(*) FROM reports WHERE status='แก้ไขแล้ว'")
    done = cur.fetchone()[0]

    # ปัญหาล่าสุด
    cur.execute("""
        SELECT id,title,detail,image,status
        FROM reports
        ORDER BY created_at DESC
        LIMIT 3
    """)
    reports = cur.fetchall()

    conn.close()

    return render_template(
        "index.html",
        reports=reports,
        total=total,
        pending=pending,
        processing=processing,
        done=done
    )



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

@app.route("/report", methods=["GET","POST"])
def report():

    if "user_id" not in session:
        return redirect("/login")

    
    if request.method == "POST":

        title = request.form["title"]
        detail = request.form["detail"]
        location = request.form["location"]
        reporter_name = request.form["reporter_name"]
        phone = request.form["phone"]

        image_file = request.files["image"]
        filename = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(image_path)

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO reports (user_id,title,detail,image,location,reporter_name,phone)
        VALUES (?,?,?,?,?,?,?)
        """,(
            session["user_id"],
            title,
            detail,
            filename,
            location,
            reporter_name,
            phone
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT fullname, phone FROM users WHERE id=?",
        (session["user_id"],)
    )

    user = cur.fetchone()
    conn.close()

    return render_template("report.html", user=user)

@app.route("/my_reports")
def my_reports():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT title,detail,image,location,reporter_name,status,created_at
    FROM reports
    WHERE user_id=?
    ORDER BY created_at DESC
    """,(session["user_id"],))

    reports = cur.fetchall()

    conn.close()

    return render_template("my_reports.html", reports=reports)

@app.route("/dashboard")
def dashboard():
    # 1. เช็คว่าล็อกอินหรือยัง
    if "user_id" not in session:
        return redirect("/login")

    # 2. เช็คว่าสิทธิ์เป็น admin หรือไม่ (ถ้าไม่ใช่ เด้งกลับหน้าแรก)
    if session.get("role") != "admin":
        return redirect("/")

    # 3. สำหรับ Admin ควรจะเห็นปัญหาของ "ทุกคน" (ลบเงื่อนไข WHERE user_id=? ออก)
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT id,title,status,created_at
    FROM reports
    ORDER BY created_at DESC
    """)

    reports = cur.fetchall()
    conn.close()

    return render_template("dashboard.html", reports=reports)

@app.route("/delete_report/<int:id>")
def delete_report(id):

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM reports
    WHERE id=? AND user_id=?
    """,(id,session["user_id"]))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/edit_report/<int:id>", methods=["GET","POST"])
def edit_report(id):

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    if request.method == "POST":

        title = request.form["title"]
        detail = request.form["detail"]

        cur.execute("""
        UPDATE reports
        SET title=?, detail=?
        WHERE id=? AND user_id=?
        """,(title,detail,id,session["user_id"]))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    cur.execute("""
    SELECT title,detail
    FROM reports
    WHERE id=? AND user_id=?
    """,(id,session["user_id"]))

    report = cur.fetchone()

    conn.close()

    return render_template("edit_report.html", report=report, id=id)


@app.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for("home")) 


if __name__ == "__main__":
    init_db()
    app.run(debug=True)