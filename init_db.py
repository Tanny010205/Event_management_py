"""
Database Initialization Script
Executes schema.sql against local MySQL server.
Can optionally seed realistic sample college events and students for demonstration.
"""
import sys
import os
import mysql.connector
from werkzeug.security import generate_password_hash
from config import Config

def init_database(seed_sample_data=False):
    print("=" * 60)
    print("College Event Management System - Database Initializer")
    print("=" * 60)
    print(f"Connecting to MySQL at {Config.DB_HOST}:{Config.DB_PORT} as '{Config.DB_USER}'...")

    try:
        # Step 1: Connect to MySQL server (without selecting database initially)
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            autocommit=True
        )
        cursor = conn.cursor()
        print("[+] Successfully connected to MySQL server.")

        # Step 2: Read schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), "database", "schema.sql")
        if not os.path.exists(schema_path):
            print(f"[-] Error: Schema file not found at {schema_path}")
            return False

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        # Step 3: Execute schema statements (split by semicolon)
        print("[+] Creating database and tables...")
        statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]
        for stmt in statements:
            # Skip empty or comment-only statements
            lines = [line for line in stmt.split("\n") if not line.strip().startswith("--")]
            clean_stmt = "\n".join(lines).strip()
            if clean_stmt:
                cursor.execute(clean_stmt)

        print("[+] Tables (users, events, students, registrations) verified / created.")

        # Step 4: Check if default admin account exists
        cursor.execute(f"USE {Config.DB_NAME};")
        cursor.execute("SELECT user_id, username FROM users WHERE username = 'admin';")
        admin_user = cursor.fetchone()

        if not admin_user:
            default_password = "admin123"
            hashed_pw = generate_password_hash(default_password)
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, 'admin');
            """, ("admin", hashed_pw))
            print(f"[+] Default administrator created:")
            print(f"    Username: admin")
            print(f"    Password: {default_password} (Please change or update in production)")
        else:
            print("[i] Admin account 'admin' already exists.")

        # Step 5: Optional Seed Data
        if seed_sample_data:
            seed_data(cursor)

        cursor.close()
        conn.close()
        print("\n[SUCCESS] Database initialization completed successfully!")
        return True

    except mysql.connector.Error as err:
        print("\n[ERROR] Failed to initialize database:")
        print(f"  Code: {err.errno}")
        print(f"  Message: {err.msg}")
        print("\nTroubleshooting tips:")
        print("  1. Is MySQL Server installed and running?")
        print("  2. Check your credentials in .env file (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT).")
        print("  3. For XAMPP: Start MySQL module in XAMPP Control Panel.")
        return False
    except Exception as ex:
        print(f"\n[UNEXPECTED ERROR] {ex}")
        return False

def seed_data(cursor):
    """Inserts sample students, events, and registrations for testing and demonstration."""
    print("[+] Seeding sample college events, students, and registrations...")
    
    # Sample Students
    students_data = [
        ("Aarav Sharma", "aarav.sharma@college.edu", "CS2023001", "Computer Science", "3rd Year"),
        ("Ananya Patel", "ananya.patel@college.edu", "IT2023015", "Information Technology", "3rd Year"),
        ("Rohan Verma", "rohan.verma@college.edu", "EC2024042", "Electronics", "2nd Year"),
        ("Priya Nair", "priya.nair@college.edu", "ME2022088", "Mechanical", "4th Year"),
        ("Vikram Singh", "vikram.singh@college.edu", "CS2023009", "Computer Science", "3rd Year"),
        ("Sneha Iyer", "sneha.iyer@college.edu", "CV2024012", "Civil", "2nd Year"),
        ("Kavya Reddy", "kavya.reddy@college.edu", "IT2023021", "Information Technology", "3rd Year")
    ]

    for name, email, roll, dept, year in students_data:
        cursor.execute("""
            INSERT IGNORE INTO students (name, email, roll_number, department, academic_year)
            VALUES (%s, %s, %s, %s, %s);
        """, (name, email, roll, dept, year))

    # Sample Events
    events_data = [
        (
            "TechFest 2026: Annual Hackathon",
            "A 24-hour coding marathon addressing real-world problem statements. Win exciting prizes and certificates.",
            "Main Auditorium & CS Labs",
            "2026-11-15 09:00:00",
            "2026-11-10 23:59:00",
            50,
            "Upcoming"
        ),
        (
            "AI & Machine Learning Workshop",
            "Hands-on workshop exploring deep learning neural networks, computer vision, and prompt engineering.",
            "Seminar Hall B",
            "2026-11-05 10:30:00",
            "2026-11-01 18:00:00",
            40,
            "Upcoming"
        ),
        (
            "Inter-College Robotics Championship",
            "Battle of autonomous and line-follower bots designed by engineering student teams.",
            "Indoor Sports Complex",
            "2026-10-18 11:00:00",
            "2026-10-15 17:00:00",
            30,
            "Completed"
        ),
        (
            "Guest Lecture on Quantum Computing",
            "Distinguished talk by Dr. R. Sundaram from Indian Institute of Science on qubits and quantum algorithms.",
            "Conference Room 1",
            "2026-12-01 14:00:00",
            "2026-11-28 23:59:00",
            60,
            "Upcoming"
        ),
        (
            "Cultural Night: Resonance 2026",
            "Annual musical evening and dance competition featuring inter-department talent.",
            "Open Air Amphitheatre",
            "2026-10-25 18:00:00",
            "2026-10-20 23:59:00",
            100,
            "Cancelled"
        )
    ]

    for title, desc, venue, edate, dline, cap, status in events_data:
        cursor.execute("""
            SELECT event_id FROM events WHERE title = %s;
        """, (title,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO events (title, description, venue, event_date, registration_deadline, capacity, status, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1);
            """, (title, desc, venue, edate, dline, cap, status))

    # Sample Registrations
    cursor.execute("SELECT student_id FROM students;")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT event_id FROM events WHERE title = 'TechFest 2026: Annual Hackathon';")
    techfest = cursor.fetchone()
    
    cursor.execute("SELECT event_id FROM events WHERE title = 'AI & Machine Learning Workshop';")
    ai_workshop = cursor.fetchone()

    if techfest and student_ids:
        for sid in student_ids[:4]:  # Register first 4 students
            cursor.execute("""
                INSERT IGNORE INTO registrations (student_id, event_id, status)
                VALUES (%s, %s, 'Registered');
            """, (sid, techfest[0]))

    if ai_workshop and student_ids:
        for sid in student_ids[2:6]:  # Register students 3-6
            cursor.execute("""
                INSERT IGNORE INTO registrations (student_id, event_id, status)
                VALUES (%s, %s, 'Registered');
            """, (sid, ai_workshop[0]))

    print("[+] Sample students, events, and registrations seeded successfully.")

if __name__ == "__main__":
    seed = "--seed" in sys.argv
    init_database(seed_sample_data=seed)
