import streamlit as st
import os
from typing import Dict
import pandas as pd
from langchain_community.tools.pubmed.tool import PubmedQueryRun
from langchain_community.retrievers import PubMedRetriever
import pprint

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


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
