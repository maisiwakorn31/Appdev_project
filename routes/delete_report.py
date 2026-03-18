from flask import Blueprint, redirect, url_for
from database import get_db
from routes.helper import is_admin

delete_report_bp = Blueprint('delete_report', __name__)


@delete_report_bp.route('/delete_report/<int:id>')
def delete_report(id):
    if not is_admin():
        return redirect(url_for("home"))

    conn = get_db()
    conn.execute("DELETE FROM reports WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard.dashboard"))
