"""
Once Upon a Page - Admin Account Creation Script
Securely creates or promotes an administrator account in the existing users table.
Uses getpass to hide passwords during entry and hashes passwords with pbkdf2:sha256.
"""

import sys
import getpass
import re
import pymysql
from werkzeug.security import generate_password_hash
from config import Config

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def get_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def create_admin(full_name=None, email=None, password=None):
    print("=" * 60)
    print("  ONCE UPON A PAGE · ADMINISTRATOR ACCOUNT SETUP")
    print("=" * 60)

    # 1. Full Name
    if not full_name:
        try:
            full_name = input("Enter Admin Full Name [Administrator]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSetup cancelled.")
            return False
    if not full_name:
        full_name = "Administrator"

    # 2. Email Address
    while not email:
        try:
            email_input = input("Enter Admin Email: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nSetup cancelled.")
            return False
        if not email_input or not EMAIL_REGEX.match(email_input):
            print("⚠️ Please enter a valid email address.")
            continue
        email = email_input

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if user already exists
            cur.execute("SELECT id, full_name, email, role FROM users WHERE email = %s", (email,))
            existing = cur.fetchone()

            if existing:
                if existing.get('role') == 'admin':
                    print(f"\n⚠️ User '{email}' is ALREADY an administrator (User ID #{existing['id']}).")
                    return False
                else:
                    print(f"\nAccount '{email}' exists as regular user. Promoting to Administrator...")
                    cur.execute("UPDATE users SET role = 'admin', is_active = 1 WHERE id = %s", (existing['id'],))
                    print(f"✨ Successfully promoted '{email}' to Administrator role!")
                    return True

            # 3. Secure Password Input (with confirmation)
            while not password:
                try:
                    pwd1 = getpass.getpass("Enter Admin Password (hidden): ")
                    if len(pwd1) < 6:
                        print("⚠️ Password must be at least 6 characters long.")
                        continue
                    pwd2 = getpass.getpass("Confirm Admin Password (hidden): ")
                    if pwd1 != pwd2:
                        print("⚠️ Passwords do not match. Please retype carefully.")
                        continue
                    password = pwd1
                except (KeyboardInterrupt, EOFError):
                    print("\nSetup cancelled.")
                    return False

            # Hash password using pbkdf2:sha256 (identical to app.py)
            hashed_pwd = generate_password_hash(password, method='pbkdf2:sha256')

            cur.execute("""
                INSERT INTO users (full_name, email, password_hash, role, is_active)
                VALUES (%s, %s, %s, 'admin', 1)
            """, (full_name, email, hashed_pwd))

            print("\n" + "=" * 60)
            print(f"✨ Administrator account '{email}' created successfully!")
            print("You can now sign in at: /admin/login")
            print("=" * 60)
            return True
    finally:
        try:
            conn.close()
        except Exception:
            pass

if __name__ == '__main__':
    # Can also accept CLI args for automated environments: python create_admin.py [name] [email] [password]
    name_arg = sys.argv[1] if len(sys.argv) > 1 else None
    email_arg = sys.argv[2] if len(sys.argv) > 2 else None
    pass_arg = sys.argv[3] if len(sys.argv) > 3 else None
    create_admin(name_arg, email_arg, pass_arg)
