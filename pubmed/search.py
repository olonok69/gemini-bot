import streamlit as st
import os
from typing import Dict

from langchain_community.tools.pubmed.tool import PubmedQueryRun


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
tool = PubmedQueryRun(verbose=True)


def visualiza(d: str):
    """
    Visualize prompt
    Args:
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
    """

    txt2 = st.text_area("resultado pubmed", height=300, key="pubmed_box", value=d)


page_select = st.text_input(
    "Introduce tema a buscar en pubmed 👇",
    key="page_select",
    placeholder="Introduce tema a buscar en pubmed",
)
if page_select:
    d = tool.invoke(page_select)
    visualiza(d)
