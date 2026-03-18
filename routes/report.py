import os
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from database import get_db

report_bp = Blueprint('report', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@report_bp.route('/report', methods=["GET", "POST"])
def report():
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    if request.method == "POST":
        title         = request.form["title"]
        detail        = request.form["detail"]
        location      = request.form["location"]
        reporter_name = request.form["reporter_name"]
        phone         = request.form["phone"]
        category      = request.form.get("category", "อื่นๆ")

        image_file = request.files.get("image")
        filename   = None

        if image_file and image_file.filename != "" and allowed_file(image_file.filename):
            filename   = secure_filename(image_file.filename)
            # ใช้ path เต็มจาก root ของ app เพื่อให้บันทึกถูกที่เสมอ
            upload_dir = os.path.join(current_app.root_path, "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            image_file.save(os.path.join(upload_dir, filename))

        conn = get_db()
        conn.execute("""
            INSERT INTO reports (user_id, title, detail, image, location, reporter_name, phone, category)
            VALUES (?,?,?,?,?,?,?,?)
        """, (session["user_id"], title, detail, filename, location, reporter_name, phone, category))
        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    conn = get_db()
    user = conn.execute(
        "SELECT fullname, phone FROM users WHERE id=?", (session["user_id"],)
    ).fetchone()
    conn.close()

    return render_template("report.html", user=user)