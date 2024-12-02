import streamlit as st
import os
from pathlib import Path
import json
from dotenv import dotenv_values
from google.oauth2 import service_account
import vertexai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from src.files import (
    create_folders,
    open_table_periciales,
    open_table_prompts,
    open_table_answers,
    open_table_answers_final,
    open_table_answers_no_case,
)
from src.helpers import reset_session_11
from src.maintenance import (
    selected_delete,
    selected_delete_prompt,
    selected_delete_percial,
    visualiza_delete_prompt,
    visualiza_delete_pericial,
    selected_delete_answer_gemini,
    visualiza_delete_answer_gemini,
    selected_delete_answer_gemini_nocase,
    visualiza_delete_answer_gemini_no_case,
)

import logging
from src.utils import print_stack

#### OPEN all necesary Tables
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
# open table with all prompts
paname, paname2, df_answers = open_table_answers(ANSWERS_DIR)
# open table answer final
pfname, pfname2, df_answers_final = open_table_answers_final(ANSWERS_DIR)
# all names of the prompts
onlyfiles_prompts = df_prompts["name_prompt"].to_list()
# all names of the perciales
onlyfiles_periciales = df_pericial["Title"].to_list()
# all responses from Gemini to use in perciales
onlyfiles_anwers_gemini = df_answers["prompt"].to_list()
onlyfiles_anwers_gemini2 = df_answers["filename"].to_list()
onlyfiles_anwers_gemini3 = df_answers["timestamp"].to_list()
onlyfiles_anwers_gemini4 = []
for x, y in zip(onlyfiles_anwers_gemini2, onlyfiles_anwers_gemini3):
    onlyfiles_anwers_gemini4.append(x + "_" + y)

# No case
pname_no_case, pname2_no_case, df_answers_no_case = open_table_answers_no_case(
    ANSWERS_DIR
)
onlyfiles_anwers_gemini2_nocase = df_answers_no_case["filename"].to_list()
onlyfiles_anwers_gemini3_nocase = df_answers_no_case["timestamp"].to_list()
onlyfiles_anwers_gemini4_nocase = []
for x, y in zip(onlyfiles_anwers_gemini2_nocase, onlyfiles_anwers_gemini3_nocase):

    onlyfiles_anwers_gemini4_nocase.append(x + "_" + y)

def change_state_11(st, placeholder):
    """
    change state after leave conversation
    params:
    st (streamlit): streamlit object
    placeholder (streamlit.empty): placeholder

    """
    placeholder.empty()
    reset_session_11(st)
    st.stop()
    del placeholder
    return

def main(options,  placeholder):
    """
    Main function
    Argr:
        options: list of options for the select box
        embeddings: embeddings model
        index: pinecone index
        vectorstore: pinecone vectorstore
        placeholder: placeholder for the main page
    """
    if st.button("Salir", on_click=change_state_11, args=(st, placeholder)):
        logging.info("Salir and writing history")
    # setup session
    if "selector_selected_delete" not in st.session_state:
        st.session_state["selector_selected_delete"] = False

    if "selector_selected_section_delete" not in st.session_state:
        st.session_state["selector_selected_section_delete"] = False

    if "selector_selected_pericial_delete" not in st.session_state:
        st.session_state["selector_selected_pericial_delete"] = False

    if "selector_selected_answer_delete" not in st.session_state:
        st.session_state["selector_selected_answer_delete"] = False

    if "selector_selected_answer_delete_no_case" not in st.session_state:
        st.session_state["selector_selected_answer_delete_no_case"] = False

    try:
        selector1 = st.selectbox(
            "Select type of document to delete. Pericial or Prompt 👇",
            options,
            index=None,
            on_change=selected_delete,
            args=[st],
            key="select_box_delete",
        )
        if st.session_state["selector_selected_delete"] == True:
            if st.session_state.select_box_delete == "Prompts":
                # fname, fname2, df_prompts
                _ = st.selectbox(
                    "select prompt 👇",
                    onlyfiles_prompts,
                    on_change=selected_delete_prompt,
                    key="select_box_delete_prompt",
                    args=[st],
                )
                logging.info("Selected Delete Prompts")
                if st.session_state["selector_selected_section_delete"] == True:
                    visualiza_delete_prompt(st, df_prompts, fname)

            elif st.session_state.select_box_delete == "Periciales":
                # pname, name2, df_pericial
                _ = st.selectbox(
                    "select pericial 👇",
                    onlyfiles_periciales,
                    on_change=selected_delete_percial,
                    args=[st],
                    key="select_box_delete_pericial",
                )
                if st.session_state["selector_selected_pericial_delete"] == True:
                    # df_pericial, pname, st.session_state["vectorstore"]
                    logging.info("Selected Delete Pericial")
                    visualiza_delete_pericial(
                        st, df_pericial, pname, st.session_state["vectorstore_11"]
                    )
            elif st.session_state.select_box_delete == "Answer_gemini":
                # pname, name2, df_pericial
                _ = st.selectbox(
                    "select answer from gemini 👇",
                    onlyfiles_anwers_gemini4,
                    on_change=selected_delete_answer_gemini,
                    args=[st],
                    key="select_box_delete_answers_gemini",
                )
                logging.info("Selected Delete Answer Gemini")
                if st.session_state["selector_selected_answer_delete"] == True:
                    visualiza_delete_answer_gemini(st, df_answers, paname)

            elif st.session_state.select_box_delete == "Answer_gemini_no_case":
                # pname, name2, df_pericial
                _ = st.selectbox(
                    "select answer from gemini 👇",
                    onlyfiles_anwers_gemini4_nocase,
                    on_change=selected_delete_answer_gemini_nocase,
                    args=[st],
                    key="select_box_delete_answers_gemini_no_case",
                )
                logging.info("Selected Delete Answer Gemini No Case")
                if st.session_state["selector_selected_answer_delete_no_case"] == True:
                    visualiza_delete_answer_gemini_no_case(
                        st, df_answers_no_case, pname_no_case
                    )
    except :
        st.session_state["salir_11"] = True
        placeholder.empty()
        text = print_stack()
        text = "Menu 11 delete " + text
        logging.error(text)

if __name__ == "__main__":
    # configure access to table . for now we can add prompts and periciales
    options = ["Prompts", "Periciales", "Answer_gemini", "Answer_gemini_no_case"]

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

    if "salir_11" not in st.session_state:
        st.session_state["salir_11"] = False  

    if st.session_state["salir_11"] == False:  
        placeholder_delete = st.empty()
        with placeholder_delete.container():
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
            if "embeddings_11" not in st.session_state:
                st.session_state["embeddings_11"] = GoogleGenerativeAIEmbeddings(model=MODEL)
            logging.info(f"Embeddings {MODEL} loaded")
            # Index Pinecone
            pc = Pinecone(api_key=config.get("PINECONE_API_KEY"))
            INDEX_NAME = "forensic"
            if "index_11" not in st.session_state:
                st.session_state["index_11"] = pc.Index(INDEX_NAME)
            if "vectorstore_11" not in st.session_state:
                st.session_state["vectorstore_11"] = PineconeVectorStore(embedding=st.session_state["embeddings_11"], index_name=INDEX_NAME)
            logging.info(f"Pinecone Vectore Store with index {INDEX_NAME} loaded")
            # call to main
            main(
                options=options,
                placeholder=placeholder_delete,
            )
