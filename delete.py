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

#### OPEN all necesary Tables
# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(ROOT_DIR)
# open table with all prompts
fname, fname2, df_prompts = open_table_prompts(PROMPTS_DIR)
# open periciales table
DATA_DIR = os.path.join(ROOT_DIR, "pericial", "table")
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


def main(options, embeddings, index, vectorstore, placeholder):
    """
    Main function
    Argr:
        options: list of options for the select box
        embeddings: embeddings model
        index: pinecone index
        vectorstore: pinecone vectorstore
        placeholder: placeholder for the main page
    """
    if st.button("Salir"):
        placeholder.empty()
        st.stop()
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

    if "embeddings" not in st.session_state:
        st.session_state["embeddings"] = embeddings
    if "index" not in st.session_state:
        st.session_state["index"] = index
    if "vectorstore" not in st.session_state:
        st.session_state["vectorstore"] = vectorstore

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

                visualiza_delete_pericial(
                    st, df_pericial, pname, st.session_state["vectorstore"]
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
            if st.session_state["selector_selected_answer_delete_no_case"] == True:
                visualiza_delete_answer_gemini_no_case(
                    st, df_answers_no_case, pname_no_case
                )


if __name__ == "__main__":
    # configure access to table . for now we can add prompts and periciales
    options = ["Prompts", "Periciales", "Answer_gemini", "Answer_gemini_no_case"]

    # access to keys and service account
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    # Set page layout
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    placeholder_delete = st.empty()
    with placeholder_delete.container():
        config = dotenv_values(os.path.join(ROOT_DIR, "keys", ".env"))
        with open(
            os.path.join(ROOT_DIR, "keys", "complete-tube-421007-9a7c35cd44e2.json")
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
            placeholder=placeholder_delete,
        )
