import streamlit as st
import json
import os
import uuid

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DICTS_DIR = os.path.join(ROOT_DIR, "dicts")
os.makedirs(DICTS_DIR, exist_ok=True)


def save_text(name_prompt, prompt, keywords):
    p_dict = {}
    p_dict["id"] = str(uuid.uuid4())
    p_dict["name_prompt"] = name_prompt
    p_dict["prompt"] = prompt
    p_dict["keywords"] = keywords.replace(" ", "")

    with open(os.path.join(ROOT_DIR, "dicts", name_prompt.lower() + ".json"), "w") as f:
        json.dump(p_dict, f)


txt = st.text_area("Introduce name of the prompt", key="name_prompt")
txt3 = st.text_area(
    "Introduce keywords",
    placeholder="introduce palabras clave separadas por una coma. Ejemplo: informe,revision",
    key="keywords",
)
txt2 = st.text_area("Introduce prompt", height=300, key="prompt")

st.button(
    "Save",
    type="primary",
    key="save_button",
    on_click=save_text,
    args=[txt, txt2, txt3],
)
