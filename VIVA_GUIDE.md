# College Event Management System — Viva Examination & Interview Guide

This guide is designed for your viva presentation and professor questions. It explains the core concepts, architecture, database design, and code decisions in simple, straightforward language.

---

## 1. Core Architectural Concepts

### Q1: What does the College Event Management System do?
**Answer:**
It is a web-based application designed for colleges to manage campus events and student participation. Administrators can create, edit, schedule, and track events, while students can browse events, register profiles, and enroll in activities within set capacities and deadlines. It also generates real-time reports and CSV exports.

### Q2: Why did we choose Python and Flask for this project?
**Answer:**
Flask is a lightweight, flexible Python WSGI micro-framework. Unlike larger frameworks like Django, Flask does not force heavy boilerplate or predefined ORMs, allowing us to implement direct SQL queries using `mysql-connector-python`, explicit transaction handling, and modular Blueprints while keeping the code easy to understand and maintain.

### Q3: What is the role of Bootstrap 5?
**Answer:**
Bootstrap 5 is a responsive CSS framework that provides a professional layout using its 12-column grid system, cards, navigation bars, tables, modal dialogs, and alert badges. It eliminates the need for hundreds of lines of complex custom CSS and ensures mobile and desktop responsiveness out-of-the-box.

### Q4: How does the frontend communicate with Flask?
**Answer:**
Communication happens via standard HTTP request-response cycles:
1. **GET requests:** When a user visits a URL (e.g., `/events/1`), Flask executes Python logic, fetches database records, injects the data into Jinja2 templates, and returns rendered HTML.
2. **POST requests:** When forms are submitted (e.g., student registration or event creation), form data is sent in the HTTP request body along with a CSRF token. Flask reads `request.form`, processes the data, writes to MySQL, and redirects the browser using `redirect(url_for(...))`.

### Q5: How does Flask connect to MySQL?
**Answer:**
We use `mysql-connector-python` with connection handling managed through Flask's request lifecycle (`g` object):
- During a request, `get_db_connection()` creates or reuses an active MySQL connection.
- After the response is sent, Flask's `@app.teardown_appcontext` hook calls `close_db_connection()`, preventing connection leaks.
- Queries are executed using cursors with `dictionary=True` so columns can be accessed by name (e.g., `row['title']`).

---

## 2. Database Design & SQL

### Q6: What are the four tables and their purposes?
**Answer:**
1. **`users`:** Stores administrator accounts with hashed passwords for authentication.
2. **`events`:** Stores event details such as title, description, venue, date, deadline, maximum capacity, and status.
3. **`students`:** Stores student directory records with unique constraints on email and roll number.
4. **`registrations`:** A junction table representing student enrollment in events, storing `student_id`, `event_id`, registration timestamp, and status.

### Q7: What are Primary Keys and Foreign Keys?
**Answer:**
- **Primary Key (PK):** A unique identifier for every row in a table (e.g., `student_id` in `students`, `event_id` in `events`).
- **Foreign Key (FK):** A column in one table that references the Primary Key of another table (e.g., `student_id` in `registrations` references `students.student_id`). It enforces referential integrity.

### Q8: What is the relationship between students, events, and registrations?
**Answer:**
It is a **Many-to-Many** relationship:
- One student can register for multiple events.
- One event can have multiple students registered.
To represent this in relational database design, we use the `registrations` table as an associative/junction table containing Foreign Keys to both `students` and `events`.

### Q9: What happens when an event is deleted?
**Answer:**
Because the Foreign Key in the `registrations` table is defined with `ON DELETE CASCADE`, deleting an event automatically removes all its associated registration records in MySQL. This prevents orphaned records and maintains database integrity.

### Q10: How do `JOIN` queries retrieve participant details?
**Answer:**
To show student names and roll numbers for an event, we join `registrations` with `students` using an inner join on the common `student_id`:
```sql
SELECT s.name, s.roll_number, s.department, r.registered_at
FROM registrations r
JOIN students s ON r.student_id = s.student_id
WHERE r.event_id = %s;
```

### Q11: Why do we use a `LEFT JOIN` in the events reports?
**Answer:**
An `INNER JOIN` only returns events that have at least one registration. By using `LEFT JOIN registrations r ON e.event_id = r.event_id`, all events are returned, including new events with **0** registrations, where `COUNT(r.registration_id)` evaluates to 0.

### Q12: How do `COUNT()` and `GROUP BY` work in department analytics?
**Answer:**
`GROUP BY s.department` aggregates all student registrations belonging to the same department into a single row, and `COUNT(r.registration_id)` computes the total number of registrations for each department.

---

## 3. Security & Concurrency

### Q13: How does admin login and password hashing work?
**Answer:**
We never store plain-text passwords. When an admin is created, Werkzeug's `generate_password_hash()` generates a secure PBKDF2:SHA256 hash with a unique salt. When logging in, `check_password_hash(stored_hash, submitted_password)` validates the password. If valid, session flags `session['admin_logged_in'] = True` and `session['admin_id']` are set.

### Q14: How are admin routes protected?
**Answer:**
We created a custom Python decorator `@admin_required` in `utils.py`. Before executing any protected route handler (like `/admin/dashboard` or `/admin/events`), the decorator checks if `session.get('admin_logged_in')` is True. If not, it redirects the user to `/admin/login`.

### Q15: What is CSRF and how do we prevent it?
**Answer:**
Cross-Site Request Forgery (CSRF) is an attack where a malicious site tricks an authenticated user's browser into submitting unauthorized actions. We prevent this by generating a cryptographically secure random token in `session['_csrf_token']`. Every POST form sends this token as a hidden field. Flask's `@app.before_request` hook validates that the submitted token matches the session token.

### Q16: How do we prevent SQL Injection?
**Answer:**
We use **parameterized queries** throughout the application (using `%s` placeholders in `mysql-connector-python`). The database engine compiles the SQL query structure separately from user inputs, ensuring user data is never interpreted as executable SQL commands.

### Q17: How is event capacity safely enforced against race conditions?
**Answer:**
In `database/db.py`, the `register_student_for_event()` function wraps the registration in an explicit database transaction with row-level pessimistic locking:
1. `SELECT ... FROM events WHERE event_id = %s FOR UPDATE;` locks the event row.
2. It verifies the current registration count against `capacity`.
3. If capacity is full, deadline passed, or event cancelled, it executes `conn.rollback()` and returns an informative error message.
4. If valid, it inserts the registration and executes `conn.commit()`.

### Q18: How do we prevent duplicate event registrations?
**Answer:**
Duplicate prevention is enforced at two levels:
1. **Application Logic:** The registration function checks if `student_id` and `event_id` already exist in `registrations`.
2. **Database Constraint:** The `registrations` table has a composite unique constraint `CONSTRAINT uq_student_event UNIQUE (student_id, event_id)`. If two simultaneous requests attempt to register the same student, MySQL rejects the second with error code `1062 (ER_DUP_ENTRY)`.

### Q19: What is CSV Formula Injection and how is it mitigated?
**Answer:**
Spreadsheet software (like Microsoft Excel or Google Sheets) automatically executes formulas in CSV cells starting with symbols like `=`, `+`, `-`, or `@`. An attacker could register with a name like `=CMD|' /C calc'!A0`. In `utils.py`, `sanitize_csv_cell()` prefixes any cell starting with these characters with a single apostrophe (`'`), forcing Excel to treat it as plain text.

### Q20: How is CSV file export implemented?
**Answer:**
We use Python's built-in `csv` and `io.StringIO` modules. Flask streams the formatted CSV string back to the browser inside a `Response` object with `mimetype='text/csv'` and a `Content-Disposition: attachment; filename=...` HTTP header, prompting the browser to download the file.

---

## 4. Quick Viva Reference Summary

| Requirement | Implementation in Project |
| :--- | :--- |
| **Framework** | Flask 3.0.3 (Application Factory & Blueprints) |
| **Database** | MySQL Server with `mysql-connector-python` |
| **Password Security** | Werkzeug PBKDF2:SHA256 (`generate_password_hash`) |
| **Session Security** | Flask server-side session cookies (HttpOnly, SameSite) |
| **CSRF Protection** | Cryptographic session tokens (`secrets.token_hex(32)`) |
| **Concurrency Lock** | MySQL Transactions with `SELECT ... FOR UPDATE` |
| **Duplicate Prevention** | Unique Database Constraints (`UNIQUE(student_id, event_id)`) |
| **Cascading Deletes** | Foreign Keys with `ON DELETE CASCADE` |
| **Frontend Styling** | Bootstrap 5.3 + Bootstrap Icons (No heavy node build tools) |
| **Testing** | Python `unittest` with 18 automated unit and mock tests |
