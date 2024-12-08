import streamlit as st
from streamlit import session_state as ss
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
import logging
from src.utils import print_stack
from src.maps import config as conf, init_session_num, reset_session_num
# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT_DIR)
PROJECT_DIR = path.parent.absolute().as_posix()
logging.info(f"PROJECT DIR: {PROJECT_DIR}, this folder: {ROOT_DIR}")

# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(PROJECT_DIR)
# open table with all prompts
fname, fname2, df_prompts = open_table_prompts(PROMPTS_DIR)
# open periciales table
DATA_DIR = os.path.join(PROJECT_DIR, "pericial", "table")
pname, name2, df_pericial = open_table_periciales(DATA_DIR)
logging.info(f"DATA DIR: {DATA_DIR}")

def change_state_10(session, placeholder):
    """
    change state after leave conversation
    params:
    st (streamlit): streamlit object
    placeholder (streamlit.empty): placeholder

    """
    placeholder.empty()
    del placeholder
    reset_session_num(session,"10")
    st.stop()
    return



def main(options,  placeholder):
    """
    Main function
    Argr:
        options: list of options for the select box
        placeholder: placeholder for the app
    """
    col1, col2 = 50, 50
    if "init_run_10" not in st.session_state:
            st.session_state["init_run_10"] = False
    if st.session_state["init_run_10"] == False:
        init_session_num(st, ss, "10", col1, col2, conf["10"]["config_10"], None)

    if st.button("Salir", on_click=change_state_10, args=(st, placeholder)):
        logging.info("Salir and writing history")


    try:
        _ = st.selectbox(
            "Select type of document to add. Pericial or Prompt to extract Information from document 👇",
            options,
            index=None,
            on_change=selected_add,
            args=[st, "10"],
            key="select_box_add_10",
        )
        if st.session_state["selector_selected_add_10"] == True:
            if st.session_state.select_box_add_10 == "Prompts":
                # fname, fname2, df_prompts
                visualiza_add_prompt(st, df_prompts, fname, num="10")
            elif st.session_state.select_box_add_10 == "Periciales":
                # pname, name2, df_pericial
                visualiza_add_pericial(st, df_pericial, pname, secciones, num="10")
    except :
        st.session_state["salir_10"] = True
        placeholder.empty()
        text = print_stack()
        text = "Menu 10 Add " + text
        logging.error(text)

if __name__ == "__main__":
    # configure access to table . for now we can add prompts and periciales
    options = ["Prompts", "Periciales"]
    # access to keys and service account
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    PROJECT_DIR = path.parent.absolute().as_posix()
    # Set page layout
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    #go to login page if not authenticated
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "main.py"
        st.switch_page("main.py")

    if "salir_10" not in st.session_state:
        st.session_state["salir_10"] = False  
    if st.session_state["salir_10"] == False:    
        placeholder_add = st.empty()
        with placeholder_add.container():
            config = dotenv_values(os.path.join(PROJECT_DIR, "keys", ".env"))
            with open(
                os.path.join(PROJECT_DIR, "keys", "complete-tube-421007-208a4862c992.json")
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
            if "GEMINI_API_KEY" not in os.environ:
                os.environ["GEMINI_API_KEY"] = config.get("GEMINI-API-KEY")
            if "GOOGLE_API_KEY" not in os.environ:
                os.environ["GOOGLE_API_KEY"] = config.get("GEMINI-API-KEY")
            if "PINECONE_API_KEY" not in os.environ:
                os.environ["PINECONE_API_KEY"] = config.get("PINECONE_API_KEY")
            if "PINECONE_INDEX_NAME" not in os.environ:
                os.environ["PINECONE_INDEX_NAME"] = "forensic"

            # configure embeddings and Pinecone vectorstore
            MODEL="models/text-embedding-004"
            if "embeddings_10" not in st.session_state:
                st.session_state["embeddings_10"] = GoogleGenerativeAIEmbeddings(model=MODEL)
            logging.info(f"Embeddings {MODEL} loaded")
            pc = Pinecone(api_key=config.get("PINECONE_API_KEY"))
            INDEX_NAME = "forensic"
            if "index_10" not in st.session_state:
                st.session_state["index_10"] = pc.Index(INDEX_NAME)
            if "vectorstore_10" not in st.session_state:
                st.session_state["vectorstore_10"] = PineconeVectorStore(embedding=st.session_state["embeddings_10"], index_name= INDEX_NAME)
            logging.info(f"Pinecone Vectore Store with index {INDEX_NAME} loaded")
            # call to main
            main(
                options=options,
                placeholder=placeholder_add,
            )
