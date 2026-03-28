import os
from flask import Flask, render_template, session
from database import init_db, get_db
from routes.helper import is_admin

from routes.login         import login_bp
from routes.register      import register_bp
from routes.logout        import logout_bp
from routes.report        import report_bp
from routes.my_reports    import my_reports_bp
from routes.dashboard     import dashboard_bp
from routes.edit_report   import edit_report_bp
from routes.delete_report import delete_report_bp
from routes.search        import search_bp
from routes.user_edit     import user_edit_bp

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(report_bp)
app.register_blueprint(my_reports_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(edit_report_bp)
app.register_blueprint(delete_report_bp)
app.register_blueprint(search_bp)
app.register_blueprint(user_edit_bp)



@app.context_processor
def inject_globals():
    return {
        "is_admin_user": is_admin(),
        "is_logged_in": "user_id" in session,
    }



@app.route('/')
def home():
    conn = get_db()

    total      = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    pending    = conn.execute("SELECT COUNT(*) FROM reports WHERE status='รอดำเนินการ'").fetchone()[0]
    processing = conn.execute("SELECT COUNT(*) FROM reports WHERE status='กำลังดำเนินการ'").fetchone()[0]
    done       = conn.execute("SELECT COUNT(*) FROM reports WHERE status='แก้ไขแล้ว'").fetchone()[0]

    reports = conn.execute("""
        SELECT id, title, detail, image, status, category
        FROM reports
        ORDER BY created_at DESC
        LIMIT 30
    """).fetchall()
    conn.close()

    return render_template(
        "index.html",
        reports=reports,
        total=total,
        pending=pending,
        processing=processing,
        done=done,
    )




if __name__ == "__main__":
    init_db()
    app.run()