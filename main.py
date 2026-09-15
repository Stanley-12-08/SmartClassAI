import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="SmartClassAI - Futuristic Portal",
    page_icon="🛡️",
    layout="wide"
)

# Futuristic Light Theme CSS
st.markdown("""
    <style>
    /* Futuristic Light Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
        font-family: 'Rajdhani', 'Segoe UI', sans-serif;
    }
    
    /* Futuristic Sidebar (Sleek Dark Navy / Glass) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
        color: #f3f4f6;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #f3f4f6;
    }

    /* Cyberpunk / Futuristic Glass Cards */
    .futuristic-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-left: 5px solid #00dfc4;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .futuristic-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px 0 rgba(0, 223, 196, 0.15);
    }
    
    /* Futuristic Badges */
    .badge-cyber {
        background: linear-gradient(135deg, #00dfc4 0%, #009efd 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)
import streamlit as st

from database import (
    create_database,
    add_student,
    get_students,
    delete_student
)

from dashboard import show_dashboard
from attendance import show_attendance_page
from tracking import show_tracking_page


# =========================================================
# DATABASE
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

    show_dashboard()


# =========================================================
# STUDENT REGISTRATION
# =========================================================

elif page == "Student Registration":

    st.header("👨‍🎓 Student Registration")

    # -----------------------------------------------------
    # REGISTER NEW STUDENT
    # -----------------------------------------------------

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

            if (
                not student_id
                or not name
                or not class_name
            ):

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

                    st.rerun()

                else:

                    st.error(
                        "This Student ID already exists."
                    )


    st.divider()


    # -----------------------------------------------------
    # REGISTERED STUDENTS
    # -----------------------------------------------------

    st.subheader("📋 Registered Students")

    students = get_students()

    if students:

        for student in students:

            student_id = student[0]
            name = student[1]
            class_name = student[2]
            face_encoding = student[3]


            # Create two columns
            col1, col2 = st.columns([5, 1])


            # -------------------------------------------------
            # STUDENT INFORMATION
            # -------------------------------------------------

            with col1:

                face_status = (
                    "🟢 Face Registered"
                    if face_encoding
                    else "⚪ Face Not Registered"
                )

                st.write(
                    f"**{student_id}** — "
                    f"{name} — "
                    f"Class {class_name} — "
                    f"{face_status}"
                )


            # -------------------------------------------------
            # DELETE BUTTON
            # -------------------------------------------------

            with col2:

                delete_button = st.button(
                    "🗑️ Delete",
                    key=f"delete_{student_id}"
                )


                if delete_button:

                    try:

                        deleted = delete_student(
                            student_id
                        )


                        if deleted:

                            st.success(
                                f"✅ {name} and all their data "
                                f"were deleted."
                            )

                            st.rerun()

                        else:

                            st.error(
                                "❌ Student was not found."
                            )


                    except Exception as error:

                        st.error(
                            f"❌ Delete error: {error}"
                        )


    else:

        st.info(
            "No students registered yet."
        )


# =========================================================
# FACE REGISTRATION
# =========================================================

elif page == "Face Registration":

    from face_recognition import (
        show_face_registration_page
    )

    show_face_registration_page()


# =========================================================
# ATTENDANCE
# =========================================================

elif page == "Attendance":

    show_attendance_page()


# =========================================================
# ENTRY / EXIT
# =========================================================

elif page == "Entry Exit":

    show_tracking_page()


# =========================================================
# LIVE CAMERA
# =========================================================

elif page == "Live Camera":

    from face_recognition import (
        show_live_camera
    )

    show_live_camera()


# =========================================================
# FACE RECOGNITION
# =========================================================

elif page == "Face Recognition":

    from face_recognition import (
        show_face_recognition_page
    )

    show_face_recognition_page()