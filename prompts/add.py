import streamlit as st
import json
import os
import uuid
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DICTS_DIR = os.path.join(ROOT_DIR, "dicts")
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


def save_text(
    name_prompt: str, prompt: str, keywords: str, df: pd.DataFrame, fname: str
):
    """
    Save prompt to a json file
    :param name_prompt: name of the prompt
    :param prompt: prompt
    :param keywords: keywords
    :param df: dataframe with all prompts
    """
    p_dict = {}
    p_dict["id"] = str(uuid.uuid4())
    p_dict["name_prompt"] = name_prompt.lower()
    p_dict["prompt"] = prompt
    p_dict["keywords"] = keywords.replace(" ", "")

    # check if id already exists, if not add to dataframe
    ids = df["name_prompt"].tolist()
    if p_dict["name_prompt"] in ids:
        df = df.drop(df[df["name_prompt"] == p_dict["name_prompt"]].index)
    row = pd.DataFrame(p_dict, index=[0])
    df = pd.concat([df, row], ignore_index=True)
    df.to_csv(fname, index=False)

    return


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
    args=[txt, txt2, txt3, df, fname],
)
