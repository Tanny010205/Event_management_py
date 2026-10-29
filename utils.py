import re
import secrets
from functools import wraps
from flask import session, request, abort, redirect, url_for, flash

def generate_csrf_token():
    """Generates a secure random CSRF token and stores it in session."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]

def validate_csrf():
    """
    Validates the submitted CSRF token for state-changing HTTP requests (POST).
    Protects against Cross-Site Request Forgery.
    """
    if request.method == "POST":
        token = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
        session_token = session.get("_csrf_token")
        if not token or not session_token or not secrets.compare_digest(token, session_token):
            flash("Security check failed (invalid or expired CSRF token). Please try again.", "danger")
            abort(400, description="Invalid CSRF token")

def admin_required(f):
    """Decorator to restrict route access exclusively to authenticated administrators."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Administrator login is required to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def sanitize_csv_cell(value):
    """
    Protects against CSV Formula Injection (CWE-1236).
    If a cell value starts with '=', '+', '-', or '@', Excel/Calc may execute it as a formula.
    Prefixing with a single quote (') forces spreadsheet software to treat it as plain text.
    """
    if value is None:
        return ""
    val_str = str(value)
    if val_str and val_str[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + val_str
    return val_str

def is_valid_email(email):
    """Validates email format using regex."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email.strip()) is not None
