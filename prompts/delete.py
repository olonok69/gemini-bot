import streamlit as st
import os
import json
from os import listdir
from os.path import isfile, join
from prompts.utils import remove

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DICTS_DIR = os.path.join(ROOT_DIR, "dicts")
os.makedirs(DICTS_DIR, exist_ok=True)


onlyfiles = [f for f in listdir(DICTS_DIR) if isfile(join(DICTS_DIR, f))]


def visualiza():
    file = st.session_state["select_box"]
    with open(os.path.join(DICTS_DIR, file), "r") as f:
        prompt_dict = json.load(f)

    txt, txt2, txt3 = "-1", "-1", "-1"
    txt = st.text_area(
        "Introduce name of the prompt",
        value=prompt_dict.get("name_prompt"),
        key="name_prompt",
    )
    txt3 = st.text_area(
        "Introduce keywords",
        value=prompt_dict.get("keywords"),
        key="keywords",
    )
    txt2 = st.text_area(
        "Introduce prompt",
        height=300,
        key="prompt",
        value=prompt_dict.get("prompt"),
    )
    st.button(
        "Delete",
        type="primary",
        key="save_button",
        on_click=remove,
        args=[file, DICTS_DIR],
    )


option = st.selectbox("select prompt", onlyfiles, on_change=visualiza, key="select_box")
