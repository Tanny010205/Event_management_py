# College Event Management System

A full-stack web application built for college event organization, student participation, and administrative oversight.

Developed with **Python (Flask)**, **MySQL**, and **Bootstrap 5**.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Database Architecture & Relationships](#database-architecture--relationships)
4. [Beginner-Friendly SQL Guide](#beginner-friendly-sql-guide)
5. [Local Windows Setup Guide](#local-windows-setup-guide)
6. [Creating Administrator Accounts](#creating-administrator-accounts)
7. [Running the Application](#running-the-application)
8. [Automated Testing](#automated-testing)
9. [Manual Verification Checklist](#manual-verification-checklist)
10. [Viva Examination Guide](#viva-examination-guide)

---

## 1. Project Overview

The **College Event Management System** streamlines campus events, workshops, hackathons, and symposiums.

### Key Capabilities:
- **Public Event Portal:** Students can browse upcoming, ongoing, and completed events, filter by venue/date/status, and search by title.
- **Student Profile Management:** Self-service student registration with validation against duplicate email addresses and roll numbers.
- **Capacity-Controlled Participation:** Students register for events using their roll number or email. Concurrency-safe transactions prevent exceeding event capacity.
- **Admin Management Portal:** Secured administrative access to create, edit, cancel, and delete events.
- **Participant Tracking:** Event-specific attendee rosters retrieved via SQL JOINs.
- **Analytics & CSV Exports:** Real-time metrics, popularity ranking, department breakdown, and CSV downloads with formula injection sanitization.

---

## 2. Technology Stack

- **Backend:** Python 3.10+, Flask 3.0
- **Database:** MySQL Server 8.0+ / MariaDB via `mysql-connector-python`
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons, JavaScript (ES6)
- **Templating:** Jinja2
- **Security:** Werkzeug password hashing, CSRF session token verification, parameterized SQL queries, CSV formula sanitization

---

## 3. Database Architecture & Relationships

The system uses **four core relational tables** under the InnoDB engine:

```
+---------------+           +---------------+
|     users     |           |   students    |
+---------------+           +---------------+
| user_id (PK)  |           | student_id(PK)|
| username (UQ) |           | name          |
| password_hash |           | email (UQ)    |
| role          |           | roll_no (UQ)  |
+-------+-------+           +-------+-------+
        |                           |
        | created_by                |
        v                           v
+---------------+           +---------------+
|    events     |           | registrations |
+---------------+           +---------------+
| event_id (PK) |<----------| reg_id (PK)   |
| title         | event_id  | student_id(FK)|
| venue         |           | event_id (FK) |
| event_date    |           | registered_at |
| deadline      |           +---------------+
| capacity      |           (UQ: student_id,
| status        |                event_id)
+---------------+
```

### Table Details:
1. **`users`**: Administrative credentials. Passwords stored using PBKDF2:SHA256 hashes via Werkzeug.
2. **`events`**: Event schedule, venue, capacity limit, and status (`Upcoming`, `Ongoing`, `Completed`, `Cancelled`).
3. **`students`**: Student academic directory enforcing unique email and roll numbers.
4. **`registrations`**: Many-to-Many junction table linking students to events. Enforces unique constraint `(student_id, event_id)` so students cannot register twice. Includes `ON DELETE CASCADE` foreign keys so deleting an event cleanly cleans up associated registrations without orphaned rows.

---

## 4. Beginner-Friendly SQL Guide

If SQL is new to you, here is everything you need to know for this project:

### 1. What is a Database and a Table?
- A **database** (`college_events_db`) is a container for organized data.
- A **table** (`students`, `events`) is a spreadsheet-like structure containing records about a specific topic.
- **Rows (Records):** A single entry, e.g., one student (Aarav Sharma).
- **Columns (Fields):** Properties describing the record, e.g., `email`, `department`.

### 2. Primary Keys vs. Foreign Keys
- **Primary Key (PK):** A column that uniquely identifies every row in a table. In `students`, `student_id` is the primary key (1, 2, 3...).
- **Foreign Key (FK):** A column in one table that points to the Primary Key of another table. In `registrations`, `student_id` points to `students.student_id`, and `event_id` points to `events.event_id`. This connects a student to the event they registered for.

### 3. Core SQL Statements Used
- **`SELECT`:** Retrieves data from tables.
  ```sql
  SELECT title, venue, capacity FROM events WHERE status = 'Upcoming';
  ```
- **`INSERT`:** Adds new rows.
  ```sql
  INSERT INTO students (name, email, roll_number, department, academic_year)
  VALUES ('Priya Nair', 'priya@college.edu', 'ME2022', 'Mechanical', '4th Year');
  ```
- **`UPDATE`:** Modifies existing rows.
  ```sql
  UPDATE events SET status = 'Cancelled' WHERE event_id = 5;
  ```
- **`DELETE`:** Removes rows.
  ```sql
  DELETE FROM events WHERE event_id = 5;
  ```

### 4. What is a `JOIN`?
When data is split across tables, a `JOIN` connects them using their relational keys.
- **Example in Participant List:**
  ```sql
  SELECT s.name, s.roll_number, s.department, r.registered_at
  FROM registrations r
  JOIN students s ON r.student_id = s.student_id
  WHERE r.event_id = 1;
  ```
- **`LEFT JOIN`:** Returns all events even if they have **zero** registrations:
  ```sql
  SELECT e.title, COUNT(r.registration_id) AS total_enrolled
  FROM events e
  LEFT JOIN registrations r ON e.event_id = r.event_id
  GROUP BY e.event_id;
  ```

### 5. `COUNT()` and `GROUP BY`
- `COUNT()` counts the number of rows.
- `GROUP BY` bundles rows by a column before counting.
  ```sql
  -- Count registrations per department
  SELECT s.department, COUNT(r.registration_id) AS total_students
  FROM registrations r
  JOIN students s ON r.student_id = s.student_id
  GROUP BY s.department;
  ```

### 6. Why Parameterized Queries Matter (SQL Injection Prevention)
- **Vulnerable Code:** `query = f"SELECT * FROM users WHERE username = '{username}'"` (An attacker can input `' OR '1'='1` to bypass passwords).
- **Secure Parameterized Code (Our Project):**
  ```python
  cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
  ```
  The database engine treats `%s` strictly as data, making SQL injection impossible.

---

## 5. Local Windows Setup Guide

### Prerequisites
1. **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/). Check **"Add Python to PATH"** during installation.
2. **MySQL Server**:
   - Option A: Install [MySQL Community Server](https://dev.mysql.com/downloads/mysql/) and set a root password.
   - Option B: Install [XAMPP](https://www.apachefriends.org/) and start the MySQL module.

### Step-by-Step Setup

1. **Open Terminal / Command Prompt** in the project folder:
   ```cmd
   cd "E:\tanny project"
   ```

2. **Create and Activate a Virtual Environment:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```cmd
   copy .env.example .env
   ```
   Open `.env` in Notepad and set your MySQL password:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=college_events_db
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   SECRET_KEY=my_secure_random_flask_key_12345
   FLASK_DEBUG=0
   ```

5. **Initialize Database and Seed Sample Data:**
   Run the automated database initializer:
   ```cmd
   python init_db.py --seed
   ```
   This script:
   - Connects to your MySQL server.
   - Creates the `college_events_db` database.
   - Creates `users`, `events`, `students`, and `registrations` tables.
   - Seeds realistic sample events, students, and registrations.
   - Creates the default admin account:
     - **Username:** `admin`
     - **Password:** `admin123`

---

## 6. Creating Administrator Accounts

To create custom administrator credentials without revealing passwords in code, use the interactive CLI tool:

```cmd
python create_admin.py
```
Prompts:
```text
Enter admin username: principal
Enter secure password: 
Confirm password: 
[+] Admin user 'principal' created successfully!
```

---

## 7. Running the Application

### Option A: Using the Windows Batch Launcher
Double-click `run.bat` or run:
```cmd
run.bat
```

### Option B: Using Python directly
```cmd
venv\Scripts\activate
python app.py
```

### Accessing the Web Application
- **Public Home Page:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Admin Portal Login:** [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)
  - Default Username: `admin`
  - Default Password: `admin123`

---

## 8. Automated Testing

Run the comprehensive unit and integration test suite:

```cmd
python -m unittest tests/test_app.py
```

### What the test suite verifies:
- Flask application factory initialization.
- Admin route protection (redirects unauthenticated requests to `/admin/login`).
- Admin authentication with password hash verification.
- Admin logout clearing sessions.
- CSRF protection against cross-site forged POST requests.
- Student duplicate email and duplicate roll number rejection.
- Concurrency-safe event registration rules:
  - Rejection if event capacity is reached.
  - Rejection if event is cancelled.
  - Rejection if registration deadline has passed.
  - Rejection of duplicate student registrations for the same event.
- Event management form validation (positive capacity, deadline <= event date).
- Safe destructive actions (DELETE requires POST).
- CSV Formula Injection protection (CWE-1236 sanitization).

---

## 9. Manual Verification Checklist

When demonstrating to your professor:

1. **Public Browsing:**
   - [ ] Open `http://127.0.0.1:5000`.
   - [ ] Search events using the title search box (e.g. "Hackathon").
   - [ ] Filter by Status ("Upcoming") or Venue.
   - [ ] Click "Clear Filters" to reset.

2. **Student Registration:**
   - [ ] Click "Student Registration".
   - [ ] Enter a new student profile and submit.
   - [ ] Try submitting the same email or roll number again -> verify error alert is displayed.

3. **Event Participation:**
   - [ ] Open an open event details page.
   - [ ] Enter the registered roll number -> verify success alert and participant count increment.
   - [ ] Enter the same roll number again -> verify duplicate prevention alert.

4. **Admin Portal:**
   - [ ] Click "Admin Portal" -> Login with `admin` / `admin123`.
   - [ ] View Dashboard metrics (Total Events, Students, Registrations).
   - [ ] Click "Manage Events" -> Click "Create New Event" and save.
   - [ ] View participant list for an event.
   - [ ] Click "Reports" -> Review event summary, popularity rank, and department breakdown.
   - [ ] Click "Download CSV" -> Verify downloaded CSV file opens cleanly.
   - [ ] Click "Logout" -> Verify admin session is terminated.

---

## 10. Troubleshooting Common Issues

1. **"Can't connect to MySQL server on 'localhost'"**:
   - Ensure MySQL Server service or XAMPP MySQL module is running.
   - Verify `DB_HOST` and `DB_PORT` in `.env`.

2. **"Access denied for user 'root'@'localhost'"**:
   - Your MySQL root user password is incorrect in `.env`. Update `DB_PASSWORD`.

3. **"CSRF token missing or invalid"**:
   - Ensure cookies are enabled in your web browser. Refresh the page and resubmit.
