import streamlit as st
import sqlite3
import face_recognition
import pickle
import io
from datetime import datetime

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


def save_face_encoding(student_id, encoding):
    connection = sqlite3.connect(DB_NAME)

    connection.execute("""
        UPDATE students
        SET face_encoding = ?
        WHERE student_id = ?
    """, (
        pickle.dumps(encoding),
        student_id
    ))

    connection.commit()
    connection.close()


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
        # Student already marked present today
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


# =========================
# FACE PROCESSING
# =========================

def process_face_image(image_bytes):

    image = face_recognition.load_image_file(
        io.BytesIO(image_bytes)
    )

    locations = face_recognition.face_locations(image)

    if len(locations) == 0:
        return None, "No face detected."

    if len(locations) > 1:
        return None, "More than one face detected."

    encodings = face_recognition.face_encodings(
        image,
        locations
    )

    if not encodings:
        return None, "Could not create face encoding."

    return encodings[0], "Face detected."


def recognize_student(encoding):

    students = get_students()

    known_encodings = []
    known_students = []

    for student in students:

        if student[3] is not None:

            stored_encoding = pickle.loads(student[3])

            known_encodings.append(
                stored_encoding
            )

            known_students.append(student)

    if not known_encodings:
        return None

    matches = face_recognition.compare_faces(
        known_encodings,
        encoding,
        tolerance=0.5
    )

    if True in matches:

        index = matches.index(True)

        return known_students[index]

    return None


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
    "Choose a section:",
    [
        "Dashboard",
        "Student Registration",
        "Face Registration",
        "Attendance"
    ]
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

            status = (
                "✅ Face registered"
                if student[3] is not None
                else "❌ Face not registered"
            )

            st.write(
                f"**{student[0]}** — "
                f"{student[1]} — "
                f"Class {student[2]} — "
                f"{status}"
            )

    else:

        st.info("No students registered yet.")


# =========================
# FACE REGISTRATION
# =========================

elif page == "Face Registration":

    st.header("📸 Face Registration")

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

        method = st.radio(
            "Registration method",
            [
                "🖼️ Upload Photo (Testing)",
                "📷 Camera"
            ]
        )

        if method == "🖼️ Upload Photo (Testing)":

            st.warning(
                "Testing only. An uploaded image does "
                "not prove that a person is physically present."
            )

            uploaded = st.file_uploader(
                "Upload one-face image",
                type=["jpg", "jpeg", "png"]
            )

            if uploaded:

                image_bytes = uploaded.getvalue()

                st.image(
                    image_bytes,
                    width=350
                )

                if st.button("🧠 Create Face Data"):

                    encoding, message = process_face_image(
                        image_bytes
                    )

                    if encoding is None:

                        st.error(message)

                    else:

                        save_face_encoding(
                            selected_id,
                            encoding
                        )

                        st.success(
                            "Face data saved successfully! 🎉"
                        )

        else:

            st.info(
                "Camera mode is ready for when a camera "
                "is connected."
            )

            camera_photo = st.camera_input(
                "Take a face photograph"
            )

            if camera_photo:

                image_bytes = camera_photo.getvalue()

                st.image(
                    image_bytes,
                    width=350
                )

                if st.button(
                    "🧠 Save Camera Face"
                ):

                    encoding, message = process_face_image(
                        image_bytes
                    )

                    if encoding is None:

                        st.error(message)

                    else:

                        save_face_encoding(
                            selected_id,
                            encoding
                        )

                        st.success(
                            "Camera face data saved! 🎉"
                        )


# =========================
# ATTENDANCE
# =========================

elif page == "Attendance":

    st.header("🟢 Automatic Attendance")

    st.info(
        "The live-camera attendance engine will be "
        "connected here. It will continuously recognize "
        "registered students and record attendance once "
        "per day."
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
        "Face recognition is ready. "
        "The next hardware step is connecting a live camera."
    )