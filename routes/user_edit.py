import os
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from database import get_db

user_edit_bp = Blueprint('user_edit', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_edit_bp.route('/user_edit/<int:id>', methods=["GET", "POST"])
def user_edit(id):
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    conn = get_db()

    # ตรวจว่าเป็นเรื่องของ user คนนี้จริงๆ ป้องกัน user อื่นแก้
    report = conn.execute(
        "SELECT * FROM reports WHERE id=? AND user_id=?", (id, session["user_id"])
    ).fetchone()

    if not report:
        conn.close()
        return redirect(url_for("my_reports.my_reports"))

    if request.method == "POST":
        title         = request.form["title"]
        detail        = request.form["detail"]
        location      = request.form["location"]
        category      = request.form.get("category", report["category"])

        # จัดการรูปภาพใหม่ (ถ้ามี)
        image_file = request.files.get("image")
        filename   = report["image"]  # ใช้รูปเดิมถ้าไม่ได้อัปโหลดใหม่

        if image_file and image_file.filename != "" and allowed_file(image_file.filename):
            filename   = secure_filename(image_file.filename)
            upload_dir = os.path.join(current_app.root_path, "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            image_file.save(os.path.join(upload_dir, filename))

        # ลบเรื่อง
        if request.form.get("action") == "delete":
            conn.execute("DELETE FROM reports WHERE id=? AND user_id=?", (id, session["user_id"]))
            conn.commit()
            conn.close()
            return redirect(url_for("my_reports.my_reports"))

        conn.execute("""
            UPDATE reports
            SET title=?, detail=?, location=?, category=?, image=?
            WHERE id=? AND user_id=?
        """, (title, detail, location, category, filename, id, session["user_id"]))
        conn.commit()
        conn.close()

        return redirect(url_for("my_reports.my_reports"))

    conn.close()
    return render_template("user_edit.html", report=report, id=id)