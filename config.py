"""
Configuration module for Once Upon a Page storybook application.
Loads environment variables from .env file for secure database and secret key management.
"""

import os
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()

class Config:
    """Application configuration parameters."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'once-upon-a-page-fairytale-secret-key-2026')
    
    # MySQL Database Connection Settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    try:
        MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306) or 3306)
    except (ValueError, TypeError):
        MYSQL_PORT = 3306
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'storybook_db')
    MYSQL_CHARSET = 'utf8mb4'
    
    # Session / Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days for "Remember Me"
