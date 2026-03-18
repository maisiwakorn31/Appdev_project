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

# ----------------- โซนของ Admin -----------------
@app.route("/dashboard")
def dashboard():
    # เช็กว่าเป็น admin หรือไม่
    if session.get("role") != "admin":
        return redirect("/")
        
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    # --- ดึงข้อมูลสรุปสำหรับการ์ดด้านบน ---
    cur.execute("SELECT COUNT(*) FROM reports")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM reports WHERE status='รอดำเนินการ'")
    pending = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM reports WHERE status='กำลังดำเนินการ'")
    processing = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM reports WHERE status='แก้ไขแล้ว'")
    done = cur.fetchone()[0]

    # --- ดึงข้อมูลรายงานทั้งหมดสำหรับตาราง ---
    cur.execute("""
        SELECT r.id, r.title, r.status, r.created_at, u.fullname
        FROM reports r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.created_at DESC
    """)
    reports = cur.fetchall()
    
    conn.close()

    # --- เตรียมข้อมูลสรุปสำหรับการ์ด ---
    stats = {
        'total': total,
        'pending': pending,
        'processing': processing,
        'done': done
    }

    return render_template("dashboard.html", reports=reports, stats=stats)

@app.route("/delete_report/<int:id>")
@app.route("/delete_report/<int:id>")
def delete_report(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    # ลบแค่ id อย่างเดียว ไม่ต้องเช็ก user_id แล้วเพื่อให้ Admin ลบได้ทุกคน
    cur.execute("DELETE FROM reports WHERE id=?", (id,))

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
        status = request.form["status"] # รับค่าสถานะมาจากฟอร์ม

        # อัปเดตเฉพาะสถานะ
        cur.execute("""
        UPDATE reports
        SET status=?
        WHERE id=?
        """, (status, id))

        conn.commit()
        conn.close()
        return redirect("/dashboard")

    # ดึงข้อมูลมาโชว์ในฟอร์ม
    cur.execute("SELECT title, status FROM reports WHERE id=?", (id,))
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