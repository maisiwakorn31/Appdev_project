from flask import Blueprint, render_template
from database import get_db

search_bp = Blueprint('search', __name__)


@search_bp.route('/search')
def search():
    conn    = get_db()
    reports = conn.execute("""
        SELECT user_id, title, detail, image, status, category,location
        FROM reports
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()

    return render_template("search.html", reports=reports)