from flask import Blueprint, render_template, session, redirect, url_for
from database import get_db

my_reports_bp = Blueprint('my_reports', __name__)


@my_reports_bp.route('/my_reports')
def my_reports():
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    conn    = get_db()
    reports = conn.execute("""
        SELECT title, detail, image, location, reporter_name, status, created_at, category
        FROM reports
        WHERE user_id=?
        ORDER BY created_at DESC
    """, (session["user_id"],)).fetchall()
    conn.close()

    return render_template("my_reports.html", reports=reports)