import streamlit as st
import os
from pathlib import Path
import json
from dotenv import dotenv_values
from pericial.gemini_fn import secciones
from google.oauth2 import service_account
import vertexai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from src.files import (
    create_folders,
    open_table_periciales,
    open_table_prompts,
)
from src.maintenance import (
    selected_modifica,
    visualiza_modify_prompt,
    selected_modify_prompt,
    selected_modify_percial,
    visualiza_pericial_modifica,
)

# Read all Dataframe need in this page
# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(ROOT_DIR)
# open table with all prompts
fname, fname2, df_prompts = open_table_prompts(PROMPTS_DIR)
# open periciales table
DATA_DIR = os.path.join(ROOT_DIR, "pericial", "table")
pname, name2, df_pericial = open_table_periciales(DATA_DIR)
# all names of the prompts
onlyfiles_prompts = df_prompts["name_prompt"].to_list()
# all names of the perciales
onlyfiles_periciales = df_pericial["Title"].to_list()


def main(options, embeddings, index, vectorstore, placeholder):
    """
    Main function
    Argr:
        options: list of options for the select box
        embeddings: embeddings model
        index: pinecone index
        vectorstore: pinecone vectorstore
        placeholder: placeholder for the streamlit app
    """
    if st.button("Salir"):
        placeholder.empty()
        st.empty()
        st.stop()
    if "selector_selected_modifica" not in st.session_state:
        st.session_state["selector_selected_modifica"] = False
    if "selector_selected_section" not in st.session_state:
        st.session_state["selector_selected_section"] = False
    if "selector_selected_pericial" not in st.session_state:
        st.session_state["selector_selected_pericial"] = False
    if "embeddings" not in st.session_state:
        st.session_state["embeddings"] = embeddings
    if "index" not in st.session_state:
        st.session_state["index"] = index
    if "vectorstore" not in st.session_state:
        st.session_state["vectorstore"] = vectorstore

    # select which type of document to modify
    selector1 = st.selectbox(
        "Select type of document to modify. Pericial or Prompt to extract Information from document 👇",
        options,
        index=None,
        on_change=selected_modifica,
        args=[st],
        key="select_box_modifica",
    )
    if st.session_state["selector_selected_modifica"] == True:
        if st.session_state.select_box_modifica == "Prompts":
            # fname, fname2, df_prompts
            option = st.selectbox(
                "select prompt 👇",
                onlyfiles_prompts,
                on_change=selected_modify_prompt,
                key="select_box_modifica_prompt",
                args=[st],
            )
            if st.session_state["selector_selected_section"] == True:
                visualiza_modify_prompt(st, df_prompts, fname)

        elif st.session_state.select_box_modifica == "Periciales":
            # pname, name2, df_pericial
            option_pericial = st.selectbox(
                "select pericial 👇",
                onlyfiles_periciales,
                on_change=selected_modify_percial,
                args=[st],
                key="select_box_modifica_pericial",
            )
            if st.session_state["selector_selected_pericial"] == True:
                # df_pericial, pname, st.session_state["vectorstore"]
                visualiza_pericial_modifica(
                    st, df_pericial, pname, st.session_state["vectorstore"]
                )


if __name__ == "__main__":
    # configure access to table . for now we can add prompts and periciales
    options = ["Prompts", "Periciales"]

    # access to keys and service account
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    # Set page layout
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    # create container to hold all components of this page
    placeholder_modifica = st.empty()
    with placeholder_modifica.container():
        config = dotenv_values(os.path.join(ROOT_DIR, "keys", ".env"))
        with open(
            os.path.join(ROOT_DIR, "keys", "complete-tube-421007-208a4862c992.json")
        ) as source:
            info = json.load(source)
        # Initialize vertex ai
        vertex_credentials = service_account.Credentials.from_service_account_info(info)
        vertexai.init(
            project=config["PROJECT"],
            location=config["REGION"],
            credentials=vertex_credentials,
        )
        # key access gemini
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = config.get("GEMINI-API-KEY")
        if "PINECONE_API_KEY" not in os.environ:
            os.environ["PINECONE_API_KEY"] = config.get("PINECONE_API_KEY")
        if "PINECONE_INDEX_NAME" not in os.environ:
            os.environ["PINECONE_INDEX_NAME"] = "forensic"

        # configure embeddings and Pinecone vectorstore
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        pc = Pinecone(api_key=config.get("PINECONE_API_KEY"))
        index = pc.Index("forensic")
        vectorstore = PineconeVectorStore(embedding=embeddings, index_name="forensic")
        # call to main
        main(
            options=options,
            embeddings=embeddings,
            index=index,
            vectorstore=vectorstore,
            placeholder=placeholder_modifica,
        )
