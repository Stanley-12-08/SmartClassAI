import os
import sys
import pickle
import importlib.util
from pathlib import Path

import streamlit as st

from database import get_students, save_face_encoding
from attendance import mark_attendance
from tracking import record_entry_exit


# =========================================================
# LOAD THE REAL face-recognition PACKAGE
# =========================================================
# The filename of this file is also face_recognition.py,
# so we load the installed package separately.

_face_recognition_package = None


def get_face_recognition():
    global _face_recognition_package

    if _face_recognition_package is not None:
        return _face_recognition_package

    import importlib.metadata

    try:
        package_path = importlib.metadata.distribution(
            "face-recognition"
        ).locate_file("face_recognition/__init__.py")
    except Exception as error:
        raise ImportError(
            "The face-recognition package is not installed."
        ) from error

    package_path = Path(package_path)
    package_folder = package_path.parent

    spec = importlib.util.spec_from_file_location(
        "_smartclass_face_recognition",
        str(package_path),
        submodule_search_locations=[str(package_folder)]
    )

    module = importlib.util.module_from_spec(spec)

    sys.modules["_smartclass_face_recognition"] = module

    spec.loader.exec_module(module)

    _face_recognition_package = module

    return module


# =========================================================
# FACE REGISTRATION
# =========================================================

def register_face():
    face_recognition = get_face_recognition()

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
    face_recognition = get_face_recognition()

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

                movement_type, movement_time = (
                    record_entry_exit(matched_id)
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
# LIVE CAMERA
# =========================================================

def show_live_camera():

    face_recognition = get_face_recognition()

    import av
    import cv2

    from streamlit_webrtc import (
        webrtc_streamer,
        VideoProcessorBase
    )

    class FaceRecognitionProcessor(
        VideoProcessorBase
    ):

        def __init__(self):
            self.status = "Waiting for camera..."
            self.name = ""
            self.student_id = ""

        def recv(self, frame):

            image = frame.to_ndarray(
                format="rgb24"
            )

            face_locations = (
                face_recognition.face_locations(
                    image
                )
            )

            if len(face_locations) == 0:

                self.status = "No face detected"
                self.name = ""
                self.student_id = ""

            else:

                encodings = (
                    face_recognition.face_encodings(
                        image,
                        face_locations
                    )
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

                        matches = (
                            face_recognition.compare_faces(
                                known_encodings,
                                encoding,
                                tolerance=0.5
                            )
                        )

                        if True in matches:

                            index = matches.index(True)

                            matched_student = (
                                known_students[index]
                            )

                            self.student_id = (
                                matched_student[0]
                            )

                            self.name = (
                                matched_student[1]
                            )

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
# FACE REGISTRATION PAGE
# =========================================================

def show_face_registration_page():

    st.header("📸 Face Registration")

    st.write(
        "Register a test face for a student."
    )

    register_face()


# =========================================================
# FACE RECOGNITION PAGE
# =========================================================

def show_face_recognition_page():

    st.header("🧠 Face Recognition + Attendance")

    st.write(
        "Upload a test image and the system "
        "will compare it with registered faces."
    )

    recognize_uploaded_face()