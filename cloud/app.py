import streamlit as st
import sqlite3
from datetime import datetime

DB_NAME = "smartclass_cloud.db"


# =========================================================
# DATABASE
# =========================================================

def create_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(student_id, date)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movement_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            entry_time TEXT,
            exit_time TEXT
        )
    """)

    connection.commit()
    connection.close()


# =========================================================
# STUDENTS
# =========================================================

def add_student(student_id, name, class_name):

    connection = sqlite3.connect(DB_NAME)

    try:
        connection.execute("""
            INSERT INTO students
            (student_id, name, class_name, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            name,
            class_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def get_students():

    connection = sqlite3.connect(DB_NAME)

    students = connection.execute("""
        SELECT
            student_id,
            name,
            class_name
        FROM students
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return students


# =========================================================
# ATTENDANCE
# =========================================================

def mark_attendance(student_id):

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    connection = sqlite3.connect(DB_NAME)

    try:

        connection.execute("""
            INSERT INTO attendance
            (student_id, date, time, status)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            date,
            time,
            "Present"
        ))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def get_today_attendance():

    today = datetime.now().strftime("%Y-%m-%d")

    connection = sqlite3.connect(DB_NAME)

    records = connection.execute("""
        SELECT
            attendance.student_id,
            students.name,
            students.class_name,
            attendance.time,
            attendance.status
        FROM attendance
        JOIN students
        ON attendance.student_id = students.student_id
        WHERE attendance.date = ?
        ORDER BY attendance.time
    """, (today,)).fetchall()

    connection.close()

    return records


# =========================================================
# ENTRY / EXIT
# =========================================================

def record_entry_exit(student_id):

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    connection = sqlite3.connect(DB_NAME)

    record = connection.execute("""
        SELECT id, entry_time, exit_time
        FROM movement_logs
        WHERE student_id = ?
        AND date = ?
        ORDER BY id DESC
        LIMIT 1
    """, (
        student_id,
        date
    )).fetchone()

    if record is None:

        connection.execute("""
            INSERT INTO movement_logs
            (student_id, date, entry_time, exit_time)
            VALUES (?, ?, ?, NULL)
        """, (
            student_id,
            date,
            current_time
        ))

        connection.commit()
        connection.close()

        return "ENTRY", current_time

    record_id = record[0]
    exit_time = record[2]

    if exit_time is None:

        connection.execute("""
            UPDATE movement_logs
            SET exit_time = ?
            WHERE id = ?
        """, (
            current_time,
            record_id
        ))

        connection.commit()
        connection.close()

        return "EXIT", current_time

    else:

        connection.execute("""
            INSERT INTO movement_logs
            (student_id, date, entry_time, exit_time)
            VALUES (?, ?, ?, NULL)
        """, (
            student_id,
            date,
            current_time
        ))

        connection.commit()
        connection.close()

        return "ENTRY", current_time


def get_today_movements():

    today = datetime.now().strftime("%Y-%m-%d")

    connection = sqlite3.connect(DB_NAME)

    movements = connection.execute("""
        SELECT
            movement_logs.student_id,
            students.name,
            movement_logs.entry_time,
            movement_logs.exit_time
        FROM movement_logs
        JOIN students
        ON movement_logs.student_id = students.student_id
        WHERE movement_logs.date = ?
        ORDER BY movement_logs.id DESC
    """, (today,)).fetchall()

    connection.close()

    return movements


# =========================================================
# START DATABASE
# =========================================================

create_database()


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Smart Classroom",
    page_icon="🏫",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🏫 AI Smart Classroom")

st.write(
    "Smart Classroom Monitoring System"
)

st.info(
    "☁️ Public Demo Version — "
    "Face recognition is demonstrated separately "
    "on the local version."
)

st.divider()


# =========================================================
# NAVIGATION
# =========================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Student Registration",
        "Attendance",
        "Entry Exit",
        "Recognition Demo"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.header("📊 Dashboard")

    students = get_students()
    attendance = get_today_attendance()
    movements = get_today_movements()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Students",
            len(students)
        )

    with col2:
        st.metric(
            "Present Today",
            len(attendance)
        )

    with col3:
        st.metric(
            "Movement Records",
            len(movements)
        )

    st.divider()

    st.subheader("Today's Attendance")

    if attendance:

        for record in attendance:

            st.write(
                f"✅ **{record[1]}** "
                f"({record[0]}) — "
                f"Class {record[2]} — "
                f"{record[3]}"
            )

    else:

        st.info(
            "No attendance recorded today."
        )


# =========================================================
# STUDENT REGISTRATION
# =========================================================

elif page == "Student Registration":

    st.header("👨‍🎓 Student Registration")

    with st.form("student_form"):

        student_id = st.text_input(
            "Student ID",
            placeholder="S001"
        )

        name = st.text_input(
            "Student Name",
            placeholder="Test Student"
        )

        class_name = st.text_input(
            "Class",
            placeholder="10-A"
        )

        submitted = st.form_submit_button(
            "➕ Register Student"
        )

        if submitted:

            if not student_id or not name or not class_name:

                st.warning(
                    "Please fill in all fields."
                )

            else:

                success = add_student(
                    student_id.strip(),
                    name.strip(),
                    class_name.strip()
                )

                if success:

                    st.success(
                        f"{name} registered successfully! 🎉"
                    )

                else:

                    st.error(
                        "This Student ID already exists."
                    )

    st.divider()

    st.subheader("📋 Registered Students")

    students = get_students()

    if students:

        for student in students:

            st.write(
                f"**{student[0]}** — "
                f"{student[1]} — "
                f"Class {student[2]}"
            )

    else:

        st.info(
            "No students registered yet."
        )


# =========================================================
# ATTENDANCE
# =========================================================

elif page == "Attendance":

    st.header("🟢 Automatic Attendance")

    attendance = get_today_attendance()

    if attendance:

        for record in attendance:

            st.success(
                f"✅ {record[1]} "
                f"({record[0]}) — "
                f"Present at {record[3]}"
            )

    else:

        st.warning(
            "No attendance recorded today."
        )


# =========================================================
# ENTRY / EXIT
# =========================================================

elif page == "Entry Exit":

    st.header("🚪 Student Entry / Exit Tracking")

    st.write(
        "Today's student movement records."
    )

    movements = get_today_movements()

    if movements:

        for movement in movements:

            student_id = movement[0]
            name = movement[1]
            entry_time = movement[2]
            exit_time = movement[3]

            if exit_time:

                st.write(
                    f"🟢 **{name}** ({student_id}) — "
                    f"Entry: **{entry_time}** | "
                    f"Exit: **{exit_time}**"
                )

            else:

                st.write(
                    f"🟢 **{name}** ({student_id}) — "
                    f"Entry: **{entry_time}** | "
                    f"Still inside"
                )

    else:

        st.info(
            "No entry/exit records today."
        )


# =========================================================
# RECOGNITION DEMO
# =========================================================

elif page == "Recognition Demo":

    st.header("🧠 Face Recognition Demo")

    st.write(
        "This public demo simulates the result of "
        "the local AI face-recognition system."
    )

    students = get_students()

    if not students:

        st.warning(
            "Register a student first."
        )

    else:

        options = {
            f"{student[0]} — {student[1]} — Class {student[2]}":
            student[0]
            for student in students
        }

        selected = st.selectbox(
            "Select recognized student",
            list(options.keys())
        )

        selected_id = options[selected]

        if st.button(
            "🧠 Simulate Face Recognition",
            type="primary"
        ):

            student = next(
                (
                    s for s in students
                    if s[0] == selected_id
                ),
                None
            )

            if student:

                st.success(
                    f"✅ Face matched: "
                    f"{student[1]} ({student[0]})"
                )

                attendance_marked = mark_attendance(
                    selected_id
                )

                if attendance_marked:

                    st.success(
                        "🟢 Attendance marked Present!"
                    )

                else:

                    st.info(
                        "ℹ️ Attendance was already "
                        "marked today."
                    )

                movement_type, movement_time = (
                    record_entry_exit(selected_id)
                )

                if movement_type == "ENTRY":

                    st.success(
                        f"🟢 ENTRY recorded at "
                        f"{movement_time}"
                    )

                else:

                    st.warning(
                        f"🔴 EXIT recorded at "
                        f"{movement_time}"
                    )
