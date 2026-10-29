import os
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()

class Config:
    """Base application configuration loaded from environment variables."""
    SECRET_KEY = os.getenv("SECRET_KEY", "college-events-dev-secret-key-change-in-prod-12345")
    
    # MySQL Database Configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_NAME = os.getenv("DB_NAME", "college_events_db")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    # Flask settings
    DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
