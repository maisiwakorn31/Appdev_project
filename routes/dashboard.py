from flask import Blueprint, render_template, session, redirect, url_for
from database import get_db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    # 1. เช็คก่อนว่าล็อกอินหรือยัง ถ้ายังให้เด้งไปหน้า Login
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    conn = get_db()
    user_id = session["user_id"]
    role = session.get("role")

    # 2. แยกการดึงข้อมูลระหว่าง Admin และ User ธรรมดา
    if role == "admin":
        # ถ้าเป็น admin ให้ดึงข้อมูลและสถิติของ "ทุกคน"
        stats = {
            "total":      conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0],
            "pending":    conn.execute("SELECT COUNT(*) FROM reports WHERE status='รอดำเนินการ'").fetchone()[0],
            "processing": conn.execute("SELECT COUNT(*) FROM reports WHERE status='กำลังดำเนินการ'").fetchone()[0],
            "done":       conn.execute("SELECT COUNT(*) FROM reports WHERE status='แก้ไขแล้ว'").fetchone()[0],
        }
        reports = conn.execute("""
            SELECT r.id, r.user_id, r.title, r.status, r.created_at, u.fullname, r.location
            FROM reports r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.created_at DESC
        """).fetchall()

    else:
        # ถ้าเป็น user ให้ดึงข้อมูลและสถิติ "เฉพาะของตัวเอง" (เช็คจาก user_id)
        stats = {
            "total":      conn.execute("SELECT COUNT(*) FROM reports WHERE user_id=?", (user_id,)).fetchone()[0],
            "pending":    conn.execute("SELECT COUNT(*) FROM reports WHERE status='รอดำเนินการ' AND user_id=?", (user_id,)).fetchone()[0],
            "processing": conn.execute("SELECT COUNT(*) FROM reports WHERE status='กำลังดำเนินการ' AND user_id=?", (user_id,)).fetchone()[0],
            "done":       conn.execute("SELECT COUNT(*) FROM reports WHERE status='แก้ไขแล้ว' AND user_id=?", (user_id,)).fetchone()[0],
        }
        reports = conn.execute("""
            SELECT r.user_id, r.title, r.status, r.created_at, u.fullname,r.location
            FROM reports r
            JOIN users u ON r.user_id = u.id
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC
        """, (user_id,)).fetchall()

    conn.close()

    return render_template("dashboard.html", reports=reports, stats=stats)