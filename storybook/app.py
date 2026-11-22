"""
Once Upon a Page - Digital Storybook Web Application
Full Stack Application with Interactive Reader & Complete Administration Dashboard
"""

import os
import re
import json
import shutil
import uuid
import math
from functools import wraps
from datetime import datetime, date, timedelta
import pymysql
import pymysql.cursors
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    g,
    jsonify,
    session
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please sign in to open your magical storybook.'
login_manager.login_message_category = 'info'

# ==============================================================================
# Cloudinary Configuration & Media URL Resolver
# ==============================================================================

try:
    import cloudinary
    import cloudinary.uploader

    cloudinary_url = os.getenv('CLOUDINARY_URL')
    cloudinary_cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    cloudinary_api_key = os.getenv('CLOUDINARY_API_KEY')
    cloudinary_api_secret = os.getenv('CLOUDINARY_API_SECRET')

    if cloudinary_url:
        cloudinary.config()
    elif cloudinary_cloud_name and cloudinary_api_key and cloudinary_api_secret:
        cloudinary.config(
            cloud_name=cloudinary_cloud_name,
            api_key=cloudinary_api_key,
            api_secret=cloudinary_api_secret,
            secure=True
        )
    HAS_CLOUDINARY = True
except Exception:
    HAS_CLOUDINARY = False


def is_cloudinary_configured():
    """Checks whether Cloudinary credentials are validly supplied."""
    if not HAS_CLOUDINARY:
        return False
    if os.getenv('CLOUDINARY_URL'):
        return True
    if os.getenv('CLOUDINARY_CLOUD_NAME') and os.getenv('CLOUDINARY_API_KEY') and os.getenv('CLOUDINARY_API_SECRET'):
        return True
    return False


@app.template_filter('media_url')
def media_url(path):
    """
    Template filter and global helper to resolve media URLs.
    If the path is an external or Cloudinary URL (starts with http:// or https://),
    returns it directly. Otherwise resolves it via url_for('static', filename=path).
    """
    if not path:
        return ''
    path_str = str(path).strip()
    if path_str.startswith('http://') or path_str.startswith('https://') or path_str.startswith('//'):
        return path_str
    return url_for('static', filename=path_str)

app.jinja_env.globals['media_url'] = media_url


# ==============================================================================
# Database Helper Functions
# ==============================================================================

def get_db():
    """
    Open a new database connection if there is none yet for the current application context.
    Uses DictCursor so columns can be accessed by name.
    Supports SSL for remote cloud databases like TiDB.
    """
    if 'db' not in g:
        conn_kwargs = {
            'host': app.config['MYSQL_HOST'],
            'port': app.config['MYSQL_PORT'],
            'user': app.config['MYSQL_USER'],
            'password': app.config['MYSQL_PASSWORD'],
            'database': app.config['MYSQL_DB'],
            'charset': app.config.get('MYSQL_CHARSET', 'utf8mb4'),
            'cursorclass': pymysql.cursors.DictCursor,
            'autocommit': True
        }
        # Enable SSL for cloud MySQL providers like TiDB Cloud
        if app.config['MYSQL_HOST'] not in ['localhost', '127.0.0.1', '']:
            conn_kwargs['ssl'] = {'ssl': {}}
        g.db = pymysql.connect(**conn_kwargs)
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass


def init_db():
    """
    Ensures the storybook_db database and core tables exist on startup.
    Helps ensure a smooth first-time run.
    """
    try:
        temp_kwargs = {
            'host': app.config['MYSQL_HOST'],
            'port': app.config['MYSQL_PORT'],
            'user': app.config['MYSQL_USER'],
            'password': app.config['MYSQL_PASSWORD'],
            'charset': 'utf8mb4'
        }
        if app.config['MYSQL_HOST'] not in ['localhost', '127.0.0.1', '']:
            temp_kwargs['ssl'] = {'ssl': {}}
            temp_kwargs['database'] = app.config['MYSQL_DB']
        try:
            temp_conn = pymysql.connect(**temp_kwargs)
            with temp_conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{app.config['MYSQL_DB']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            temp_conn.commit()
            temp_conn.close()
        except Exception:
            pass

        db = get_db()
        with db.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'user',
                    is_active TINYINT(1) NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    slug VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    slug VARCHAR(100) NOT NULL UNIQUE,
                    title VARCHAR(255) NOT NULL,
                    category_id INT NULL,
                    category VARCHAR(100) NOT NULL DEFAULT 'Bedtime Story',
                    cover VARCHAR(255) NOT NULL,
                    author VARCHAR(150) NOT NULL DEFAULT 'Once Upon a Page',
                    description TEXT,
                    target_age VARCHAR(50) DEFAULT '3-7 years',
                    pages INT NOT NULL DEFAULT 16,
                    duration VARCHAR(50) DEFAULT '5 mins',
                    rating VARCHAR(10) DEFAULT '5.0',
                    is_published TINYINT(1) NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_category (category_id),
                    INDEX idx_published (is_published)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS story_pages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    book_id INT NOT NULL,
                    spread_number INT NOT NULL DEFAULT 1,
                    page_number INT NOT NULL DEFAULT 1,
                    page_side VARCHAR(10) NOT NULL DEFAULT 'left',
                    title VARCHAR(255) NULL,
                    text TEXT NULL,
                    image_url VARCHAR(255) NULL,
                    dialogue TEXT NULL,
                    final_message TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_book_spread (book_id, spread_number),
                    CONSTRAINT fk_story_pages_book FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_favorites (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    book_id INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_user_fav (user_id, book_id),
                    CONSTRAINT fk_user_fav FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reading_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    book_id INT NOT NULL,
                    last_read_page INT NOT NULL DEFAULT 1,
                    total_pages INT NOT NULL DEFAULT 16,
                    last_opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_user_history (user_id, book_id),
                    CONSTRAINT fk_user_history FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS site_settings (
                    setting_key VARCHAR(100) PRIMARY KEY,
                    setting_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INT PRIMARY KEY,
                    theme VARCHAR(20) NOT NULL DEFAULT 'light',
                    night_sky TINYINT(1) NOT NULL DEFAULT 1,
                    page_turn_whispers TINYINT(1) NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    CONSTRAINT fk_user_pref FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
    except Exception as e:
        app.logger.warning(f"Database auto-initialization note: {e}")


# ==============================================================================
# Flask-Login User Model & User Loader
# ==============================================================================

class User(UserMixin):
    """User representation for Flask-Login session management and authorization."""
    def __init__(self, id, full_name, email, password_hash, created_at=None, role='user', is_active=1):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.role = role or 'user'
        self.is_active_account = bool(is_active)

    @property
    def is_active(self):
        """Overrides Flask-Login is_active to respect database deactivation."""
        return self.is_active_account

    @property
    def is_admin(self):
        """Checks if current user has administrator role."""
        return self.role == 'admin'

    @staticmethod
    def get_by_id(user_id):
        """Fetch user by primary key id."""
        try:
            db = get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT id, full_name, email, password_hash, created_at, role, is_active FROM users WHERE id = %s",
                    (user_id,)
                )
                row = cur.fetchone()
                if row:
                    return User(
                        id=row['id'],
                        full_name=row['full_name'],
                        email=row['email'],
                        password_hash=row['password_hash'],
                        created_at=row.get('created_at'),
                        role=row.get('role', 'user'),
                        is_active=row.get('is_active', 1)
                    )
        except Exception as e:
            app.logger.error(f"Error loading user by ID: {e}")
        return None

    @staticmethod
    def get_by_email(email):
        """Fetch user by email address."""
        try:
            db = get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT id, full_name, email, password_hash, created_at, role, is_active FROM users WHERE email = %s",
                    (email,)
                )
                row = cur.fetchone()
                if row:
                    return User(
                        id=row['id'],
                        full_name=row['full_name'],
                        email=row['email'],
                        password_hash=row['password_hash'],
                        created_at=row.get('created_at'),
                        role=row.get('role', 'user'),
                        is_active=row.get('is_active', 1)
                    )
        except Exception as e:
            app.logger.error(f"Error loading user by email: {e}")
        return None


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to reload the user object from user_id stored in session."""
    return User.get_by_id(user_id)


# ==============================================================================
# Authorization Decorator: @admin_required
# ==============================================================================

def admin_required(f):
    """Ensures that the current user is authenticated and has administrative privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please sign in with administrator credentials.', 'warning')
            return redirect(url_for('admin_login', next=request.path))
        if not current_user.is_admin:
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==============================================================================
# Helper Utilities & File Upload Management
# ==============================================================================

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'm4v', 'ogv'}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS

def is_valid_email(email):
    """Validate email address format."""
    return bool(email and EMAIL_REGEX.match(email.strip()))

def allowed_file(filename):
    """Check if uploaded file has an allowed media extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    """Check if uploaded file has an allowed image extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_video_file(filename):
    """Check if uploaded file has an allowed video extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def get_mirror_dir(subfolder=''):
    r"""Returns mirrored upload folder between D:\story_book and D:\story_book\storybook."""
    curr_base = os.path.basename(app.root_path).lower()
    if curr_base == 'storybook':
        parent = os.path.dirname(app.root_path)
        return os.path.join(parent, 'static', 'uploads', subfolder) if subfolder else os.path.join(parent, 'static', 'uploads')
    else:
        child = os.path.join(app.root_path, 'storybook')
        if os.path.isdir(child):
            return os.path.join(child, 'static', 'uploads', subfolder) if subfolder else os.path.join(child, 'static', 'uploads')
    return None


def save_image_upload(file_storage, subfolder):
    """
    Saves an uploaded image file.
    If Cloudinary is configured, uploads directly to Cloudinary and returns secure URL.
    Otherwise saves to local static/uploads/<subfolder> directory.
    Returns relative path (e.g. 'uploads/...') or full Cloudinary URL, or None if no file was uploaded.
    """
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_image_file(file_storage.filename):
        return None

    if is_cloudinary_configured():
        try:
            file_storage.seek(0)
            res = cloudinary.uploader.upload(
                file_storage,
                folder=f"storybook/{subfolder}",
                resource_type="image"
            )
            secure_url = res.get('secure_url')
            if secure_url:
                return secure_url
        except Exception as e:
            app.logger.warning(f"Cloudinary image upload error, falling back to local: {e}")

    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    clean_base = secure_filename(file_storage.filename.rsplit('.', 1)[0])[:30]
    unique_filename = f"{uuid.uuid4().hex[:10]}_{clean_base}.{ext}"

    target_dir = os.path.join(app.root_path, 'static', 'uploads', subfolder)
    os.makedirs(target_dir, exist_ok=True)
    full_path = os.path.join(target_dir, unique_filename)
    file_storage.seek(0)
    file_storage.save(full_path)

    # Mirror to sibling/parent directory if existing
    mirror_dir = get_mirror_dir(subfolder)
    if mirror_dir:
        os.makedirs(mirror_dir, exist_ok=True)
        try:
            shutil.copy2(full_path, os.path.join(mirror_dir, unique_filename))
        except Exception as e:
            app.logger.warning(f"Error mirroring image upload to {mirror_dir}: {e}")

    return f"uploads/{subfolder}/{unique_filename}"


def save_video_upload(file_storage, subfolder):
    """
    Saves an uploaded video file.
    If Cloudinary is configured, uploads directly to Cloudinary and returns secure URL.
    Otherwise saves to local static/uploads/<subfolder> directory.
    Returns relative path (e.g. 'uploads/...') or full Cloudinary URL, or None if no file was uploaded.
    """
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_video_file(file_storage.filename):
        return None

    if is_cloudinary_configured():
        try:
            file_storage.seek(0)
            res = cloudinary.uploader.upload_large(
                file_storage,
                folder=f"storybook/{subfolder}",
                resource_type="video"
            )
            secure_url = res.get('secure_url')
            if secure_url:
                return secure_url
        except Exception as e:
            app.logger.warning(f"Cloudinary video upload error, falling back to local: {e}")

    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    clean_base = secure_filename(file_storage.filename.rsplit('.', 1)[0])[:30]
    unique_filename = f"{uuid.uuid4().hex[:10]}_{clean_base}.{ext}"

    target_dir = os.path.join(app.root_path, 'static', 'uploads', subfolder)
    os.makedirs(target_dir, exist_ok=True)
    full_path = os.path.join(target_dir, unique_filename)
    file_storage.seek(0)
    file_storage.save(full_path)

    # Mirror to sibling/parent directory if existing
    mirror_dir = get_mirror_dir(subfolder)
    if mirror_dir:
        os.makedirs(mirror_dir, exist_ok=True)
        try:
            shutil.copy2(full_path, os.path.join(mirror_dir, unique_filename))
        except Exception as e:
            app.logger.warning(f"Error mirroring video upload to {mirror_dir}: {e}")

    return f"uploads/{subfolder}/{unique_filename}"


DEFAULT_SETTINGS = {
    'site_name': 'Once Upon a Page',
    'welcome_label': 'Cozy Bedtime Stories',
    'welcome_heading': 'Welcome to a World of Little Stories',
    'welcome_subtitle': "Every little story holds a little magic. Come, let's explore!",
    'welcome_button_text': 'Enter the Story World ✨',
    'welcome_bg_type': 'image',
    'welcome_bg_image': 'images/welcome_bg.jpg',
    'welcome_bg_video': '',
    'login_bg_type': 'plain',
    'login_bg_image': '',
    'login_bg_video': '',
    'default_target_age': '3-7 years',
    'default_duration': '5 mins'
}

BACKUP_SETTINGS_FILE = os.path.join(app.root_path, 'static', 'uploads', 'site_settings_backup.json')

def load_disk_settings_backup():
    """Loads backup settings from disk JSON file if available."""
    paths = [BACKUP_SETTINGS_FILE]
    mirror_dir = get_mirror_dir('')
    if mirror_dir:
        paths.append(os.path.join(mirror_dir, 'site_settings_backup.json'))

    for path in paths:
        if path and os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                app.logger.warning(f"Error reading settings backup {path}: {e}")
    return {}

def save_disk_settings_backup(settings_dict):
    """Persists settings dictionary to JSON files on disk across workspace folders."""
    paths = [BACKUP_SETTINGS_FILE]
    mirror_dir = get_mirror_dir('')
    if mirror_dir:
        paths.append(os.path.join(mirror_dir, 'site_settings_backup.json'))

    media_data = {
        k: v for k, v in settings_dict.items()
        if k in ['welcome_bg_type', 'welcome_bg_video', 'welcome_bg_image',
                 'login_bg_type', 'login_bg_video', 'login_bg_image',
                 'welcome_label', 'welcome_heading', 'welcome_subtitle', 'welcome_button_text']
        and v is not None
    }
    for path in paths:
        if path:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(media_data, f, indent=2)
            except Exception as e:
                app.logger.warning(f"Error writing settings backup {path}: {e}")

@app.context_processor
def inject_site_settings():
    """Make site settings universally accessible in all templates."""
    return {'site_settings': get_site_settings()}

def get_site_settings():
    """Fetches key-value configuration from site_settings table with persistent disk fallback."""
    settings = dict(DEFAULT_SETTINGS)
    disk_backup = load_disk_settings_backup()

    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SHOW TABLES LIKE 'site_settings';")
            if cur.fetchone():
                cur.execute("SELECT setting_key, setting_value FROM site_settings")
                for row in cur.fetchall():
                    if row['setting_value'] is not None:
                        settings[row['setting_key']] = row['setting_value']

                # Persistence Protection: If any uploaded media setting is missing or empty in DB,
                # but exists in the persistent disk backup and the media file exists on disk,
                # restore it into MySQL and settings!
                media_keys = ['welcome_bg_video', 'welcome_bg_image', 'login_bg_video', 'login_bg_image', 'welcome_bg_type', 'login_bg_type']
                needs_db_sync = False
                for mk in media_keys:
                    db_val = settings.get(mk)
                    backup_val = disk_backup.get(mk)
                    if (not db_val or (mk == 'welcome_bg_image' and db_val == 'images/welcome_bg.jpg' and backup_val and backup_val != 'images/welcome_bg.jpg')) and backup_val:
                        if mk.endswith('_type'):
                            settings[mk] = backup_val
                            needs_db_sync = True
                            cur.execute("""
                                INSERT INTO site_settings (setting_key, setting_value)
                                VALUES (%s, %s)
                                ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);
                            """, (mk, backup_val))
                        else:
                            is_cloud = str(backup_val).startswith(('http://', 'https://', '//'))
                            f1 = os.path.join(app.root_path, 'static', backup_val)
                            mirror_base = get_mirror_dir('')
                            f2 = os.path.join(os.path.dirname(mirror_base), backup_val) if mirror_base else None
                            if is_cloud or os.path.isfile(f1) or (f2 and os.path.isfile(f2)):
                                settings[mk] = backup_val
                                needs_db_sync = True
                                cur.execute("""
                                    INSERT INTO site_settings (setting_key, setting_value)
                                    VALUES (%s, %s)
                                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);
                                """, (mk, backup_val))
                if needs_db_sync:
                    db.commit()

        # Update disk backup with any non-empty media settings from DB
        media_to_backup = {k: v for k, v in settings.items() if v}
        if disk_backup != media_to_backup:
            disk_backup.update(media_to_backup)
            save_disk_settings_backup(disk_backup)

    except Exception as e:
        app.logger.warning(f"Error fetching site settings: {e}")
        for k, v in disk_backup.items():
            if v:
                settings[k] = v

    return settings


def get_user_preferences(user_id):
    """Fetches user preferences (theme, night_sky, page_turn_whispers) with defaults."""
    prefs = {'theme': 'light', 'night_sky': True, 'page_turn_whispers': True}
    if not user_id:
        return prefs
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SHOW TABLES LIKE 'user_preferences';")
            if cur.fetchone():
                cur.execute(
                    "SELECT theme, night_sky, page_turn_whispers FROM user_preferences WHERE user_id = %s",
                    (user_id,)
                )
                row = cur.fetchone()
                if row:
                    prefs['theme'] = row.get('theme') or 'light'
                    prefs['night_sky'] = bool(row.get('night_sky', 1))
                    prefs['page_turn_whispers'] = bool(row.get('page_turn_whispers', 1))
    except Exception as e:
        app.logger.warning(f"Error loading user preferences: {e}")
    return prefs


def save_user_preferences(user_id, theme=None, night_sky=None, page_turn_whispers=None):
    """Saves user preferences into user_preferences table."""
    if not user_id:
        return False
    current = get_user_preferences(user_id)
    new_theme = theme if theme in ['light', 'dark'] else current['theme']
    new_night_sky = bool(night_sky) if night_sky is not None else current['night_sky']
    new_whispers = bool(page_turn_whispers) if page_turn_whispers is not None else current['page_turn_whispers']
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO user_preferences (user_id, theme, night_sky, page_turn_whispers)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    theme = VALUES(theme),
                    night_sky = VALUES(night_sky),
                    page_turn_whispers = VALUES(page_turn_whispers);
            """, (user_id, new_theme, int(new_night_sky), int(new_whispers)))
        db.commit()
        return True
    except Exception as e:
        app.logger.warning(f"Error saving user preferences: {e}")
        return False


@app.context_processor
def inject_user_preferences():
    """Make user preferences universally available in all templates."""
    if current_user.is_authenticated:
        return {'user_preferences': get_user_preferences(current_user.id)}
    return {
        'user_preferences': {
            'theme': session.get('theme', 'light'),
            'night_sky': True,
            'page_turn_whispers': True
        }
    }


def format_relative_time(dt):
    """Format datetime into friendly reading-history string."""
    if not dt:
        return "Recently"
    now = datetime.now()
    if isinstance(dt, str):
        return dt
    if dt.date() == now.date():
        return f"Today, {dt.strftime('%I:%M %p')}"
    elif dt.date() == (now.date() - timedelta(days=1)):
        return "Yesterday"
    else:
        return dt.strftime('%b %d, %Y')


def format_datetime(dt):
    """Format datetime into standard date string."""
    if not dt:
        return "—"
    if isinstance(dt, str):
        return dt
    return dt.strftime('%b %d, %Y')


# ==============================================================================
# Sample Storybooks Collection & Twinkle Spreads
# ==============================================================================

STORYBOOKS = [
    {
        "id": 1,
        "slug": "twinkle",
        "title": "Twinkle",
        "category": "Bedtime Story",
        "cover": "images/covers/twinkle-cover.png",
        "author": "Once Upon a Page",
        "description": "The heartwarming tale of a tiny star named Twinkle who discovers that you don't have to be the brightest star in the sky to make someone's night beautiful.",
        "pages": 16,
        "duration": "5 mins",
        "rating": "5.0",
        "is_favorite": True,
    },
    {
        "id": 2,
        "slug": "fairy-and-firefly",
        "title": "The Fairy and the Tiny Bug",
        "category": "Magic & Wonder",
        "cover": "images/books/book_fairy.jpg",
        "author": "Rowan Whisper",
        "description": "Follow Pip the lost firefly and Petal the fairy on an illuminated quest through the moonlit Whispering Woods.",
        "pages": 18,
        "duration": "5 mins",
        "rating": "4.9",
        "is_favorite": True,
    }
]

TWINKLE_SPREADS = [
    {
        "spread_number": 1,
        "title": "Meet Twinkle",
        "text": "Once upon a time, there was a tiny star named Twinkle.",
        "illustration": "images/storybook/twinkle/twinkle_scene1.jpg",
        "page_num_left": 1,
        "page_num_right": 2
    },
    {
        "spread_number": 2,
        "title": "The Little Star Who Couldn't Shine",
        "text": "Every night, all the stars would shine brightly. But Twinkle couldn't shine, no matter how hard she tried.",
        "illustration": "images/storybook/twinkle/twinkle_scene2.jpg",
        "page_num_left": 3,
        "page_num_right": 4
    },
    {
        "spread_number": 3,
        "title": "Twinkle's Sadness",
        "text": "'I'm too small. Nobody will ever notice me,' she whispered sadly.",
        "illustration": "images/storybook/twinkle/twinkle_scene3.jpg",
        "page_num_left": 5,
        "page_num_right": 6
    },
    {
        "spread_number": 4,
        "title": "The Little Girl",
        "text": "One night, she looked down and saw a little girl sitting by her bedroom window, crying.",
        "illustration": "images/storybook/twinkle/twinkle_scene4.jpg",
        "page_num_left": 7,
        "page_num_right": 8
    },
    {
        "spread_number": 5,
        "title": "Gathering Courage",
        "text": "Twinkle wanted to help, but she was afraid. Still, she gathered her courage and tried one more time.",
        "illustration": "images/storybook/twinkle/twinkle_scene5.jpg",
        "page_num_left": 9,
        "page_num_right": 10
    },
    {
        "spread_number": 6,
        "title": "A Little Golden Light",
        "text": "A tiny golden light appeared around her. It wasn't very bright, but it reached the little girl's window.",
        "illustration": "images/storybook/twinkle/twinkle_scene6.jpg",
        "page_num_left": 11,
        "page_num_right": 12
    },
    {
        "spread_number": 7,
        "title": "Someone Notices Twinkle",
        "text": "The girl smiled and whispered, 'Look! My little star is here!'",
        "dialogue": 'The Moon smiled and said, "You don\'t have to be the brightest star in the sky to make someone\'s night beautiful."',
        "illustration": "images/storybook/twinkle/twinkle_scene7.jpg",
        "page_num_left": 13,
        "page_num_right": 14
    },
    {
        "spread_number": 8,
        "title": "Twinkle's Happy Ending",
        "text": "From that night onwards, Twinkle never worried about being small again. She shone every night, just for the little girl.",
        "final_message": "Sometimes, the smallest lights make the biggest difference. 💛",
        "illustration": "images/storybook/twinkle/twinkle_scene8.jpg",
        "page_num_left": 15,
        "page_num_right": 16
    }
]


def get_book_spreads(book):
    """
    Returns the spreads for a storybook:
    1. First tries database `story_pages` if available.
    2. If Twinkle, returns TWINKLE_SPREADS.
    3. If other existing storybook, generates richly illustrated spreads based on book theme and cover.
    """
    book_id = book.get('id') if isinstance(book, dict) else getattr(book, 'id', None)
    cover_img = book.get('cover') if isinstance(book, dict) else getattr(book, 'cover', 'images/covers/twinkle-cover.png')
    title = book.get('title') if isinstance(book, dict) else getattr(book, 'title', 'Enchanted Story')
    desc = book.get('description') if isinstance(book, dict) else getattr(book, 'description', '')

    # Check MySQL story_pages table
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SHOW TABLES LIKE 'story_pages';")
            if cur.fetchone():
                cur.execute("""
                    SELECT * FROM story_pages 
                    WHERE book_id = %s 
                    ORDER BY spread_number ASC, page_number ASC
                """, (book_id,))
                pages = cur.fetchall()
                if pages:
                    spreads_dict = {}
                    for p in pages:
                        sp_num = p['spread_number']
                        if sp_num not in spreads_dict:
                            spreads_dict[sp_num] = {
                                "spread_number": sp_num,
                                "title": p.get('title') or f"Chapter {sp_num}",
                                "text": p.get('text') or '',
                                "illustration": p.get('image_url') or cover_img,
                                "page_num_left": (sp_num * 2) - 1,
                                "page_num_right": sp_num * 2,
                                "dialogue": p.get('dialogue') or '',
                                "final_message": p.get('final_message') or ''
                            }
                        else:
                            if p.get('title') and not spreads_dict[sp_num]['title']:
                                spreads_dict[sp_num]['title'] = p['title']
                            if p.get('text'):
                                if spreads_dict[sp_num]['text']:
                                    spreads_dict[sp_num]['text'] += "\n\n" + p['text']
                                else:
                                    spreads_dict[sp_num]['text'] = p['text']
                            if p.get('image_url'):
                                spreads_dict[sp_num]['illustration'] = p['image_url']
                            if p.get('dialogue'):
                                spreads_dict[sp_num]['dialogue'] = p['dialogue']
                            if p.get('final_message'):
                                spreads_dict[sp_num]['final_message'] = p['final_message']
                    return list(spreads_dict.values())
    except Exception as e:
        app.logger.warning(f"Error checking story_pages: {e}")

    slug = (book.get('slug') if isinstance(book, dict) else getattr(book, 'slug', '')) or ''
    if slug == 'twinkle' or book_id == 1:
        return TWINKLE_SPREADS

    # For other books, provide rich default spreads
    return [
        {
            "spread_number": 1,
            "title": f"The Beginning of {title}",
            "text": f"Deep within the enchanted story realm, a wonderful new journey was about to begin. {desc}",
            "illustration": cover_img,
            "page_num_left": 1,
            "page_num_right": 2
        },
        {
            "spread_number": 2,
            "title": "A World of Wonder",
            "text": "Every whisper of the night wind brought gentle secrets from faraway starry lands. Friends gathered beneath the warm, glowing moonlight to share laughter and sweet tales.",
            "illustration": cover_img,
            "page_num_left": 3,
            "page_num_right": 4
        },
        {
            "spread_number": 3,
            "title": "A Gentle Courage",
            "text": "With hearts full of hope and eyes shining with curiosity, they took a brave step forward into the magical forest, guided by fireflies and gentle starlight.",
            "illustration": cover_img,
            "page_num_left": 5,
            "page_num_right": 6
        },
        {
            "spread_number": 4,
            "title": "Sweet Bedtime Dreams",
            "text": "As twilight settled over the sleepy hills, all was calm and peaceful. The stars sang a soft lullaby for dreamers everywhere.",
            "final_message": "May your dreams be filled with magic and wonder. 💛",
            "illustration": cover_img,
            "page_num_left": 7,
            "page_num_right": 8
        }
    ]


# ==============================================================================
# Public Routes: Authentication & Core Experience
# ==============================================================================

@app.route('/')
def index():
    """Root route: Redirect to welcome if authenticated, otherwise to login."""
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login:
    - GET: Render login page.
    - POST: Validate credentials, verify hashed password, verify active status, and initiate session.
    """
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please enter both your email address and password.', 'danger')
            return render_template('login.html', email=email)

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'warning')
            return render_template('login.html', email=email)

        try:
            user = User.get_by_email(email)

            if not user or not check_password_hash(user.password_hash, password):
                flash('Invalid email or password. Please check your credentials and try again.', 'danger')
                return render_template('login.html', email=email)

            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return render_template('login.html', email=email)

            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name}! ✨ The story continues...', 'success')

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('welcome'))

        except pymysql.MySQLError as err:
            app.logger.error(f"Database error during login: {err}")
            flash('Database connection error. Please ensure MySQL is running.', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle new user registration:
    - GET: Render registration page.
    - POST: Validate form inputs, check existing email, hash password, and store user.
    """
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name or not email or not password or not confirm_password:
            flash('All fields are required to begin your story.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

        if len(full_name) < 2:
            flash('Full name must be at least 2 characters long.', 'warning')
            return render_template('register.html', full_name=full_name, email=email)

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'warning')
            return render_template('register.html', full_name=full_name, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('register.html', full_name=full_name, email=email)

        if password != confirm_password:
            flash('Passwords do not match. Please retype carefully.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

        try:
            existing_user = User.get_by_email(email)
            if existing_user:
                flash('An account with this email address already exists. Please log in instead.', 'warning')
                return render_template('register.html', full_name=full_name, email=email)

            password_hash = generate_password_hash(password, method='pbkdf2:sha256')

            db = get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (full_name, email, password_hash, role, is_active) VALUES (%s, %s, %s, 'user', 1)",
                    (full_name, email, password_hash)
                )

            flash('Your account has been created successfully! Please sign in to enter.', 'success')
            return redirect(url_for('login'))

        except pymysql.MySQLError as err:
            app.logger.error(f"Database error during registration: {err}")
            flash('Database error occurred. Please ensure MySQL is running.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

    return render_template('register.html')


@app.route('/welcome')
@login_required
def welcome():
    """
    Page 1: Welcome / Landing Page.
    Magical, cozy bedtime-story atmosphere inspired by the little girl under the blanket.
    Dynamically renders welcome_settings from MySQL site_settings.
    """
    welcome_settings = get_site_settings()
    return render_template('welcome.html', welcome_settings=welcome_settings)


@app.route('/dashboard')
@login_required
def dashboard():
    """
    Page 2: Interactive Storybook Dashboard.
    Supports:
    - Library view: shows published books from MySQL.
    - Favorites view: shows user's favorites from MySQL user_favorites.
    - Reading History view: shows books opened by the user with last-read-page progress.
    """
    current_view = request.args.get('view', 'library')
    category_filter = request.args.get('category', 'all')
    if category_filter == 'favorites':
        current_view = 'favorites'

    db = get_db()

    # 1. Fetch categories
    categories = []
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id, name, slug FROM categories ORDER BY id ASC")
            categories = cur.fetchall()
    except Exception as e:
        app.logger.warning(f"Error fetching categories: {e}")

    # 2. Fetch current user's favorites from MySQL
    user_fav_ids = set()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT book_id FROM user_favorites WHERE user_id = %s", (current_user.id,))
            rows = cur.fetchall()
            user_fav_ids = {r['book_id'] for r in rows}
    except Exception as e:
        app.logger.error(f"Error fetching favorites: {e}")

    # 3. Fetch published books from MySQL books table
    books_list = []
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT b.id, b.slug, b.title, b.category_id, b.category, b.cover, 
                       b.author, b.description, b.target_age, b.pages, b.duration, 
                       b.rating, b.is_published, b.created_at
                FROM books b
                WHERE b.is_published = 1
                ORDER BY b.id ASC
            """)
            db_books = cur.fetchall()
            if db_books:
                for b in db_books:
                    b_dict = dict(b)
                    b_dict['is_favorite'] = (b['id'] in user_fav_ids)
                    books_list.append(b_dict)
    except Exception as e:
        app.logger.warning(f"Error fetching books from DB: {e}")

    # No dummy books auto-injected; books are strictly loaded from MySQL books table

    # 4. Fetch reading history for progress indicators & history view
    reading_history_items = []
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT book_id, last_read_page, total_pages, last_opened_at 
                FROM reading_history 
                WHERE user_id = %s 
                ORDER BY last_opened_at DESC
            """, (current_user.id,))
            history_rows = cur.fetchall()

            for h in history_rows:
                book_meta = next((b for b in books_list if b['id'] == h['book_id']), None)
                if not book_meta:
                    book_meta = next((b for b in STORYBOOKS if b['id'] == h['book_id']), None)
                if book_meta:
                    last_page = h['last_read_page'] or 1
                    total_p = h['total_pages'] or book_meta.get('pages', 16)
                    percent = min(100, int((last_page / total_p) * 100))
                    reading_history_items.append({
                        'book': book_meta,
                        'last_read_page': last_page,
                        'total_pages': total_p,
                        'percent': percent,
                        'last_opened_formatted': format_relative_time(h['last_opened_at'])
                    })
    except Exception as e:
        app.logger.error(f"Error fetching reading history: {e}")

    # Filter books by view and category
    if current_view == 'favorites':
        displayed_books = [b for b in books_list if b['id'] in user_fav_ids]
    elif category_filter != 'all':
        displayed_books = [
            b for b in books_list 
            if (b.get('category', '').lower() == category_filter.lower() or 
                b.get('slug', '').lower() == category_filter.lower())
        ]
    else:
        displayed_books = books_list

    return render_template(
        'dashboard.html',
        books=displayed_books,
        all_books=books_list,
        categories=categories,
        current_view=current_view,
        current_filter=category_filter,
        reading_history_items=reading_history_items,
        total_favorites=len(user_fav_ids),
        total_books=len(books_list)
    )


@app.route('/reader/<book_identifier>')
@login_required
def reader(book_identifier):
    """
    Reader route for storybooks:
    Loads ANY book by id or slug.
    Retrieves or initializes user's reading history in MySQL, and renders the interactive
    closed-to-open reader with StPageFlip.js.
    """
    ident = str(book_identifier).strip().lower()

    # 1. Look up book from database or fallback to STORYBOOKS
    book = None
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SHOW TABLES LIKE 'books';")
            if cur.fetchone():
                if ident.isdigit():
                    cur.execute("SELECT * FROM books WHERE id = %s", (int(ident),))
                else:
                    cur.execute("SELECT * FROM books WHERE slug = %s", (ident,))
                row = cur.fetchone()
                if row:
                    book = dict(row)
    except Exception as e:
        app.logger.warning(f"Error checking books table: {e}")

    if not book:
        if ident in ['1', 'twinkle']:
            book = dict(STORYBOOKS[0])
        else:
            try:
                b_id = int(ident)
                book = next((dict(b) for b in STORYBOOKS if b['id'] == b_id), None)
            except ValueError:
                book = next((dict(b) for b in STORYBOOKS if b.get('slug') == ident), None)

    if not book:
        flash('The selected storybook is being bound by our scribes. Please choose another!', 'warning')
        return redirect(url_for('dashboard'))

    # If book is a draft and user is not an admin, deny access
    if not book.get('is_published', 1) and not getattr(current_user, 'is_admin', False):
        flash('This storybook is currently undergoing draft binding.', 'info')
        return redirect(url_for('dashboard'))

    # 2. Retrieve or initialize reading progress in MySQL
    last_read_page = 1
    total_pages = book.get('pages', 16)
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT last_read_page, total_pages FROM reading_history WHERE user_id = %s AND book_id = %s",
                (current_user.id, book['id'])
            )
            row = cur.fetchone()
            if row and row['last_read_page']:
                last_read_page = row['last_read_page']
                cur.execute(
                    "UPDATE reading_history SET last_opened_at = NOW() WHERE user_id = %s AND book_id = %s",
                    (current_user.id, book['id'])
                )
            else:
                cur.execute(
                    "INSERT INTO reading_history (user_id, book_id, last_read_page, total_pages) VALUES (%s, %s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE last_opened_at = NOW()",
                    (current_user.id, book['id'], 1, total_pages)
                )
    except Exception as e:
        app.logger.error(f"Error checking reading history for book {book['id']}: {e}")

    spreads = get_book_spreads(book)
    template_to_render = 'twinkle_reader.html' if ident in ['1', 'twinkle'] else 'reader.html'
    return render_template(
        template_to_render,
        book=book,
        spreads=spreads,
        last_read_page=last_read_page,
        is_preview=False
    )


# ==============================================================================
# AJAX API Endpoints: Favorites & Reading History
# ==============================================================================

@app.route('/api/favorites/toggle', methods=['POST'])
@login_required
def toggle_favorite():
    """Toggle favorite status for current logged-in user on a specific book."""
    data = request.get_json(silent=True) or request.form
    try:
        book_id = int(data.get('book_id'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid book ID.'}), 400

    # Verify book exists in database or STORYBOOKS
    db = get_db()
    book_exists = False
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM books WHERE id = %s", (book_id,))
            if cur.fetchone():
                book_exists = True
    except Exception:
        pass

    if not book_exists:
        book_exists = any(b['id'] == book_id for b in STORYBOOKS)

    if not book_exists:
        return jsonify({'success': False, 'message': 'Book not found.'}), 404

    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id FROM user_favorites WHERE user_id = %s AND book_id = %s",
                (current_user.id, book_id)
            )
            fav = cur.fetchone()
            if fav:
                cur.execute(
                    "DELETE FROM user_favorites WHERE user_id = %s AND book_id = %s",
                    (current_user.id, book_id)
                )
                is_fav = False
                msg = "Removed from favorites."
            else:
                cur.execute(
                    "INSERT INTO user_favorites (user_id, book_id) VALUES (%s, %s)",
                    (current_user.id, book_id)
                )
                is_fav = True
                msg = "Added to favorites! 💜"

        return jsonify({'success': True, 'is_favorite': is_fav, 'message': msg, 'book_id': book_id})
    except Exception as e:
        app.logger.error(f"Error toggling favorite: {e}")
        return jsonify({'success': False, 'message': 'Database error occurred.'}), 500


@app.route('/api/reading-history/save', methods=['POST'])
@login_required
def save_reading_history():
    """Save user's current reading page progress in MySQL."""
    data = request.get_json(silent=True) or request.form
    if data.get('is_preview'):
        return jsonify({'success': True, 'preview': True})

    try:
        book_id = int(data.get('book_id'))
        page_number = int(data.get('page_number', 1))
        total_pages = int(data.get('total_pages', 16))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid input parameters.'}), 400

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO reading_history (user_id, book_id, last_read_page, total_pages, last_opened_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE 
                    last_read_page = VALUES(last_read_page),
                    total_pages = VALUES(total_pages),
                    last_opened_at = NOW()
            """, (current_user.id, book_id, page_number, total_pages))
        return jsonify({'success': True, 'saved_page': page_number, 'book_id': book_id})
    except Exception as e:
        app.logger.error(f"Error saving reading history: {e}")
        return jsonify({'success': False, 'message': 'Database error occurred.'}), 500


@app.route('/api/reading-history/<int:book_id>', methods=['GET'])
@login_required
def get_reading_history(book_id):
    """Retrieve saved reading page for current user and book."""
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT last_read_page, total_pages, last_opened_at FROM reading_history WHERE user_id = %s AND book_id = %s",
                (current_user.id, book_id)
            )
            row = cur.fetchone()
            if row:
                return jsonify({
                    'success': True,
                    'book_id': book_id,
                    'last_read_page': row['last_read_page'],
                    'total_pages': row['total_pages']
                })
        return jsonify({'success': True, 'book_id': book_id, 'last_read_page': 1, 'total_pages': 16})
    except Exception as e:
        app.logger.error(f"Error fetching reading progress: {e}")
        return jsonify({'success': False, 'message': 'Database error.'}), 500


@app.route('/api/user/preferences', methods=['GET', 'POST'])
def api_user_preferences():
    """
    Get or save user preferences (theme: light/dark, night_sky atmosphere, page_turn_whispers).
    Available to authenticated readers (saved to MySQL) and guests (saved in session).
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        theme = data.get('theme')
        night_sky = data.get('night_sky')
        page_turn_whispers = data.get('page_turn_whispers')

        if theme in ['light', 'dark']:
            session['theme'] = theme

        if current_user.is_authenticated:
            save_user_preferences(
                current_user.id,
                theme=theme,
                night_sky=night_sky,
                page_turn_whispers=page_turn_whispers
            )
            prefs = get_user_preferences(current_user.id)
        else:
            current_theme = session.get('theme', 'light')
            prefs = {
                'theme': theme if theme in ['light', 'dark'] else current_theme,
                'night_sky': bool(night_sky) if night_sky is not None else True,
                'page_turn_whispers': bool(page_turn_whispers) if page_turn_whispers is not None else True
            }
        return jsonify({'success': True, 'preferences': prefs})

    if current_user.is_authenticated:
        prefs = get_user_preferences(current_user.id)
    else:
        prefs = {
            'theme': session.get('theme', 'light'),
            'night_sky': True,
            'page_turn_whispers': True
        }
    return jsonify({'success': True, 'preferences': prefs})


@app.route('/logout')
@login_required
def logout():
    """Log out the current user and redirect to login page with a flash message."""
    logout_user()
    flash('You have closed the storybook. See you next time! 🌙', 'info')
    return redirect(url_for('login'))


# ==============================================================================
# ADMIN PORTAL: Authentication & Management
# ==============================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    Dedicated Administrator Login Portal:
    - URL: /admin/login
    - Checks credentials and verifies user.role == 'admin'.
    """
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter your administrator email and password.', 'danger')
            return render_template('admin/login.html', email=email)

        user = User.get_by_email(email)

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid administrator credentials.', 'danger')
            return render_template('admin/login.html', email=email)

        if not user.is_admin:
            flash('Access restricted. This account does not possess administrator privileges.', 'danger')
            return render_template('admin/login.html', email=email)

        if not user.is_active:
            flash('This administrator account has been deactivated.', 'danger')
            return render_template('admin/login.html', email=email)

        login_user(user, remember=True)
        flash(f'Welcome back, Administrator {user.full_name}!', 'success')

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/admin'):
            return redirect(next_page)
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/login.html')


@app.route('/admin/logout')
@login_required
def admin_logout():
    """Sign out of the administrator portal and redirect to /admin/login."""
    logout_user()
    flash('Signed out of the administration portal.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """
    Admin Overview Dashboard:
    Real database statistics, Chart.js dataset generation, popular story spotlight,
    recent readers and chronologically recent books.
    """
    db = get_db()
    stats = {
        'total_users': 0,
        'total_published': 0,
        'total_drafts': 0,
        'total_sessions': 0,
        'most_popular_book': None
    }

    try:
        with db.cursor() as cur:
            # User count (exclude admin or all users)
            cur.execute("SELECT COUNT(*) AS c FROM users;")
            stats['total_users'] = cur.fetchone()['c']

            # Published & Draft book counts
            cur.execute("SELECT COUNT(*) AS c FROM books WHERE is_published = 1;")
            stats['total_published'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(*) AS c FROM books WHERE is_published = 0;")
            stats['total_drafts'] = cur.fetchone()['c']

            # Reading sessions
            cur.execute("SELECT COUNT(*) AS c FROM reading_history;")
            stats['total_sessions'] = cur.fetchone()['c']

            # Most popular book
            cur.execute("""
                SELECT b.id, b.title, b.cover, b.category,
                       COUNT(DISTINCT rh.user_id) AS reader_count,
                       (SELECT COUNT(*) FROM user_favorites uf WHERE uf.book_id = b.id) AS fav_count
                FROM books b
                LEFT JOIN reading_history rh ON b.id = rh.book_id
                GROUP BY b.id, b.title, b.cover, b.category
                ORDER BY reader_count DESC, fav_count DESC
                LIMIT 1;
            """)
            pop_row = cur.fetchone()
            if pop_row and (pop_row['reader_count'] > 0 or pop_row['fav_count'] > 0):
                stats['most_popular_book'] = pop_row
            else:
                # Default spotlight on Twinkle if no reading history yet
                cur.execute("SELECT id, title, cover, category FROM books WHERE id = 1 LIMIT 1;")
                twk = cur.fetchone()
                if twk:
                    twk['reader_count'] = 0
                    twk['fav_count'] = 0
                    stats['most_popular_book'] = twk

            # Reading sessions timeline (last 7 days)
            cur.execute("""
                SELECT DATE_FORMAT(last_opened_at, '%b %d') AS dt, COUNT(*) AS cnt
                FROM reading_history
                GROUP BY DATE(last_opened_at), DATE_FORMAT(last_opened_at, '%b %d')
                ORDER BY DATE(last_opened_at) ASC
                LIMIT 10;
            """)
            session_rows = cur.fetchall()

            # Category distribution
            cur.execute("""
                SELECT c.name, COUNT(b.id) AS cnt
                FROM categories c
                LEFT JOIN books b ON c.id = b.category_id
                GROUP BY c.id
                ORDER BY cnt DESC;
            """)
            category_rows = cur.fetchall()

            # Recent users (last 5)
            cur.execute("""
                SELECT id, full_name, email, role, is_active, created_at 
                FROM users 
                ORDER BY id DESC 
                LIMIT 5;
            """)
            recent_users = cur.fetchall()
            for u in recent_users:
                u['created_at_formatted'] = format_datetime(u.get('created_at'))

            # Recent books (last 5)
            cur.execute("""
                SELECT id, title, author, category, cover, is_published, created_at 
                FROM books 
                ORDER BY id DESC 
                LIMIT 5;
            """)
            recent_books = cur.fetchall()
            for b in recent_books:
                b['created_at_formatted'] = format_datetime(b.get('created_at'))

    except Exception as e:
        app.logger.error(f"Error fetching dashboard data: {e}")
        session_rows = []
        category_rows = []
        recent_users = []
        recent_books = []

    # Chart datasets
    if session_rows:
        chart_session_labels = [r['dt'] for r in session_rows]
        chart_session_counts = [r['cnt'] for r in session_rows]
    else:
        # Provide welcoming placeholder curve if no sessions logged yet
        chart_session_labels = [(datetime.now() - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
        chart_session_counts = [1, 2, 3, 2, 4, 3, max(1, stats['total_sessions'])]

    if category_rows:
        chart_category_labels = [r['name'] for r in category_rows if r['cnt'] > 0] or [r['name'] for r in category_rows[:5]]
        chart_category_counts = [r['cnt'] for r in category_rows if r['cnt'] > 0] or [1 for _ in chart_category_labels]
    else:
        chart_category_labels = ['Bedtime Story', 'Magic & Wonder', 'Dream Tale', 'Nature Fantasy', 'Night Sky']
        chart_category_counts = [2, 2, 2, 2, 2]

    return render_template(
        'admin/dashboard.html',
        active_page='dashboard',
        stats=stats,
        chart_session_labels=chart_session_labels,
        chart_session_counts=chart_session_counts,
        chart_category_labels=chart_category_labels,
        chart_category_counts=chart_category_counts,
        recent_users=recent_users,
        recent_books=recent_books
    )


# ==============================================================================
# ADMIN: Reader / User Management
# ==============================================================================

@app.route('/admin/users')
@admin_required
def admin_users():
    """User Management: Paginated search & list with status indicators and quick actions."""
    db = get_db()
    search_q = request.args.get('q', '').strip()

    try:
        with db.cursor() as cur:
            if search_q:
                q_wild = f"%{search_q}%"
                cur.execute("""
                    SELECT u.id, u.full_name, u.email, u.role, u.is_active, u.created_at,
                           (SELECT COUNT(*) FROM user_favorites uf WHERE uf.user_id = u.id) AS fav_count,
                           (SELECT COUNT(*) FROM reading_history rh WHERE rh.user_id = u.id) AS history_count
                    FROM users u
                    WHERE u.full_name LIKE %s OR u.email LIKE %s
                    ORDER BY u.id DESC;
                """, (q_wild, q_wild))
            else:
                cur.execute("""
                    SELECT u.id, u.full_name, u.email, u.role, u.is_active, u.created_at,
                           (SELECT COUNT(*) FROM user_favorites uf WHERE uf.user_id = u.id) AS fav_count,
                           (SELECT COUNT(*) FROM reading_history rh WHERE rh.user_id = u.id) AS history_count
                    FROM users u
                    ORDER BY u.id DESC;
                """)
            users = cur.fetchall()
            for u in users:
                u['created_at_formatted'] = format_datetime(u.get('created_at'))

    except Exception as e:
        app.logger.error(f"Error loading users: {e}")
        users = []

    page = request.args.get('page', 1, type=int)
    per_page = 15
    total_users = len(users)
    total_pages = max(1, math.ceil(total_users / per_page))
    current_page = max(1, min(page, total_pages))
    paged_users = users[(current_page - 1) * per_page : current_page * per_page]

    return render_template(
        'admin/users.html',
        active_page='users',
        users=paged_users,
        total_users=total_users,
        total_pages=total_pages,
        current_page=current_page,
        search_query=search_q
    )


@app.route('/admin/users/<int:user_id>')
@admin_required
def admin_user_detail(user_id):
    """Detailed profile view for a specific reader, with reading history and saved favorites."""
    db = get_db()
    user_row = None
    history = []
    favorites = []

    try:
        with db.cursor() as cur:
            cur.execute("SELECT id, full_name, email, role, is_active, created_at FROM users WHERE id = %s;", (user_id,))
            user_row = cur.fetchone()
            if not user_row:
                flash('Reader account not found.', 'danger')
                return redirect(url_for('admin_users'))

            user_row['created_at_formatted'] = format_datetime(user_row.get('created_at'))

            # Reading history
            cur.execute("""
                SELECT rh.last_read_page, rh.total_pages, rh.last_opened_at,
                       b.id AS book_id, b.title AS book_title, b.cover AS book_cover
                FROM reading_history rh
                JOIN books b ON rh.book_id = b.id
                WHERE rh.user_id = %s
                ORDER BY rh.last_opened_at DESC;
            """, (user_id,))
            h_rows = cur.fetchall()
            for h in h_rows:
                pct = int((h['last_read_page'] / max(1, h['total_pages'])) * 100)
                history.append({
                    'book_title': h['book_title'],
                    'book_cover': h['book_cover'],
                    'last_read_page': h['last_read_page'],
                    'total_pages': h['total_pages'],
                    'percent': min(100, pct),
                    'last_opened_formatted': format_relative_time(h['last_opened_at'])
                })

            # Favorites
            cur.execute("""
                SELECT b.id AS book_id, b.title AS book_title, b.cover AS book_cover, b.category
                FROM user_favorites uf
                JOIN books b ON uf.book_id = b.id
                WHERE uf.user_id = %s
                ORDER BY uf.created_at DESC;
            """, (user_id,))
            favorites = cur.fetchall()

    except Exception as e:
        app.logger.error(f"Error fetching user details: {e}")

    return render_template(
        'admin/user_detail.html',
        active_page='users',
        user=user_row,
        history=history,
        favorites=favorites
    )


@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def admin_user_toggle_status(user_id):
    """Toggle user active / inactive status."""
    if user_id == current_user.id:
        flash('You cannot deactivate your own active administrator account.', 'danger')
        return redirect(url_for('admin_users'))

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT full_name, is_active FROM users WHERE id = %s;", (user_id,))
            target = cur.fetchone()
            if target:
                new_state = 0 if target['is_active'] else 1
                cur.execute("UPDATE users SET is_active = %s WHERE id = %s;", (new_state, user_id))
                action_text = "activated" if new_state else "deactivated"
                flash(f"Account for {target['full_name']} has been {action_text}.", 'success')
    except Exception as e:
        app.logger.error(f"Error toggling user status: {e}")
        flash('Failed to update user status.', 'danger')

    return redirect(request.referrer or url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_user_delete(user_id):
    """Delete a user account and cascade delete bookmarks/history."""
    if user_id == current_user.id:
        flash('You cannot delete your own logged-in administrator account.', 'danger')
        return redirect(url_for('admin_users'))

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT full_name FROM users WHERE id = %s;", (user_id,))
            target = cur.fetchone()
            if target:
                cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))
                flash(f"User account for '{target['full_name']}' was permanently removed.", 'success')
    except Exception as e:
        app.logger.error(f"Error deleting user: {e}")
        flash('Failed to delete user account.', 'danger')

    return redirect(url_for('admin_users'))


# ==============================================================================
# ADMIN: Book Management & Storybook Builder
# ==============================================================================

@app.route('/admin/books')
@admin_required
def admin_books():
    """Chronicle of all storybooks: cover thumbnails, status, page count, and actions."""
    db = get_db()
    books = []
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT b.id, b.slug, b.title, b.author, b.category, b.cover, 
                       b.pages, b.duration, b.rating, b.is_published, b.created_at
                FROM books b
                ORDER BY b.id ASC;
            """)
            books = cur.fetchall()
            for b in books:
                b['created_at_formatted'] = format_datetime(b.get('created_at'))
    except Exception as e:
        app.logger.error(f"Error listing books: {e}")

    return render_template(
        'admin/books.html',
        active_page='books',
        books=books
    )


@app.route('/admin/books/new', methods=['GET', 'POST'])
@admin_required
def admin_book_new():
    """
    Storybook Builder: Create a new digital storybook.
    Uploads cover art, configures metadata, and builds dynamic illustrated spreads.
    """
    db = get_db()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('A book title is required.', 'danger')
            return redirect(url_for('admin_book_new'))

        category_id = request.form.get('category_id')
        category_name = 'Bedtime Story'
        try:
            with db.cursor() as cur:
                cur.execute("SELECT name FROM categories WHERE id = %s;", (category_id,))
                cat_row = cur.fetchone()
                if cat_row:
                    category_name = cat_row['name']
        except Exception:
            pass

        author = request.form.get('author', 'Once Upon a Page').strip() or 'Once Upon a Page'
        target_age = request.form.get('target_age', '3-7 years').strip()
        duration = request.form.get('duration', '5 mins').strip()
        description = request.form.get('description', '').strip()
        action_save = request.form.get('action_save', 'publish')
        is_published = 1 if action_save == 'publish' else 0

        # Cover image upload
        cover_file = request.files.get('cover_image')
        cover_path = save_image_upload(cover_file, 'covers')
        if not cover_path:
            cover_path = 'images/covers/twinkle-cover.png'

        # Generate unique slug
        base_slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-') or 'story'
        slug = base_slug
        counter = 1
        with db.cursor() as cur:
            while True:
                cur.execute("SELECT id FROM books WHERE slug = %s;", (slug,))
                if not cur.fetchone():
                    break
                counter += 1
                slug = f"{base_slug}-{counter}"

        try:
            with db.cursor() as cur:
                # 1. Insert book record
                cur.execute("""
                    INSERT INTO books (slug, title, category_id, category, cover, author, description, target_age, pages, duration, rating, is_published)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '5.0', %s);
                """, (slug, title, category_id, category_name, cover_path, author, description, target_age, 2, duration, is_published))
                new_book_id = cur.lastrowid

                # 2. Parse & insert story spreads
                spread_indices = []
                for k in request.form.keys():
                    m = re.match(r'^spread_text_(\d+)$', k)
                    if m:
                        spread_indices.append(int(m.group(1)))
                spread_indices = sorted(list(set(spread_indices)))
                if not spread_indices:
                    spread_indices = [1]

                for order, idx in enumerate(spread_indices, start=1):
                    sp_title = request.form.get(f'spread_title_{idx}', '').strip() or f'Chapter {order}'
                    sp_text = request.form.get(f'spread_text_{idx}', '').strip()
                    sp_dialogue = request.form.get(f'spread_dialogue_{idx}', '').strip()

                    ill_file = request.files.get(f'spread_illustration_{idx}')
                    sp_ill = save_image_upload(ill_file, 'story_pages')
                    if not sp_ill:
                        sp_ill = request.form.get(f'existing_illustration_{idx}', '').strip()
                    if not sp_ill:
                        sp_ill = cover_path

                    # Insert left page (illustration & chapter heading)
                    cur.execute("""
                        INSERT INTO story_pages (book_id, spread_number, page_number, page_side, title, text, image_url, dialogue)
                        VALUES (%s, %s, %s, 'left', %s, NULL, %s, NULL);
                    """, (new_book_id, order, (order * 2) - 1, sp_title, sp_ill))

                    # Insert right page (story prose & dialogue)
                    cur.execute("""
                        INSERT INTO story_pages (book_id, spread_number, page_number, page_side, title, text, image_url, dialogue)
                        VALUES (%s, %s, %s, 'right', NULL, %s, NULL, %s);
                    """, (new_book_id, order, order * 2, sp_text, sp_dialogue))

                # Update total page count
                total_pages = len(spread_indices) * 2
                cur.execute("UPDATE books SET pages = %s WHERE id = %s;", (total_pages, new_book_id))

            flash(f'Storybook "{title}" created successfully! ✨', 'success')
            return redirect(url_for('admin_books'))

        except Exception as e:
            app.logger.error(f"Error creating storybook: {e}")
            flash(f'Failed to create storybook: {e}', 'danger')
            return redirect(url_for('admin_book_new'))

    # GET: render Storybook Builder form
    categories = []
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM categories ORDER BY name ASC;")
            categories = cur.fetchall()
    except Exception:
        pass

    return render_template(
        'admin/book_editor.html',
        active_page='new_book',
        book=None,
        spreads=[],
        categories=categories
    )


@app.route('/admin/books/<int:book_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_book_edit(book_id):
    """Edit existing storybook details, cover artwork, and dynamic story spreads."""
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM books WHERE id = %s;", (book_id,))
        book = cur.fetchone()
    if not book:
        flash('Storybook not found.', 'danger')
        return redirect(url_for('admin_books'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Book title cannot be empty.', 'danger')
            return redirect(url_for('admin_book_edit', book_id=book_id))

        category_id = request.form.get('category_id')
        category_name = book['category']
        try:
            with db.cursor() as cur:
                cur.execute("SELECT name FROM categories WHERE id = %s;", (category_id,))
                cat_row = cur.fetchone()
                if cat_row:
                    category_name = cat_row['name']
        except Exception:
            pass

        author = request.form.get('author', 'Once Upon a Page').strip() or 'Once Upon a Page'
        target_age = request.form.get('target_age', '3-7 years').strip()
        duration = request.form.get('duration', '5 mins').strip()
        description = request.form.get('description', '').strip()

        action_save = request.form.get('action_save')
        is_published = book['is_published']
        if action_save == 'publish':
            is_published = 1
        elif action_save == 'draft':
            is_published = 0

        # Cover artwork replacement check
        cover_file = request.files.get('cover_image')
        new_cover_path = save_image_upload(cover_file, 'covers')
        cover_path = new_cover_path or book['cover']

        try:
            with db.cursor() as cur:
                # 1. Update book metadata
                cur.execute("""
                    UPDATE books 
                    SET title = %s, category_id = %s, category = %s, cover = %s,
                        author = %s, description = %s, target_age = %s, duration = %s,
                        is_published = %s
                    WHERE id = %s;
                """, (title, category_id, category_name, cover_path, author, description, target_age, duration, is_published, book_id))

                # 2. Update spreads: clear previous and re-insert
                cur.execute("DELETE FROM story_pages WHERE book_id = %s;", (book_id,))

                spread_indices = []
                for k in request.form.keys():
                    m = re.match(r'^spread_text_(\d+)$', k)
                    if m:
                        spread_indices.append(int(m.group(1)))
                spread_indices = sorted(list(set(spread_indices)))
                if not spread_indices:
                    spread_indices = [1]

                for order, idx in enumerate(spread_indices, start=1):
                    sp_title = request.form.get(f'spread_title_{idx}', '').strip() or f'Chapter {order}'
                    sp_text = request.form.get(f'spread_text_{idx}', '').strip()
                    sp_dialogue = request.form.get(f'spread_dialogue_{idx}', '').strip()

                    ill_file = request.files.get(f'spread_illustration_{idx}')
                    sp_ill = save_image_upload(ill_file, 'story_pages')
                    if not sp_ill:
                        sp_ill = request.form.get(f'existing_illustration_{idx}', '').strip()
                    if not sp_ill:
                        sp_ill = cover_path

                    # Left page
                    cur.execute("""
                        INSERT INTO story_pages (book_id, spread_number, page_number, page_side, title, text, image_url, dialogue)
                        VALUES (%s, %s, %s, 'left', %s, NULL, %s, NULL);
                    """, (book_id, order, (order * 2) - 1, sp_title, sp_ill))

                    # Right page
                    cur.execute("""
                        INSERT INTO story_pages (book_id, spread_number, page_number, page_side, title, text, image_url, dialogue)
                        VALUES (%s, %s, %s, 'right', NULL, %s, NULL, %s);
                    """, (book_id, order, order * 2, sp_text, sp_dialogue))

                total_pages = len(spread_indices) * 2
                cur.execute("UPDATE books SET pages = %s WHERE id = %s;", (total_pages, book_id))

            flash(f'Storybook "{title}" updated successfully! ✨', 'success')
            return redirect(url_for('admin_books'))

        except Exception as e:
            app.logger.error(f"Error updating storybook: {e}")
            flash(f'Failed to update storybook: {e}', 'danger')
            return redirect(url_for('admin_book_edit', book_id=book_id))

    # GET
    categories = []
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM categories ORDER BY name ASC;")
            categories = cur.fetchall()
    except Exception:
        pass

    spreads = get_book_spreads(book)
    return render_template(
        'admin/book_editor.html',
        active_page='books',
        book=book,
        spreads=spreads,
        categories=categories
    )


@app.route('/admin/books/<int:book_id>/toggle-publish', methods=['POST'])
@admin_required
def admin_book_toggle_publish(book_id):
    """Toggle book published / draft state."""
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT title, is_published FROM books WHERE id = %s;", (book_id,))
            book = cur.fetchone()
            if book:
                new_status = 0 if book['is_published'] else 1
                cur.execute("UPDATE books SET is_published = %s WHERE id = %s;", (new_status, book_id))
                state_str = "published to the digital library" if new_status else "moved to draft"
                flash(f'Storybook "{book["title"]}" is now {state_str}.', 'success')
    except Exception as e:
        app.logger.error(f"Error toggling publish state: {e}")
        flash('Failed to update book publish status.', 'danger')

    return redirect(url_for('admin_books'))


@app.route('/admin/books/<int:book_id>/delete', methods=['POST'])
@admin_required
def admin_book_delete(book_id):
    """Permanently delete a storybook and all associated spreads."""
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT title FROM books WHERE id = %s;", (book_id,))
            book = cur.fetchone()
            if book:
                cur.execute("DELETE FROM books WHERE id = %s;", (book_id,))
                flash(f'Storybook "{book["title"]}" was removed.', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting book: {e}")
        flash('Failed to delete storybook.', 'danger')

    return redirect(url_for('admin_books'))


@app.route('/admin/books/<int:book_id>/preview')
@admin_required
def admin_book_preview(book_id):
    """
    Administrator Storybook Preview:
    Opens reader view without modifying or saving user reading history.
    """
    db = get_db()
    book = None
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM books WHERE id = %s;", (book_id,))
            book = cur.fetchone()
    except Exception as e:
        app.logger.error(f"Error checking book for preview: {e}")

    if not book:
        flash('Storybook not found.', 'danger')
        return redirect(url_for('admin_books'))

    spreads = get_book_spreads(book)
    template_to_render = 'twinkle_reader.html' if book['id'] == 1 or book.get('slug') == 'twinkle' else 'reader.html'
    return render_template(
        template_to_render,
        book=book,
        spreads=spreads,
        last_read_page=1,
        is_preview=True
    )


# ==============================================================================
# ADMIN: Category Management
# ==============================================================================

@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    """List all categories with storybook count, and handle adding new categories."""
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('admin_categories'))

        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        try:
            with db.cursor() as cur:
                cur.execute("INSERT INTO categories (name, slug, description) VALUES (%s, %s, %s);", (name, slug, description))
                flash(f'Category "{name}" created successfully.', 'success')
        except pymysql.err.IntegrityError:
            flash(f'A category named "{name}" already exists.', 'warning')
        except Exception as e:
            app.logger.error(f"Error creating category: {e}")
            flash('Failed to create category.', 'danger')

        return redirect(url_for('admin_categories'))

    categories = []
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.slug, c.description, c.created_at,
                       (SELECT COUNT(*) FROM books b WHERE b.category_id = c.id) AS book_count
                FROM categories c
                ORDER BY c.name ASC;
            """)
            categories = cur.fetchall()
            for c in categories:
                c['created_at_formatted'] = format_datetime(c.get('created_at'))
    except Exception as e:
        app.logger.error(f"Error loading categories: {e}")

    return render_template(
        'admin/categories.html',
        active_page='categories',
        categories=categories
    )


@app.route('/admin/categories/<int:category_id>/edit', methods=['POST'])
@admin_required
def admin_category_edit(category_id):
    """Edit existing category name and description."""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Category name cannot be empty.', 'danger')
        return redirect(url_for('admin_categories'))

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE categories SET name = %s, description = %s WHERE id = %s;", (name, description, category_id))
            flash(f'Category "{name}" updated.', 'success')
    except Exception as e:
        app.logger.error(f"Error updating category: {e}")
        flash('Failed to update category.', 'danger')

    return redirect(url_for('admin_categories'))


@app.route('/admin/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def admin_category_delete(category_id):
    """Delete a category only if no books are assigned to it."""
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM books WHERE category_id = %s;", (category_id,))
            count = cur.fetchone()['cnt']
            if count > 0:
                flash(f'Cannot delete category because {count} storybook(s) are currently assigned to it. Please reassign those books first.', 'danger')
            else:
                cur.execute("DELETE FROM categories WHERE id = %s;", (category_id,))
                flash('Category was deleted successfully.', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting category: {e}")
        flash('Failed to delete category.', 'danger')

    return redirect(url_for('admin_categories'))


# ==============================================================================
# ADMIN: Welcome Page Management
# ==============================================================================

@app.route('/admin/welcome', methods=['GET', 'POST'])
@admin_required
def admin_welcome():
    """
    Manage the Bedtime Story Welcome Page:
    Allows administrator to upload and preview background hero artwork and customize
    atmosphere text without touching source code.
    """
    db = get_db()
    if request.method == 'POST':
        welcome_label = request.form.get('welcome_label', '').strip()
        welcome_heading = request.form.get('welcome_heading', '').strip()
        welcome_subtitle = request.form.get('welcome_subtitle', '').strip()
        welcome_button_text = request.form.get('welcome_button_text', '').strip()
        welcome_bg_type = request.form.get('welcome_bg_type', 'image').strip()
        remove_welcome_image = request.form.get('remove_welcome_image')
        remove_welcome_video = request.form.get('remove_welcome_video')

        # Hero background image upload
        bg_file = request.files.get('welcome_bg')
        new_bg_path = save_image_upload(bg_file, 'welcome')

        # Hero background video upload
        bg_video_file = request.files.get('welcome_bg_video')
        new_video_path = save_video_upload(bg_video_file, 'welcome')

        # If a new video file was uploaded and type wasn't explicitly changed, activate video
        if new_video_path and 'welcome_bg_type' not in request.form:
            welcome_bg_type = 'video'
        elif new_bg_path and 'welcome_bg_type' not in request.form:
            welcome_bg_type = 'image'

        updates = [
            ('welcome_label', welcome_label or 'Cozy Bedtime Stories'),
            ('welcome_heading', welcome_heading or 'Welcome to a World of Little Stories'),
            ('welcome_subtitle', welcome_subtitle or "Every little story holds a little magic. Come, let's explore!"),
            ('welcome_button_text', welcome_button_text or 'Enter the Story World ✨'),
            ('welcome_bg_type', welcome_bg_type)
        ]
        if new_bg_path:
            updates.append(('welcome_bg_image', new_bg_path))
        elif remove_welcome_image:
            updates.append(('welcome_bg_image', 'images/welcome_bg.jpg'))

        if new_video_path:
            updates.append(('welcome_bg_video', new_video_path))
        elif remove_welcome_video:
            updates.append(('welcome_bg_video', ''))

        try:
            with db.cursor() as cur:
                for k, v in updates:
                    cur.execute("""
                        INSERT INTO site_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);
                    """, (k, v))
            db.commit()
            save_disk_settings_backup(get_site_settings())
            flash('Welcome page settings updated successfully! ✨', 'success')
        except Exception as e:
            app.logger.error(f"Error updating welcome settings: {e}")
            flash('Failed to update welcome settings.', 'danger')

        return redirect(url_for('admin_welcome'))

    settings = get_site_settings()
    return render_template(
        'admin/welcome.html',
        active_page='welcome',
        settings=settings
    )


@app.route('/admin/login-settings', methods=['GET', 'POST'])
@admin_required
def admin_login_settings():
    """
    Manage the Login Landing Page Background:
    Allows administrator to choose between Plain, Image, or Video background,
    upload/preview media, replace or remove media, and save settings.
    """
    db = get_db()
    if request.method == 'POST':
        login_bg_type = request.form.get('login_bg_type', 'plain').strip()
        remove_login_image = request.form.get('remove_login_image')
        remove_login_video = request.form.get('remove_login_video')

        # Image upload
        bg_file = request.files.get('login_bg')
        new_img_path = save_image_upload(bg_file, 'login')

        # Video upload
        bg_video_file = request.files.get('login_bg_video')
        new_video_path = save_video_upload(bg_video_file, 'login')

        # Auto-switch type if new file uploaded without explicit radio change
        if new_video_path and 'login_bg_type' not in request.form:
            login_bg_type = 'video'
        elif new_img_path and 'login_bg_type' not in request.form:
            login_bg_type = 'image'

        updates = [
            ('login_bg_type', login_bg_type)
        ]
        if new_img_path:
            updates.append(('login_bg_image', new_img_path))
        elif remove_login_image:
            updates.append(('login_bg_image', ''))

        if new_video_path:
            updates.append(('login_bg_video', new_video_path))
        elif remove_login_video:
            updates.append(('login_bg_video', ''))

        try:
            with db.cursor() as cur:
                for k, v in updates:
                    cur.execute("""
                        INSERT INTO site_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);
                    """, (k, v))
            db.commit()
            save_disk_settings_backup(get_site_settings())
            flash('Login landing page background settings saved successfully! ✨', 'success')
        except Exception as e:
            app.logger.error(f"Error updating login background settings: {e}")
            flash('Failed to update login background settings.', 'danger')

        return redirect(url_for('admin_login_settings'))

    settings = get_site_settings()
    return render_template(
        'admin/login_settings.html',
        active_page='login_settings',
        settings=settings
    )


# ==============================================================================
# ADMIN: Reading Analytics & Insights
# ==============================================================================

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """
    Reading Analytics:
    Aggregates reading session metrics, top-read books, top favorites,
    and recent reader activity.
    """
    db = get_db()
    analytics = {
        'total_books_opened': 0,
        'total_sessions': 0,
        'active_readers': 0,
        'total_favorites': 0
    }
    recent_sessions = []
    popular_books = []
    chart_top_read_titles = []
    chart_top_read_counts = []
    chart_fav_titles = []
    chart_fav_counts = []

    try:
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(DISTINCT book_id) AS c FROM reading_history;")
            analytics['total_books_opened'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(*) AS c FROM reading_history;")
            analytics['total_sessions'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(DISTINCT user_id) AS c FROM reading_history;")
            analytics['active_readers'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(*) AS c FROM user_favorites;")
            analytics['total_favorites'] = cur.fetchone()['c']

            # Top read books
            cur.execute("""
                SELECT b.title, COUNT(rh.id) AS read_count
                FROM books b
                JOIN reading_history rh ON b.id = rh.book_id
                GROUP BY b.id
                ORDER BY read_count DESC
                LIMIT 6;
            """)
            for r in cur.fetchall():
                chart_top_read_titles.append(r['title'])
                chart_top_read_counts.append(r['read_count'])

            # Top favorited books
            cur.execute("""
                SELECT b.title, COUNT(uf.id) AS fav_count
                FROM books b
                JOIN user_favorites uf ON b.id = uf.book_id
                GROUP BY b.id
                ORDER BY fav_count DESC
                LIMIT 5;
            """)
            for r in cur.fetchall():
                chart_fav_titles.append(r['title'])
                chart_fav_counts.append(r['fav_count'])

            # Recent sessions
            cur.execute("""
                SELECT rh.last_read_page, rh.total_pages, rh.last_opened_at,
                       u.full_name AS user_name, b.title AS book_title
                FROM reading_history rh
                JOIN users u ON rh.user_id = u.id
                JOIN books b ON rh.book_id = b.id
                ORDER BY rh.last_opened_at DESC
                LIMIT 10;
            """)
            s_rows = cur.fetchall()
            for s in s_rows:
                s['last_opened_formatted'] = format_relative_time(s.get('last_opened_at'))
                recent_sessions.append(s)

            # Popular books detailed list
            cur.execute("""
                SELECT b.id, b.title, b.cover, b.category,
                       (SELECT COUNT(*) FROM reading_history rh WHERE rh.book_id = b.id) AS reader_count,
                       (SELECT COUNT(*) FROM user_favorites uf WHERE uf.book_id = b.id) AS fav_count
                FROM books b
                ORDER BY reader_count DESC, fav_count DESC
                LIMIT 6;
            """)
            popular_books = cur.fetchall()

    except Exception as e:
        app.logger.error(f"Error computing analytics: {e}")

    # Fallback chart data if library is new
    if not chart_top_read_titles:
        chart_top_read_titles = ['Twinkle', 'The Fairy and the Firefly', 'The Little Girl and Her Dreams']
        chart_top_read_counts = [5, 3, 2]
    if not chart_fav_titles:
        chart_fav_titles = ['Twinkle', 'The Fairy and the Firefly']
        chart_fav_counts = [4, 2]

    return render_template(
        'admin/analytics.html',
        active_page='analytics',
        analytics=analytics,
        recent_sessions=recent_sessions,
        popular_books=popular_books,
        chart_top_read_titles=chart_top_read_titles,
        chart_top_read_counts=chart_top_read_counts,
        chart_fav_titles=chart_fav_titles,
        chart_fav_counts=chart_fav_counts
    )


# ==============================================================================
# ADMIN: System Settings
# ==============================================================================

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """System Settings & Diagnostics: Manage defaults and check database health."""
    db = get_db()
    if request.method == 'POST':
        default_target_age = request.form.get('default_target_age', '3-7 years').strip()
        default_duration = request.form.get('default_duration', '5 mins').strip()

        try:
            with db.cursor() as cur:
                for k, v in [('default_target_age', default_target_age), ('default_duration', default_duration)]:
                    cur.execute("""
                        INSERT INTO site_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);
                    """, (k, v))
            flash('Library preferences saved successfully.', 'success')
        except Exception as e:
            app.logger.error(f"Error saving settings: {e}")
            flash('Failed to save preferences.', 'danger')

        return redirect(url_for('admin_settings'))

    settings = get_site_settings()
    tables_count = 7
    try:
        with db.cursor() as cur:
            cur.execute("SHOW TABLES;")
            tables_count = len(cur.fetchall())
    except Exception:
        pass

    return render_template(
        'admin/settings.html',
        active_page='settings',
        settings=settings,
        db_tables_count=tables_count
    )


# ==============================================================================
# Main Application Entry Point
# ==============================================================================

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
