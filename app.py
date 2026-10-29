import os
from datetime import datetime
from flask import Flask, render_template, request, session
from config import Config
from database.db import close_db_connection
from utils import generate_csrf_token, validate_csrf
from routes.auth import auth_bp
from routes.events import events_bp
from routes.students import students_bp
from routes.reports import reports_bp

def create_app():
    """Application factory for College Event Management System."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(reports_bp)

    # Teardown request to close MySQL connection
    @app.teardown_appcontext
    def teardown_db(exception):
        close_db_connection(exception)

    # CSRF protection hook
    @app.before_request
    def check_csrf():
        validate_csrf()

    # Context processors to inject global variables and helpers into all Jinja templates
    @app.context_processor
    def inject_helpers():
        return {
            "csrf_token": generate_csrf_token,
            "now": datetime.now(),
            "admin_logged_in": session.get("admin_logged_in", False),
            "admin_username": session.get("admin_username", "")
        }

    # Custom Jinja template filters
    @app.template_filter("format_datetime")
    def format_datetime(value, format="%b %d, %Y at %I:%M %p"):
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                return value
        if isinstance(value, datetime):
            return value.strftime(format)
        return ""

    @app.template_filter("status_badge_class")
    def status_badge_class(status):
        mapping = {
            "Upcoming": "bg-primary",
            "Ongoing": "bg-success",
            "Completed": "bg-secondary",
            "Cancelled": "bg-danger",
            "Registered": "bg-info text-dark"
        }
        return mapping.get(status, "bg-secondary")

    # Friendly HTTP Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("base.html", error_title="404 - Page Not Found", error_message="The requested page could not be found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("base.html", error_title="500 - Server Error", error_message="An internal server error occurred. Please contact the administrator."), 500

    @app.errorhandler(400)
    def bad_request(e):
        msg = getattr(e, "description", "Bad Request")
        return render_template("base.html", error_title="400 - Bad Request", error_message=msg), 400

    return app

app = create_app()

if __name__ == "__main__":
    # Runs the local development server on http://127.0.0.1:5000
    print("=" * 60)
    print("Starting College Event Management System...")
    print("Application URL: http://127.0.0.1:5000")
    print("Admin Login URL: http://127.0.0.1:5000/admin/login")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)
