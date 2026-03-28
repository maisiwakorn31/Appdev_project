from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db
import sqlite3   # 🔥 ต้องมี

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        phone    = request.form["phone"]
        password = request.form["password"]
        confirm  = request.form["confirm_password"]

        if not phone.isdigit() or len(phone) != 10:
            return render_template("auth.html", error="เบอร์โทรศัพท์ไม่ถูกต้อง")

        if password != confirm:
            return render_template("auth.html", error="รหัสผ่านไม่ตรงกัน")

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (fullname, phone, password) VALUES (?,?,?)",
                (fullname, phone, password)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return render_template("auth.html", error="เบอร์นี้ถูกใช้แล้ว")

        conn.close()

        return redirect(url_for("login.login"))

    return render_template("auth.html")