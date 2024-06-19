import streamlit as st
import os
from typing import Dict
import pandas as pd
from langchain_community.tools.pubmed.tool import PubmedQueryRun
from langchain_community.retrievers import PubMedRetriever
import pprint

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


def visualiza(docs: str):
    """
    Visualize prompt
    Args:
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
    """
    title = st.session_state["select_box"]
    for d in docs:
        if d.metadata["Title"] == title:
            texto = d.page_content
            metadata = d.metadata
            break

    txt1 = st.text_area("resultado pubmed", height=300, key="pubmed_box", value=texto)
    txt2 = st.text_area("Metadata", height=150, key="pubmed_box_2", value=metadata)


if "search_done" not in st.session_state:
    st.session_state["search_done"] = "start"
if "docs" not in st.session_state:
    st.session_state["docs"] = []


page_select = st.text_input(
    "Introduce tema a buscar en pubmed 👇",
    key="page_select",
    placeholder="Introduce tema a buscar en pubmed luego una coma y el numero de documentos que quieres traer. Solo puede haber una coma en este input",
)
if page_select:
    tema = page_select.split(",")[0].strip()
    top_k_results = page_select.split(",")[-1].strip()

    if st.session_state["search_done"] != page_select:
        retriever = PubMedRetriever(
            verbose=True, kwargs={"top_k_results": int(top_k_results)}
        )
        st.session_state["docs"] = retriever.invoke(tema)
        st.session_state["search_done"] = page_select
    onlyfiles = [f.metadata["Title"] for f in st.session_state["docs"]]

    option = st.selectbox(
        "select prompt",
        onlyfiles,
        on_change=visualiza,
        args=[st.session_state["docs"]],
        key="select_box",
    )
