import streamlit as st
import os
import json
from src.files import open_table_answers, create_folders
import pandas as pd
from dotenv import dotenv_values
from google.oauth2 import service_account
import vertexai
from src.utils import create_client_logging
from src.files import file_selector, open_table_periciales
from src.helpers import visualiza_display_page, visualiza_pericial
from src.work_gemini import init_model
from pericial.gemini_fn import (
    secciones,
    get_embeddings_model,
    get_pinecone_objects,
    pericial_prompt_selected,
)
import logging

# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(ROOT_DIR)
# open table with all prompts
pname, pname2, df_answers = open_table_answers(ANSWERS_DIR)
# open periciales table
DATA_DIR = os.path.join(ROOT_DIR, "pericial", "table")
fname, fname2, df = open_table_periciales(DATA_DIR)


# fill the selector with name of the prompt and timestamp
def concat_date_row(row):
    return f"{row['filename']} - {row['timestamp']}"


df_answers["file_and_answer"] = df_answers.apply(concat_date_row, axis=1)


def selected(st):
    st.session_state["file_prompt_selected"] = True


def main(model, embeddings, index, vectorstore):
    """
    main loop
    param model: gemini model
    param embeddings: embeddings model
    param index: pinecone index
    param vectorstore: pinecone vectorstore
    """
    if "upload_state" not in st.session_state:
        st.session_state["upload_state"] = ""
    if "file_prompt_selected_visualiza" not in st.session_state:
        st.session_state["file_prompt_selected_visualiza"] = False
    if "answer_introduced" not in st.session_state:
        st.session_state["answer_introduced"] = {}
    if "file_and_answer_select_has_changed" not in st.session_state:
        st.session_state["file_and_answer_select_has_changed"] = False
    if "embeddings" not in st.session_state:
        st.session_state["embeddings"] = embeddings
    if "index" not in st.session_state:
        st.session_state["index"] = index
    if "vectorstore" not in st.session_state:
        st.session_state["vectorstore"] = vectorstore
    if "pericial_prompt_selected" not in st.session_state:
        st.session_state["pericial_prompt_selected"] = False
    if "seccion_introduced" not in st.session_state:
        st.session_state["seccion_introduced"] = ""

    selection_dict = file_selector(st, df_answers)
    if (
        len(selection_dict.keys()) >= 5
        and st.session_state["file_prompt_selected_visualiza"] == False
        and st.session_state["file_and_answer_select_has_changed"] == True
    ):

        visualiza_display_page(st=st, selection_dict=selection_dict)
    elif (
        len(selection_dict.keys()) >= 5
        and st.session_state["file_prompt_selected_visualiza"] == True
    ):
        title = st.text_area(
            "Introduce texto a Buscar Pericial separa con una # y dame el numero de documentos a buscar 👇",
            height=100,
            key="search_pericial",
            placeholder="Ejemplo: texto a buscar aqui y no puede haber este caracter--># 10",
        )

        if len(title) > 0:
            seccion = st.selectbox(
                "selecciona seccion 👇",
                secciones,
                key="select_box",
            )
            if seccion:
                numero = title.split("#")[-1].strip()
                title = title.split("#")[0].strip()
                v_query = embeddings.embed_query(title)
                r = index.query(
                    vector=list(v_query),
                    top_k=int(numero),
                    include_metadata=True,
                    filter={"sections": seccion},
                )
                if len(r["matches"]) > 0:
                    list_matches = []
                    list_matches_textos = []
                    for match in r["matches"]:

                        list_matches.append(match["id"])
                        itemlist = (
                            str(match["score"]) + ", " + match["metadata"]["text"]
                        )

                        list_matches_textos.append(itemlist)
                    seccion2 = st.selectbox(
                        "selecciona match 👇",
                        list_matches_textos,
                        key="select_box_2",
                        on_change=pericial_prompt_selected,
                        args=[st],
                    )
                    if (
                        seccion2
                        and st.session_state["pericial_prompt_selected"] == True
                    ):
                        visualiza_pericial(st, df, list_matches_textos, list_matches)


if __name__ == "__main__":
    config = dotenv_values("keys/.env")
    with open("keys/complete-tube-421007-9a7c35cd44e2.json") as source:
        info = json.load(source)

    vertex_credentials = service_account.Credentials.from_service_account_info(info)
    client = create_client_logging(vertex_credentials=vertex_credentials)
    # Retrieves a Cloud Logging handler based on the environment
    # you're running in and integrates the handler with the
    # Python logging module. By default this captures all logs
    # at INFO level and higher

    client.setup_logging()

    vertexai.init(
        project=config["PROJECT"],
        location=config["REGION"],
        credentials=vertex_credentials,
    )
    # get gemini model
    model = init_model(config)
    logging.info("Gemini display Page: Model loaded")

    # get embeddings model
    embeddings = get_embeddings_model(model_name=config.get("EMBEDDINGS"))
    # get Pinecone objects
    index, vectorstore = get_pinecone_objects(
        config=config, embeddings=embeddings, index_name="forensic"
    )
    logging.info("Gemini display Page: Embeddings and Pinecone loaded")
    main(model=model, embeddings=embeddings, index=index, vectorstore=vectorstore)
