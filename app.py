import streamlit as st
import sqlite3
import pickle
import av
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import face_recognition

DB_NAME = "smartclass.db"


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
            class_name,
            face_encoding
        FROM students
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return students


# =========================================================
# FACE ENCODING
# =========================================================

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

    # First recognition = ENTRY
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

    # Second recognition = EXIT
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

    # After an EXIT, next recognition = new ENTRY
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
# FACE REGISTRATION
# =========================================================

def register_face():

    students = get_students()

    if not students:

        st.warning("Register a student first.")
        return

    options = {
        f"{student[0]} — {student[1]}": student[0]
        for student in students
    }

    selected = st.selectbox(
        "Select student",
        list(options.keys())
    )

    selected_id = options[selected]

    st.write(
        f"Selected Student ID: **{selected_id}**"
    )

    uploaded_image = st.file_uploader(
        "Upload the student's test face image",
        type=["jpg", "jpeg", "png"],
        key="registration_upload"
    )

    if uploaded_image is None:

        st.info(
            "Upload one image containing one face."
        )
        return

    try:

        image = face_recognition.load_image_file(
            uploaded_image
        )

        face_locations = face_recognition.face_locations(
            image
        )

        st.image(
            image,
            caption="Uploaded Test Image",
            width=350
        )

        if len(face_locations) == 0:

            st.error("❌ No face detected.")
            return

        if len(face_locations) > 1:

            st.warning(
                "⚠️ More than one face detected. "
                "Please use an image with one face."
            )
            return

        encodings = face_recognition.face_encodings(
            image,
            face_locations
        )

        if not encodings:

            st.error(
                "❌ Could not create face encoding."
            )
            return

        save_face_encoding(
            selected_id,
            encodings[0]
        )

        st.success(
            f"✅ Face registered for {selected_id}!"
        )

        st.info(
            "The face encoding has been saved "
            "in the database."
        )

    except Exception as error:

        st.error(
            f"Face registration error: {error}"
        )


# =========================================================
# FACE RECOGNITION
# =========================================================

def recognize_uploaded_face():

    students = get_students()

    known_encodings = []
    known_ids = []

    for student in students:

        student_id = student[0]
        face_encoding = student[3]

        if face_encoding:

            try:

                encoding = pickle.loads(
                    face_encoding
                )

                known_encodings.append(encoding)
                known_ids.append(student_id)

            except Exception:
                pass

    if not known_encodings:

        st.warning(
            "No registered face encodings found."
        )
        return

    uploaded_image = st.file_uploader(
        "Upload a face to identify",
        type=["jpg", "jpeg", "png"],
        key="recognition_upload"
    )

    if uploaded_image is None:

        st.info(
            "Upload an image to identify the student."
        )
        return

    try:

        image = face_recognition.load_image_file(
            uploaded_image
        )

        locations = face_recognition.face_locations(
            image
        )

        encodings = face_recognition.face_encodings(
            image,
            locations
        )

        st.image(
            image,
            caption="Recognition Image",
            width=350
        )

        if len(encodings) == 0:

            st.warning("⚠️ No face detected.")
            return

        for encoding in encodings:

            matches = face_recognition.compare_faces(
                known_encodings,
                encoding,
                tolerance=0.5
            )

            if True in matches:

                index = matches.index(True)

                matched_id = known_ids[index]

                student = next(
                    (
                        s for s in students
                        if s[0] == matched_id
                    ),
                    None
                )

                # -------------------------
                # ATTENDANCE
                # -------------------------

                attendance_marked = mark_attendance(
                    matched_id
                )

                if student:

                    st.success(
                        f"✅ Face matched: "
                        f"{student[1]} ({student[0]})"
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

                # -------------------------
                # ENTRY / EXIT
                # -------------------------

                movement_type, movement_time = record_entry_exit(
                    matched_id
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

            else:

                st.warning(
                    "⚠️ Face not recognized."
                )

    except Exception as error:

        st.error(
            f"Recognition error: {error}"
        )


# =========================================================
# LIVE CAMERA PROCESSOR
# =========================================================

class FaceRecognitionProcessor(VideoProcessorBase):

    def __init__(self):

        self.status = "Waiting for camera..."
        self.name = ""
        self.student_id = ""

    def recv(self, frame):

        import cv2

        image = frame.to_ndarray(
            format="rgb24"
        )

        face_locations = face_recognition.face_locations(
            image
        )

        if len(face_locations) == 0:

            self.status = "No face detected"
            self.name = ""
            self.student_id = ""

        else:

            encodings = face_recognition.face_encodings(
                image,
                face_locations
            )

            students = get_students()

            known_encodings = []
            known_students = []

            for student in students:

                if student[3]:

                    try:

                        saved_encoding = pickle.loads(
                            student[3]
                        )

                        known_encodings.append(
                            saved_encoding
                        )

                        known_students.append(
                            student
                        )

                    except Exception:
                        pass

            if not known_encodings:

                self.status = "No registered faces"

            else:

                for encoding in encodings:

                    matches = face_recognition.compare_faces(
                        known_encodings,
                        encoding,
                        tolerance=0.5
                    )

                    if True in matches:

                        index = matches.index(True)

                        matched_student = known_students[index]

                        self.student_id = matched_student[0]
                        self.name = matched_student[1]

                        self.status = "MATCH"

                    else:

                        self.status = "Unknown face"
                        self.name = ""
                        self.student_id = ""

        for top, right, bottom, left in face_locations:

            cv2.rectangle(
                image,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                2
            )

        return av.VideoFrame.from_ndarray(
            image,
            format="rgb24"
        )


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
        "Face Registration",
        "Attendance",
        "Entry Exit",
        "Live Camera",
        "Face Recognition"
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

            face_status = (
                "🟢 Face Registered"
                if student[3]
                else "⚪ Face Not Registered"
            )

            st.write(
                f"**{student[0]}** — "
                f"{student[1]} — "
                f"Class {student[2]} — "
                f"{face_status}"
            )

    else:

        st.info(
            "No students registered yet."
        )


# =========================================================
# FACE REGISTRATION PAGE
# =========================================================

elif page == "Face Registration":

    st.header("📸 Face Registration")

    st.write(
        "Register a test face for a student."
    )

    register_face()


# =========================================================
# ATTENDANCE PAGE
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
# ENTRY / EXIT PAGE
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
# LIVE CAMERA
# =========================================================

elif page == "Live Camera":

    st.header("📷 Live Classroom Recognition")

    st.write(
        "The camera will continuously check "
        "for registered faces."
    )

    ctx = webrtc_streamer(
        key="classroom-recognition",

        video_processor_factory=FaceRecognitionProcessor,

        media_stream_constraints={
            "video": True,
            "audio": False
        }
    )

    if ctx.video_processor:

        st.divider()

        status = ctx.video_processor.status

        if status == "MATCH":

            st.success(
                f"✅ Recognized: "
                f"{ctx.video_processor.name} "
                f"({ctx.video_processor.student_id})"
            )

        elif status == "Unknown face":

            st.warning(
                "⚠️ Face detected, but student "
                "is not registered."
            )

        elif status == "No face detected":

            st.info(
                "No face currently visible."
            )

        elif status == "No registered faces":

            st.warning(
                "No student faces have been "
                "registered yet."
            )

        else:

            st.info(status)


# =========================================================
# FACE RECOGNITION
# =========================================================

elif page == "Face Recognition":

    st.header("🧠 Face Recognition + Attendance")

    st.write(
        "Upload a test image and the system "
        "will compare it with registered faces."
    )

    recognize_uploaded_face()
