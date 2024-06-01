import streamlit as st
import os
from prompts.utils import remove
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DICTS_DIR = os.path.join(ROOT_DIR, "dicts")
DATA_DIR = os.path.join(ROOT_DIR, "table")
os.makedirs(DICTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# open table with all prompts
fname = os.path.join(DATA_DIR, "prompts.csv")
fname2 = os.path.join(DATA_DIR, "prompts_backup.csv")

if os.path.isfile(fname):
    df = pd.read_csv(fname)
    df.to_csv(fname2, index=False)
else:
    df = pd.DataFrame(columns=["id", "name_prompt", "prompt", "keywords"])
    df.to_csv(fname, index=False)

# all names of the prompts
onlyfiles = df["name_prompt"].to_list()


def visualiza():
    """
    Visualiza prompt
    """
    file = st.session_state["select_box"]
    # transform the row into a dictionary
    prompt_dict = df[df.name_prompt == file].to_dict(orient="records")[0]
    id_ = prompt_dict["id"]

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
        args=[df, id_, fname],
    )


option = st.selectbox("select prompt", onlyfiles, on_change=visualiza, key="select_box")
