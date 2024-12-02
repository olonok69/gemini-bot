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
from src.maintenance import visualiza_add_prompt, visualiza_add_pericial, selected_add

# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(ROOT_DIR)
# open table with all prompts
fname, fname2, df_prompts = open_table_prompts(PROMPTS_DIR)
# open periciales table
DATA_DIR = os.path.join(ROOT_DIR, "pericial", "table")
pname, name2, df_pericial = open_table_periciales(DATA_DIR)


def main(options, embeddings, index, vectorstore, placeholder):
    """
    Main function
    Argr:
        options: list of options for the select box
        embeddings: embeddings model
        index: pinecone index
        vectorstore: pinecone vectorstore
        placeholder: placeholder for the app
    """
    if st.button("Salir"):
        placeholder.empty()
        st.stop()
    if "selector_selected_add" not in st.session_state:
        st.session_state["selector_selected_add"] = False
    if "embeddings" not in st.session_state:
        st.session_state["embeddings"] = embeddings
    if "index" not in st.session_state:
        st.session_state["index"] = index
    if "vectorstore" not in st.session_state:
        st.session_state["vectorstore"] = vectorstore

    _ = st.selectbox(
        "Select type of document to add. Pericial or Prompt to extract Information from document 👇",
        options,
        index=None,
        on_change=selected_add,
        args=[st],
        key="select_box_add",
    )
    if st.session_state["selector_selected_add"] == True:
        if st.session_state.select_box_add == "Prompts":
            # fname, fname2, df_prompts
            visualiza_add_prompt(st, df_prompts, fname)
        elif st.session_state.select_box_add == "Periciales":
            # pname, name2, df_pericial
            visualiza_add_pericial(st, df_pericial, pname, secciones)


if __name__ == "__main__":
    # configure access to table . for now we can add prompts and periciales
    options = ["Prompts", "Periciales"]
    # access to keys and service account
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    # Set page layout
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    #go to login page if not authenticated
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "pages/home.py"
        st.switch_page("pages/home.py")
        
    placeholder_add = st.empty()
    with placeholder_add.container():
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
            placeholder=placeholder_add,
        )
