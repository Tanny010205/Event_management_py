"""
Admin User Creation Script
Provides a secure CLI tool to create an administrator account
using Werkzeug's secure password hashing.
"""
import sys
import getpass
import mysql.connector
from werkzeug.security import generate_password_hash
from config import Config

def create_admin(username=None, password=None):
    print("=" * 50)
    print("College Event Management - Create Admin User")
    print("=" * 50)

    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            autocommit=True
        )
        cursor = conn.cursor(dictionary=True)

        if not username:
            username = input("Enter admin username: ").strip()

        if not username:
            print("[-] Error: Username cannot be blank.")
            return

        # Check if username already exists
        cursor.execute("SELECT user_id FROM users WHERE username = %s;", (username,))
        existing = cursor.fetchone()
        if existing:
            print(f"[-] Error: User '{username}' already exists.")
            return

        if not password:
            password = getpass.getpass("Enter secure password: ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("[-] Error: Passwords do not match.")
                return

        if len(password) < 6:
            print("[-] Error: Password must be at least 6 characters long.")
            return

        # Securely hash the password
        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, 'admin');
        """, (username, password_hash))

        print(f"[+] Admin user '{username}' created successfully!")
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"[-] Database Error: {err}")
    except Exception as ex:
        print(f"[-] Unexpected error: {ex}")

if __name__ == "__main__":
    u = sys.argv[1] if len(sys.argv) > 1 else None
    p = sys.argv[2] if len(sys.argv) > 2 else None
    create_admin(u, p)
