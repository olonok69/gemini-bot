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
from src.maintenance import (
    selected_modifica,
    visualiza_modify_prompt,
    selected_modify_prompt,
    selected_modify_percial,
    visualiza_pericial_modifica,
)
import logging
from src.utils import print_stack
from src.maps import config as conf, init_session_num, reset_session_num

# Read all Dataframe need in this page
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
logging.info(f"DATA DIR: {DATA_DIR}")
pname, name2, df_pericial = open_table_periciales(DATA_DIR)
# all names of the prompts
onlyfiles_prompts = df_prompts["name_prompt"].to_list()
# all names of the perciales
onlyfiles_periciales = df_pericial["Title"].to_list()

def change_state_12(session, placeholder):
    """
    change state after leave conversation
    params:
    st (streamlit): streamlit object
    placeholder (streamlit.empty): placeholder

    """
    placeholder.empty()
    del placeholder
    reset_session_num(session,"12")
    st.stop()
    return

def main(options, placeholder):
    """
    Main function
    Argr:
        options: list of options for the select box
        embeddings: embeddings model
        index: pinecone index
        vectorstore: pinecone vectorstore
        placeholder: placeholder for the streamlit app
    """
    if st.button("Salir", on_click=change_state_12, args=(st, placeholder)):
        logging.info("Salir and writing history")
    col1, col2 = 50, 50
    if "init_run_12" not in st.session_state:
            st.session_state["init_run_12"] = False
    if st.session_state["init_run_12"] == False:
        init_session_num(st, ss, "12", col1, col2, conf["12"]["config_12"], None)



    if "selector_selected_pericial_12" not in st.session_state:
        st.session_state["selector_selected_pericial_12"] = False

    try:
        # select which type of document to modify
        selector1 = st.selectbox(
            "Select type of document to modify. Pericial or Prompt to extract Information from document 👇",
            options,
            index=None,
            on_change=selected_modifica,
            args=[st, "12"],
            key="select_box_modifica_12",
        )
        if st.session_state["selector_selected_modifica_12"] == True:
            if st.session_state.select_box_modifica_12 == "Prompts":
                # fname, fname2, df_prompts
                option = st.selectbox(
                    "select prompt 👇",
                    onlyfiles_prompts,
                    on_change=selected_modify_prompt,
                    key="select_box_modifica_prompt_12",
                    args=[st, "12"],
                )
                if st.session_state["selector_selected_section_12"] == True:
                    logging.info("Selected visualiza Prompt")
                    visualiza_modify_prompt(st, df_prompts, fname, num="12")

            elif st.session_state.select_box_modifica_12 == "Periciales":
                # pname, name2, df_pericial
                option_pericial = st.selectbox(
                    "select pericial 👇",
                    onlyfiles_periciales,
                    on_change=selected_modify_percial,
                    args=[st, "12"],
                    key="select_box_modifica_pericial_12",
                )
                if st.session_state["selector_selected_pericial_12"] == True:
                    # df_pericial, pname, st.session_state["vectorstore"]
                    logging.info("Selected visualiza Pericial")
                    visualiza_pericial_modifica(
                        st, df_pericial, pname, st.session_state["vectorstore_12"], num="12"
                    )
    except :
        st.session_state["salir_12"] = True
        placeholder.empty()
        text = print_stack()
        text = "Menu 12 Modify " + text
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

    if "salir_12" not in st.session_state:
        st.session_state["salir_12"] = False  

    if st.session_state["salir_12"] == False:  
        placeholder_modifica = st.empty()
        with placeholder_modifica.container():
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
            if "embeddings_12" not in st.session_state:
                st.session_state["embeddings_12"] = GoogleGenerativeAIEmbeddings(model=MODEL)
            logging.info(f"Embeddings {MODEL} loaded")
            # Index Pinecone
            pc = Pinecone(api_key=config.get("PINECONE_API_KEY"))
            INDEX_NAME = "forensic"
            if "index_12" not in st.session_state:
                st.session_state["index_12"] = pc.Index(INDEX_NAME)
            if "vectorstore_12" not in st.session_state:
                st.session_state["vectorstore_12"] = PineconeVectorStore(embedding=st.session_state["embeddings_12"], index_name=INDEX_NAME)
            logging.info(f"Pinecone Vectore Store with index {INDEX_NAME} loaded")
            # call to main
            main(
                options=options,
                placeholder=placeholder_modifica,
            )
