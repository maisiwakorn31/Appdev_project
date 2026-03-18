from flask import Blueprint, render_template, request, session, redirect, url_for
from database import get_db

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone    = request.form["phone"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE phone=? AND password=?", (phone, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["role"]    = user["role"]
            return redirect(url_for("home"))

        return render_template("auth.html", error="เบอร์โทรหรือรหัสผ่านไม่ถูกต้อง")

    return render_template("auth.html")
