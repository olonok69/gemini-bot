import streamlit as st
import os


# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FOLDER = os.path.join(ROOT_DIR, "out")
TMP_FOLDER = os.path.join(ROOT_DIR, "tmp")

if "upload_state" not in st.session_state:
    st.session_state["upload_state"] = ""


def file_selector(folder_path=os.path.join(ROOT_DIR, "answers")):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox(
        "Select a file", filenames, placeholder="Select a file"
    )
    return os.path.join(folder_path, selected_filename)


filename = file_selector()
if filename:
    with open(filename, "r", encoding="utf-8") as f:
        answer = f.read()
    st.write(f"You selected `{filename}`")
    st.session_state["upload_state"] = answer

upload_state = st.text_area("Status selection", "", key="upload_state", height=400)
