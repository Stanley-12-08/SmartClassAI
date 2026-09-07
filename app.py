import face_recognition
import os
import streamlit as st
import sqlite3
import pickle
import io
from datetime import datetime
from streamlit_webrtc import webrtc_streamer

DB_NAME = "smartclass.db"


# =========================
# DATABASE
# =========================

def create_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            face_encoding BLOB,
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

    connection.commit()
    connection.close()


# =========================
# STUDENTS
# =========================

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
        SELECT student_id, name, class_name, face_encoding
        FROM students
        ORDER BY id DESC
    """).fetchall()

    connection.close()
    return students


# =========================
# ATTENDANCE
# =========================

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

def test_face_recognition():
    image_path = os.path.join("test_faces", "test_student.jpg")

    if not os.path.exists(image_path):
        st.error("Test image not found.")
        return

    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)

    st.image(image, caption="Test Image", width=350)

    if len(face_locations) == 0:
        st.warning("No face detected.")
    elif len(face_locations) > 1:
        st.warning("More than one face detected.")
    else:
        st.success("✅ One face detected successfully!")
        
# =========================
# INITIALIZE
# =========================

create_database()

st.set_page_config(
    page_title="AI Smart Classroom",
    page_icon="🏫",
    layout="wide"
)


# =========================
# HEADER
# =========================

st.title("🏫 AI Smart Classroom")
st.write("Smart Classroom Monitoring System")

st.divider()


# =========================
# NAVIGATION
# =========================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Student Registration", "Face Registration", "Attendance", "Live Camera", ""Face AI Test""]
)


# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.header("📊 Dashboard")

    students = get_students()
    attendance = get_today_attendance()

    total_students = len(students)
    present_students = len(attendance)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Students",
            total_students
        )

    with col2:
        st.metric(
            "Present Today",
            present_students
        )

    with col3:
        st.metric(
            "Alerts",
            "Coming Soon"
        )

    st.divider()

    st.subheader("Today's Attendance")

    if attendance:

        for record in attendance:
            st.write(
                f"✅ **{record[1]}** "
                f"({record[0]}) — "
                f"{record[3]}"
            )

    else:
        st.info(
            "No attendance recorded yet today."
        )


# =========================
# STUDENT REGISTRATION
# =========================

elif page == "Student Registration":

    st.header("👨‍🎓 Student Registration")

    with st.form("student_form"):

        student_id = st.text_input(
            "Student ID",
            placeholder="Example: S001"
        )

        name = st.text_input(
            "Student Name",
            placeholder="Example: Test Student"
        )

        class_name = st.text_input(
            "Class",
            placeholder="Example: 10-A"
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


# =========================
# FACE REGISTRATION
# =========================

elif page == "Face Registration":

    st.header("📸 Face Registration")

    st.info(
        "Cloud AI face-recognition is being prepared. "
        "The public website is currently running in "
        "database/demo mode."
    )

    students = get_students()

    if not students:

        st.warning(
            "Register a student first."
        )

    else:

        options = {
            f"{student[0]} — {student[1]}": student[0]
            for student in students
        }

        selected = st.selectbox(
            "Select registered student",
            list(options.keys())
        )

        selected_id = options[selected]

        st.subheader("📷 Camera Test")

        camera_photo = st.camera_input(
            "Take a test photograph"
        )

        if camera_photo:

            st.image(
                camera_photo,
                width=350
            )

            st.warning(
                "Photo captured successfully. "
                "Automatic face recognition will be "
                "connected in the next AI stage."
            )


# =========================
# ATTENDANCE
# =========================

elif page == "Attendance":

    st.header("🟢 Automatic Attendance")

    st.info(
        "The live-camera attendance engine will be "
        "connected in the next AI stage."
    )

    st.subheader("Today's Attendance")

    attendance = get_today_attendance()

    if attendance:

        for record in attendance:

            st.success(
                f"✅ {record[1]} ({record[0]}) — "
                f"Present at {record[3]}"
            )

    else:

        st.warning(
            "No students have been marked present today."
        )

    st.divider()

    st.subheader("🔧 Recognition Engine")

    st.write(
        "Status: Preparing cloud-compatible "
        "real-time recognition."
    )
elif page == "Live Camera":
    st.header("📷 Live Classroom Camera")

    st.write("Allow camera access when your browser asks.")

    webrtc_streamer(
        key="classroom-camera",
        media_stream_constraints={
            "video": True,
            "audio": False
        }
    )
elif page == "Live Camera":
    st.header("📷 Live Classroom Camera")

    st.write("Allow camera access when your browser asks.")

    webrtc_streamer(
        key="classroom-camera",
        media_stream_constraints={
            "video": True,
            "audio": False
        }
    )
