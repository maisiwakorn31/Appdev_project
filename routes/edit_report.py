from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db
from routes.helper import is_admin

edit_report_bp = Blueprint('edit_report', __name__)


@edit_report_bp.route('/edit_report/<int:id>', methods=["GET", "POST"])
def edit_report(id):
    if not is_admin():
        return redirect(url_for("home"))

    conn = get_db()

    if request.method == "POST":
        conn.execute(
            "UPDATE reports SET status=? WHERE id=?", (request.form["status"], id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard.dashboard"))

    report = conn.execute(
        "SELECT title, status FROM reports WHERE id=?", (id,)
    ).fetchone()
    conn.close()

    return render_template("edit_report.html", report=report, id=id)
