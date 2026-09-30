import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key"
)


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST", "localhost"),
        port=int(os.environ.get("MYSQLPORT", "3306")),
        user=os.environ.get("MYSQLUSER", "root"),
        password=os.environ.get("MYSQLPASSWORD", "YOUR_MYSQL_PASSWORD"),
        database=os.environ.get("MYSQLDATABASE", "hostel_allocation")
    )


def login_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                if role == "student":
                    return redirect(url_for("login"))
                return redirect(url_for("admin_login"))
            return func(*args, **kwargs)

        return wrapper

    return decorator


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    message = None

    if request.method == "POST":
        data = (
            request.form["name"].strip(),
            request.form["email"].strip(),
            request.form["phone"].strip(),
            request.form["gender"],
            request.form["course"].strip(),
            request.form["year"],
            request.form["address"].strip()
        )

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO student
                (name, email, phone, gender, course, year, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data)

            conn.commit()

            student_id = cur.lastrowid

            cur.execute("""
                INSERT INTO student_account
                (student_id, email, password)
                VALUES (%s, %s, %s)
            """, (
                student_id,
                data[1],
                "ChangeMe@123"
            ))

            conn.commit()

            message = "Registration successful. Temporary password: ChangeMe@123"

        except Error as e:
            conn.rollback()
            message = f"Registration failed: {e}"

        finally:
            cur.close()
            conn.close()

    return render_template("register.html", message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT student.student_id,
                   student.name,
                   student.email
            FROM student
            JOIN student_account
            ON student.student_id = student_account.student_id
            WHERE student_account.email = %s
            AND student_account.password = %s
        """, (email, password))

        student = cur.fetchone()

        cur.close()
        conn.close()

        if student:
            session.clear()
            session["role"] = "student"
            session["student_id"] = student[0]
            session["student_name"] = student[1]

            return redirect(url_for("dashboard"))

        error = "Invalid email or password."

    return render_template("login.html", error=error)


@app.route("/dashboard")
@login_required("student")
def dashboard():
    sid = session["student_id"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT *
        FROM student
        WHERE student_id = %s
    """, (sid,))

    student = cur.fetchone()

    cur.execute("""
        SELECT a.application_id,
               a.application_date,
               a.status,
               h.hostel_name,
               h.hostel_type
        FROM application a
        JOIN hostel h
        ON a.hostel_id = h.hostel_id
        WHERE a.student_id = %s
        ORDER BY a.application_id DESC
        LIMIT 1
    """, (sid,))

    application = cur.fetchone()

    cur.execute("""
        SELECT al.allocation_id,
               al.allocation_date,
               r.room_number,
               h.hostel_name
        FROM allocation al
        JOIN room r
        ON al.room_id = r.room_id
        JOIN hostel h
        ON r.hostel_id = h.hostel_id
        WHERE al.student_id = %s
        ORDER BY al.allocation_id DESC
        LIMIT 1
    """, (sid,))

    allocation = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        student=student,
        application=application,
        allocation=allocation
    )


@app.route("/apply", methods=["GET", "POST"])
@login_required("student")
def apply_hostel():
    message = None

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT *
        FROM hostel
        ORDER BY hostel_name
    """)

    hostels = cur.fetchall()

    if request.method == "POST":
        hostel_id = request.form["hostel_id"]
        sid = session["student_id"]

        try:
            cur.execute("""
                SELECT COUNT(*) AS cnt
                FROM application
                WHERE student_id = %s
                AND status IN ('Pending', 'Approved')
            """, (sid,))

            if cur.fetchone()["cnt"] > 0:
                message = "You already have an active hostel application."

            else:
                cur.execute("""
                    INSERT INTO application
                    (student_id, hostel_id, application_date, status)
                    VALUES (%s, %s, CURDATE(), 'Pending')
                """, (sid, hostel_id))

                conn.commit()

                message = "Hostel application submitted successfully."

        except Error as e:
            conn.rollback()
            message = f"Application failed: {e}"

    cur.close()
    conn.close()

    return render_template(
        "apply.html",
        hostels=hostels,
        message=message
    )


@app.route("/application")
@login_required("student")
def application_status():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT a.*,
               h.hostel_name,
               h.hostel_type,
               h.location
        FROM application a
        JOIN hostel h
        ON a.hostel_id = h.hostel_id
        WHERE a.student_id = %s
        ORDER BY a.application_id DESC
    """, (session["student_id"],))

    applications = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "application_status.html",
        applications=applications
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT admin_id,
                   name,
                   email
            FROM admin_account
            WHERE email = %s
            AND password = %s
        """, (email, password))

        admin = cur.fetchone()

        cur.close()
        conn.close()

        if admin:
            session.clear()
            session["role"] = "admin"
            session["admin_id"] = admin["admin_id"]
            session["admin_name"] = admin["name"]

            return redirect(url_for("admin_dashboard"))

        error = "Invalid admin credentials."

    return render_template(
        "admin_login.html",
        error=error
    )


@app.route("/admin/dashboard")
@login_required("admin")
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT a.application_id,
               a.application_date,
               a.status,
               s.student_id,
               s.name AS student_name,
               s.email,
               h.hostel_name
        FROM application a
        JOIN student s
        ON a.student_id = s.student_id
        JOIN hostel h
        ON a.hostel_id = h.hostel_id
        ORDER BY a.application_id DESC
    """)

    applications = cur.fetchall()

    cur.execute("""
        SELECT r.room_id,
               r.room_number,
               r.capacity,
               r.occupied,
               r.room_status,
               h.hostel_name
        FROM room r
        JOIN hostel h
        ON r.hostel_id = h.hostel_id
        ORDER BY h.hostel_name,
                 r.room_number
    """)

    rooms = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        applications=applications,
        rooms=rooms
    )


@app.route(
    "/admin/application/<int:application_id>/approve",
    methods=["POST"]
)
@login_required("admin")
def approve_application(application_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE application
            SET status = 'Approved'
            WHERE application_id = %s
            AND status = 'Pending'
        """, (application_id,))

        conn.commit()

    except Error:
        conn.rollback()

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("admin_dashboard"))


@app.route(
    "/admin/application/<int:application_id>/reject",
    methods=["POST"]
)
@login_required("admin")
def reject_application(application_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE application
            SET status = 'Rejected'
            WHERE application_id = %s
            AND status = 'Pending'
        """, (application_id,))

        conn.commit()

    except Error:
        conn.rollback()

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("admin_dashboard"))


@app.route(
    "/admin/allocation/<int:application_id>",
    methods=["POST"]
)
@login_required("admin")
def allocate_room(application_id):
    room_id = request.form["room_id"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        conn.start_transaction()

        cur.execute("""
            SELECT student_id,
                   status
            FROM application
            WHERE application_id = %s
            FOR UPDATE
        """, (application_id,))

        application = cur.fetchone()

        cur.execute("""
            SELECT room_id,
                   capacity,
                   occupied,
                   room_status
            FROM room
            WHERE room_id = %s
            FOR UPDATE
        """, (room_id,))

        room = cur.fetchone()

        if not application or application["status"] != "Approved":
            raise ValueError(
                "Only approved applications can be allocated."
            )

        if (
            not room
            or room["occupied"] >= room["capacity"]
            or room["room_status"] == "Full"
        ):
            raise ValueError(
                "Selected room is full or unavailable."
            )

        cur.execute("""
            SELECT allocation_id
            FROM allocation
            WHERE student_id = %s
            LIMIT 1
        """, (application["student_id"],))

        if cur.fetchone():
            raise ValueError(
                "This student already has an allocation."
            )

        cur.execute("""
            INSERT INTO allocation
            (student_id, room_id, allocation_date)
            VALUES (%s, %s, CURDATE())
        """, (
            application["student_id"],
            room_id
        ))

        new_occupied = room["occupied"] + 1

        if new_occupied >= room["capacity"]:
            new_status = "Full"
        else:
            new_status = "Available"

        cur.execute("""
            UPDATE room
            SET occupied = %s,
                room_status = %s
            WHERE room_id = %s
        """, (
            new_occupied,
            new_status,
            room_id
        ))

        conn.commit()

    except Exception:
        conn.rollback()

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("admin_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )