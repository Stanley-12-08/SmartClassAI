import os
import sys
import pickle
import importlib.util
from pathlib import Path

import streamlit as st
import cv2
import numpy as np
from PIL import Image

from database import get_students, save_face_encoding
from attendance import mark_attendance
from tracking import record_entry_exit


# =========================================================
# LOAD THE REAL face-recognition PACKAGE
# =========================================================

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
# FACE REGISTRATION PAGE (Database Connected)
# =========================================================

def show_face_registration_page():
    face_recognition = get_face_recognition()

    st.markdown("## Biometric Enrollment Portal")
    st.markdown("<p style='color: #64748b;'>Configure facial vector mapping via live optical capture or secure file upload.</p>", unsafe_allow_html=True)

    students = get_students()

    if not students:
        st.warning("System Notice: No registered students found. Register student profiles before capturing biometrics.")
        return

    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
        st.subheader("Enrollment Parameters")

        options = {
            f"{student[1]} ({student[0]})": student[0]
            for student in students
        }

        selected_display = st.selectbox("Select Target Student", list(options.keys()))
        selected_id = options[selected_display]

        capture_mode = st.radio("Acquisition Mode", ["Live Optical Capture", "Secure File Upload"])

        registered_image = None

        if capture_mode == "Live Optical Capture":
            camera_photo = st.camera_input("Optical Shutter Feed")
            if camera_photo is not None:
                registered_image = Image.open(camera_photo)
                st.success("Optical frame captured successfully.")
        else:
            uploaded_file = st.file_uploader("Upload Portrait Asset", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                registered_image = Image.open(uploaded_file)
                st.success("Target asset ingested successfully.")

        if st.button("Commit Biometric Record"):
            if registered_image is not None:
                try:
                    with st.spinner("Processing neural vector embeddings..."):
                        image_np = np.array(registered_image)
                        face_locations = face_recognition.face_locations(image_np)

                        if len(face_locations) == 0:
                            st.error("Validation Error: No distinct face detected in the asset.")
                        elif len(face_locations) > 1:
                            st.warning("Validation Warning: Multiple faces detected. Provide a single-subject image.")
                        else:
                            encodings = face_recognition.face_encodings(image_np, face_locations)
                            if encodings:
                                save_face_encoding(selected_id, encodings[0])
                                st.success(f"Biometric encryption successfully compiled for ID: {selected_id}.")
                            else:
                                st.error("Processing Error: Failed to extract facial encoding vector.")
                except Exception as error:
                    st.error(f"System Exception: {error}")
            else:
                st.warning("Validation Error: Provide an active camera capture or portrait file.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
        st.subheader("Asset Preview")
        if registered_image:
            st.image(registered_image, use_container_width=True)
        else:
            st.info("Awaiting optical frame input buffer...")
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# FACE RECOGNITION (Upload & Verify)
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
                encoding = pickle.loads(face_encoding)
                known_encodings.append(encoding)
                known_ids.append(student_id)
            except Exception:
                pass

    if not known_encodings:
        st.warning("System Notice: No registered facial encodings available for verification.")
        return

    uploaded_image = st.file_uploader(
        "Upload Portrait for Identification",
        type=["jpg", "jpeg", "png"],
        key="recognition_upload"
    )

    if uploaded_image is None:
        st.info("Ingest a target image to initiate student identification.")
        return

    try:
        image = face_recognition.load_image_file(uploaded_image)
        locations = face_recognition.face_locations(image)
        encodings = face_recognition.face_encodings(image, locations)

        st.image(image, caption="Target Asset Ingested", width=350)

        if len(encodings) == 0:
            st.warning("Verification Notice: No face detected in target asset.")
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
                    (s for s in students if s[0] == matched_id),
                    None
                )

                attendance_marked = mark_attendance(matched_id)

                if student:
                    st.success(f"Match Confirmed: {student[1]} (ID: {student[0]})")

                if attendance_marked:
                    st.success("Attendance Status: Marked Present.")
                else:
                    st.info("Attendance Status: Record already registered for today.")

                movement_type, movement_time = record_entry_exit(matched_id)

                if movement_type == "ENTRY":
                    st.success(f"Telemetry Log: ENTRY recorded at {movement_time}")
                else:
                    st.warning(f"Telemetry Log: EXIT recorded at {movement_time}")
            else:
                st.warning("Verification Notice: Target face unrecognized in database.")

    except Exception as error:
        st.error(f"Recognition Exception: {error}")


def show_face_recognition_page():
    st.markdown("## Neural Recognition and Attendance")
    st.markdown("<p style='color: #64748b;'>Upload target imagery to verify identity and automatically log attendance telemetry.</p>", unsafe_allow_html=True)
    recognize_uploaded_face()


# =========================================================
# LIVE CAMERA
# =========================================================

def show_live_camera():
    face_recognition = get_face_recognition()

    import av
    import cv2
    from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

    class FaceRecognitionProcessor(VideoProcessorBase):
        def __init__(self):
            self.status = "Waiting for optical feed..."
            self.name = ""
            self.student_id = ""

        def recv(self, frame):
            image = frame.to_ndarray(format="rgb24")
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                self.status = "No face detected"
                self.name = ""
                self.student_id = ""
            else:
                encodings = face_recognition.face_encodings(image, face_locations)
                students = get_students()

                known_encodings = []
                known_students = []

                for student in students:
                    if student[3]:
                        try:
                            saved_encoding = pickle.loads(student[3])
                            known_encodings.append(saved_encoding)
                            known_students.append(student)
                        except Exception:
                            pass

                if not known_encodings:
                    self.status = "No registered facial data"
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
                            self.status = "Unregistered subject"
                            self.name = ""
                            self.student_id = ""

            for top, right, bottom, left in face_locations:
                cv2.rectangle(image, (left, top), (right, bottom), (79, 70, 229), 2)

            return av.VideoFrame.from_ndarray(image, format="rgb24")

    st.markdown("## Real-Time Surveillance Stream")
    st.markdown("<p style='color: #64748b;'>Continuous optical stream scanning for registered biometrics.</p>", unsafe_allow_html=True)

    ctx = webrtc_streamer(
        key="classroom-recognition",
        video_processor_factory=FaceRecognitionProcessor,
        media_stream_constraints={"video": True, "audio": False}
    )

    if ctx.video_processor:
        st.divider()
        status = ctx.video_processor.status

        if status == "MATCH":
            st.success(f"Active Match: {ctx.video_processor.name} (ID: {ctx.video_processor.student_id})")
        elif status == "Unregistered subject":
            st.warning("Security Notice: Subject detected but not registered.")
        elif status == "No face detected":
            st.info("Telemetry: No face currently visible in optical frame.")
        elif status == "No registered facial data":
            st.warning("System Notice: No database profiles available.")
        else:
            st.info(status)