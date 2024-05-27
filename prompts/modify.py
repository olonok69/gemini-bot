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


def save_text(name_prompt, prompt, keywords, prompt_dict, file):
    """
    Save text after modification
    """

    p_dict = {}
    # if name_prompt_change
    if st.session_state["name_prompt"] != prompt_dict.get("name_prompt"):
        # delete file
        remove(file, DICTS_DIR)

        name_prompt = st.session_state["name_prompt"]
        p_dict["name_prompt"] = st.session_state["name_prompt"]
    else:
        name_prompt = prompt_dict.get("name_prompt")
        p_dict["name_prompt"] = prompt_dict.get("name_prompt")

    # if prompt_change
    if st.session_state["prompt"] != prompt_dict.get("prompt"):
        p_dict["prompt"] = st.session_state["prompt"]
    else:
        p_dict["prompt"] = prompt_dict.get("prompt")
    # if keywords change
    if st.session_state["keywords"] != prompt_dict.get("keywords"):
        p_dict["keywords"] = st.session_state["keywords"]
    else:
        p_dict["keywords"] = prompt_dict.get("keywords")

    with open(os.path.join(ROOT_DIR, "dicts", name_prompt.lower() + ".json"), "w") as f:
        json.dump(p_dict, f)
    return


def visualiza():
    file = st.session_state["select_box"]
    with open(os.path.join(DICTS_DIR, file), "r") as f:
        prompt_dict = json.load(f)

    txt, txt2, txt3 = "-1", "-1", "-1"
    txt = st.text_area(
        "Introduce name of the prompt",
        value=prompt_dict.get("name_prompt"),
        key="name_prompt",
        on_change=save_text,
        args=[txt, txt2, txt3, prompt_dict, file],
    )
    txt3 = st.text_area(
        "Introduce keywords",
        value=prompt_dict.get("keywords"),
        key="keywords",
        on_change=save_text,
        args=[txt, txt2, txt3, prompt_dict, file],
    )
    txt2 = st.text_area(
        "Introduce prompt",
        height=300,
        key="prompt",
        value=prompt_dict.get("prompt"),
        on_change=save_text,
        args=[txt, txt2, txt3, prompt_dict, file],
    )


option = st.selectbox("select prompt", onlyfiles, on_change=visualiza, key="select_box")
