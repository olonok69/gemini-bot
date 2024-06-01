import streamlit as st
import os
from typing import Dict
import pandas as pd


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DICTS_DIR = os.path.join(ROOT_DIR, "dicts")
os.makedirs(DICTS_DIR, exist_ok=True)
DATA_DIR = os.path.join(ROOT_DIR, "table")
# create durs if does not exists
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


def save_text(fname: str, prompt_dict: Dict, df: pd.DataFrame):
    """
    Save text after modification
    Args:
        fname (str): name of the file
        prompt_dict (dict): dictionary with the new prompt
        df (pd.DataFrame): dataframe with all prompts
    """
    # get id of the prompt
    id_ = prompt_dict["id"]

    p_dict = {}
    # if name_prompt_change
    if st.session_state["name_prompt"] != prompt_dict.get("name_prompt"):

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

    p_dict["id"] = id_

    # drop the previous records
    df = df.drop(df[df["id"] == prompt_dict["id"]].index)
    row = pd.DataFrame(p_dict, index=[0])
    df = pd.concat([df, row], ignore_index=True)
    # save the new dataframe
    df.to_csv(fname, index=False)
    return


def visualiza(df: pd.DataFrame, fname: str):
    """
    Visualize prompt
    Args:
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
    """
    file = st.session_state["select_box"]

    # transform the row into a dictionary
    prompt_dict = df[df.name_prompt == file].to_dict(orient="records")[0]
    txt, txt2, txt3 = "-1", "-1", "-1"
    txt = st.text_area(
        "Introduce name of the prompt",
        value=prompt_dict.get("name_prompt"),
        key="name_prompt",
        on_change=save_text,
        args=[fname, prompt_dict, df],
    )
    txt3 = st.text_area(
        "Introduce keywords",
        value=prompt_dict.get("keywords"),
        key="keywords",
        on_change=save_text,
        args=[fname, prompt_dict, df],
    )
    txt2 = st.text_area(
        "Introduce prompt",
        height=300,
        key="prompt",
        value=prompt_dict.get("prompt"),
        on_change=save_text,
        args=[fname, prompt_dict, df],
    )


option = st.selectbox(
    "select prompt", onlyfiles, on_change=visualiza, args=[df, fname], key="select_box"
)
