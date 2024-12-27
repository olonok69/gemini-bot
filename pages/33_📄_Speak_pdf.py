import streamlit as st
import os.path
from streamlit_pdf_viewer import pdf_viewer
from streamlit import session_state as ss
from pathlib import Path
from google.oauth2 import service_account
import vertexai
from dotenv import dotenv_values
import json
from src.files import create_folders
import logging
from src.utils import print_stack
from src.pdf_utils import count_pdf_pages
from src.maps import config as conf, init_session_num, reset_session_num
from src.work_gemini import init_google_embeddings, init_llm
from src.vector import (
    add_documents_vector_store,
)
from IPython import embed
from langchain.chains import ConversationalRetrievalChain

# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT_DIR)
PROJECT_DIR = path.parent.absolute().as_posix()
logging.info(f"PROJECT DIR: {PROJECT_DIR}, this folder: {ROOT_DIR}")
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(
    PROJECT_DIR
)


def change_state_33(session, placeholder):
    """
    change state after leave conversation
    params:
    session (streamlit): streamlit object
    placeholder (streamlit.empty): placeholder

    """
    placeholder.empty()
    del placeholder
    reset_session_num(session, "33")
    st.stop()
    return


def main(
    col1,
    col2,
    placeholder,
    config,
):
    """
    main loop
    params:

    col1 (int): size col 1
    col2 (int): size col 2
    placeholder (streamlit.empty): placeholder
    config: Configuration Dictionary
    """
    # two columns

    if "vcol1doc_33" in st.session_state and "vcol2doc_33" in st.session_state:
        col1 = st.session_state["vcol1doc_33"]
        col2 = st.session_state["vcol2doc_33"]

    row1_1, row1_2 = st.columns((col1, col2))
    try:
        # Initialize Vars
        # Initialize Vars
        with placeholder.container():
            if "init_run_33" not in st.session_state:
                st.session_state["init_run_33"] = False
            if st.session_state["init_run_33"] == False:
                init_session_num(
                    st, ss, "33", col1, col2, conf["33"]["config_33"], None
                )

            with row1_1:
                # Access the uploaded ref via a key.
                if st.session_state["value_33"] >= 0:
                    uploaded_files = st.file_uploader(
                        "Upload PDF file",
                        type=("pdf"),
                        key="pdf_33",
                        accept_multiple_files=False,
                    )  # accept_multiple_files=True,
                    if uploaded_files:
                        logging.info(
                            f"Gemini Bot Page  33 : Files Uploaded {uploaded_files.name}"
                        )
                    if uploaded_files:
                        # To read file as bytes:
                        im_bytes = uploaded_files.getvalue()
                        file_path = f"{TMP_FOLDER}/{uploaded_files.name}"
                        logging.info(
                            f"Path Temporal fichero {uploaded_files.name} : {file_path}"
                        )
                        with open(file_path, "wb") as f:
                            f.write(im_bytes)
                            f.close()
                        if ss.pdf_33:
                            ss.pdf_ref_33 = im_bytes
                        numpages = count_pdf_pages(file_path)
                        logging.info(
                            f"Numero de paginas del fichero {uploaded_files.name} : {numpages}"
                        )
                        st.session_state["file_name_33"] = file_path
                        st.session_state["file_history_33"] = uploaded_files.name
                        st.session_state["upload_state_33"] = (
                            f"Numero de paginas del fichero {uploaded_files.name} : {numpages}"
                        )

                    st.session_state["value_33"] = 1  # file uploaded

                # Now you can access "pdf_ref1" anywhere in your app.
                if ss.pdf_ref_33:
                    with row1_1:
                        if st.session_state["value_33"] >= 1:
                            binary_data = ss.pdf_ref_33
                            if st.session_state["vcol1doc_33"] == 50:
                                width = 900
                            elif st.session_state["vcol1doc_33"] == 20:
                                width = 350
                            else:
                                width = 700
                            pdf_viewer(
                                input=binary_data,
                                width=width,
                                height=400,
                                key="pdf_viewer_33",
                            )
                    if st.button("Parse pdf"):
                        if st.session_state["vectorstore_33"] == None:

                            db = add_documents_vector_store(
                                config=config,
                                session=st,
                                embeddings=st.session_state["embeddings_33"],
                                num=33,
                            )
                            st.session_state["vectorstore_33"] = db

                    if (
                        st.session_state["vectorstore_33"] != None
                        and st.session_state["salir_33"] == False
                    ):
                        st.session_state["retriever_33"] = st.session_state[
                            "vectorstore_33"
                        ].as_retriever(
                            search_kwargs={"k": int(config.get("TOP_N_RETRIEVER"))},
                        )
                        st.session_state["chat_true_33"] = "chat activo"
                    if (
                        st.session_state["retriever_33"] != None
                        and st.session_state["salir_33"] == False
                    ):
                        input_prompt = st.text_input(
                            "Introduce  query to the document paginas a extraer 👇",
                            key="pdf_query",
                        )
                        if (
                            input_prompt
                            and st.session_state["value_33"] >= 1
                            and st.session_state["salir_33"] == False
                        ):
                            st.session_state["value_33"] = 2  # pages selected
                            st.session_state["upload_state_33"] = (
                                f"Intial question to Model {input_prompt}"
                            )
                            st.session_state["prompt_introduced_33"] = (
                                f"Intial question to Model {input_prompt}"
                            )
                            st.session_state["chat_true_33"] = "chat activo"
                            chain = ConversationalRetrievalChain.from_llm(
                                st.session_state["llm_33"],
                                retriever=st.session_state["retriever_33"],
                                return_source_documents=True,
                            )

                            result = chain.invoke(
                                {
                                    "question": input_prompt,
                                    "chat_history": st.session_state["chat_history_33"],
                                }
                            )
                            st.session_state["upload_state_33"] = result["answer"]
                            # add History
                            st.session_state["chat_history_33"].append(
                                (input_prompt, result["answer"])
                            )
            with row1_2:
                if st.button("Salir", on_click=change_state_33, args=(st, placeholder)):
                    logging.info("Salir and writing history")

                with st.expander(
                    "���️ Instruccion to send to Model 👇👇",
                    expanded=st.session_state["expander_33"],
                ):
                    _ = st.text_area(
                        "Status selection", "", key="upload_state_33", height=500
                    )

    except:

        st.session_state["salir_33"] = True
        # get the sys stack and log to gcloud
        placeholder.empty()
        text = print_stack()
        text = "Gemini Page 33" + text
        logging.error(text)
    return


if __name__ == "__main__":
    global col1, col2
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    # access to keys and service account
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    PROJECT_DIR = path.parent.absolute().as_posix()
    # go to login page if not authenticated
    if (
        st.session_state["authentication_status"] == None
        or st.session_state["authentication_status"] == False
    ):
        st.session_state.runpage = "main.py"
        st.switch_page("main.py")
    if "salir_33" not in st.session_state:
        st.session_state["salir_33"] = False

    if st.session_state["salir_33"] == False:
        # Empty placeholder for session objects
        placeholder_33 = st.empty()
        with placeholder_33.container():
            col1, col2 = 50, 50
            config = dotenv_values(os.path.join(PROJECT_DIR, "keys", ".env"))
            with open(
                os.path.join(
                    PROJECT_DIR, "keys", "complete-tube-421007-208a4862c992.json"
                )
            ) as source:
                info = json.load(source)

            vertex_credentials = service_account.Credentials.from_service_account_info(
                info
            )
            google_api_key = config["GEMINI-API-KEY"]
            os.environ["GEMINI_API_KEY"] = google_api_key
            # setup rebuild Elastic Index

            vertexai.init(
                project=config["PROJECT"],
                location=config["REGION"],
                credentials=vertex_credentials,
            )
            # Initialize Model
            if "llm_33" not in st.session_state:
                st.session_state["llm_33"] = init_llm(
                    model=config.get("MODEL"), credentials=vertex_credentials
                )

            logging.info(f"Model loaded: {config.get('MODEL')}")
            # Initialize embeddings models

            if "embeddings_33" not in st.session_state:
                st.session_state["embeddings_33"] = init_google_embeddings(
                    credentials=vertex_credentials,
                    google_api_key=config["GEMINI-API-KEY"],
                    config=config,
                )
            logging.info(f"Model Embeddings: {config.get('EMBEDDINGS2')} initialized")

            main(
                col1=col1,
                col2=col2,
                placeholder=placeholder_33,
                config=config,
            )
