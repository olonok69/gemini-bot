import streamlit as st
from streamlit import session_state as ss
import os.path
from pathlib import Path
from streamlit_pdf_viewer import pdf_viewer
from streamlit import session_state as ss
from src.pdf_utils import count_pdf_pages
from google.oauth2 import service_account
from langchain_community.vectorstores import FAISS
import vertexai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import dotenv_values
import json
from src.helpers import (
    reset_session_add_kb,
    init_session_add_kb,
)
from src.utils import create_client_logging, print_stack
from kb.utils import (
    load_file,
    get_docs_to_add_vectorstore_faiss,
    add_new_documents_to_faiss,
)
from src.utils import print_stack
import logging
from src.maps import config as conf, init_session_num, reset_session_num
from src.work_gemini import init_llm, init_google_embeddings
import time
from src.files import (
    open_table_answers,
    create_folders,
    open_table_prompts,
)

# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT_DIR)
PROJECT_DIR = path.parent.absolute().as_posix()
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(PROJECT_DIR)

secciones = ["legal", "medicine", "engineering", "science", "procedures", "other"]


def selected(st):
    st.session_state["file_prompt_selected"] = True


def reload_add_doc_kb(st, ss, placeholder):
    """
    reload page
    params:
    st (streamlit): streamlit object
    ss (streamlit.session_state): streamlit session state
    model (vertexai.generative_models.GenerativeModel): model
    df_answers (pd.DataFrame): dataframe with all answers

    """
    # delete files

    reset_session_add_kb(st, ss)
    files = [f.unlink() for f in Path(f"{TMP_FOLDER}").glob("*") if f.is_file()]
    files = [f.unlink() for f in Path(f"{OUT_FOLDER}").glob("*") if f.is_file()]

    placeholder.empty()
    st.stop()
    return


def selected_seccion_add_kb(st, num: int):
    st.session_state[f"add_file_kb_selected_{num}"] = True

def change_state_33(session, placeholder):
    """
    change state after leave conversation
    params:
    st (streamlit): streamlit object
    placeholder (streamlit.empty): placeholder

    """
    placeholder.empty()
    del placeholder
    reset_session_num(session,"32")
    st.stop()
    return

def main( path_faiss, placeholder):
    """
    main loop
    params:
    vectorstore (FAISS): vectorstore
    path_faiss (str): path to faiss file
    placeholder (streamlit.empty): placeholder
    """

    try:
        # Initialize Vars
        # Initialice state
        if "init_run_32" not in st.session_state:
            st.session_state["init_run_32"] = False
        if st.session_state["init_run_32"] == False:
            init_session_num(st, ss, "32", col1, col2, conf["32"]["config_32"], None)

        # if you press salir any time you close the conainer
        if st.button("Salir", on_click=change_state_32, args=(st, placeholder)):
            logging.info("Salir and writing history")

        # Access the uploaded ref via a key.
        if st.session_state['value_32'] >= 0:
            uploaded_files = st.file_uploader(
                "Upload PDF file",
                type=("pdf"),
                key="pdf",
                accept_multiple_files=False,
            )  # accept_multiple_files=True,
            if uploaded_files:
                logging.info(f"Gemini Page 32: file uploaded {uploaded_files.name}")
            if uploaded_files:
                # To read file as bytes:
                im_bytes = uploaded_files.getvalue()
                file_path = f"{TMP_FOLDER}/{uploaded_files.name}"
                with open(file_path, "wb") as f:
                    f.write(im_bytes)
                    f.close()
                if ss.pdf:
                    ss.pdf_ref_32 = im_bytes
                numpages = count_pdf_pages(file_path)
                st.session_state[f"file_name_32"] = file_path
                st.session_state[f"file_history_32"] = uploaded_files.name
                st.session_state[f"upload_state_32"] = (
                    f"Numero de paginas del fichero {uploaded_files.name} : {numpages}"
                )
            st.session_state['value_32'] = 1  # file uploaded

        # Now you can access "pdf_ref" anywhere in your app.
        if ss.pdf_ref_32:

            if st.session_state['value_32'] >= 1:
                binary_data = ss.pdf_ref

                pdf_viewer(input=binary_data, width=700, height=300)
                # logging.info(f"Gemini 1 Page: pdf viewer {uploaded_files.name}")
                _ = st.selectbox(
                    "Choose category 👇",
                    key="selectbox_category_32",
                    index=None,
                    options=secciones,
                    on_change=selected_seccion_add_kb,
                    args=[st, "32"],
                )
                if st.session_state[f"add_file_kb_selected_32"]:

                    # load the pdf and split in Langchain Documents. 1 per pages
                    if len(st.session_state["pages_32"]) == 0:
                        st.session_state["pages_32"] = load_file(
                            st.session_state["file_name_32"]
                        )
                        pages = st.session_state["pages_32"]
                        #  get embeddings, ids and text to add to vectorestore
                        documents, ids, metadatas = get_docs_to_add_vectorstore_faiss(
                            pages=pages,
                            file=st.session_state["file_history_32"],
                            category=st.session_state["selectbox_category_32"],
                        )
                        st.session_state["documents_32"] = documents
                        st.session_state["ids_32"] = ids
                        st.session_state["metadatas_32"] = metadatas
                    else:
                        pages = st.session_state["pages_32"]
                        documents = st.session_state["documents_32"]
                        ids = st.session_state["ids_32"]
                        metadatas = st.session_state["metadatas_32"]
                    #  get embeddings, ids and text to add to vectorestore

                    if st.button("Add to vectorstore"):
                        # add documents to contentstore
                        st.session_state["add_file_kb_selected_32"] = False
                        num_documents = len(documents)
                        vector_store_length_before = st.session_state[
                            "faiss_vectorstore_32"
                        ].index.ntotal
                        vector_store_length_after = add_new_documents_to_faiss(
                            st, documents, ids, metadatas
                        )
                        print(
                            f"Vectorstore length before: {vector_store_length_before}"
                        )
                        print(f"Vectorstore length after: {vector_store_length_after}")
                        print(f"Number of documents added: {num_documents}")
                        # if length after add = length before + len documents then seraialize database again
                        if (
                            vector_store_length_after
                            == vector_store_length_before + num_documents
                        ):
                            st.session_state["faiss_vectorstore_32"].save_local(
                                path_faiss, index_name="forensic"
                            )
                            texto = (
                                f"Documents added to vectorstore: {num_documents}"
                                + "\n"
                                + f"Length vector Store {vector_store_length_after}"
                            )
                            st.text_area("Status adding to Knowledge Base", value=texto)
                            time.sleep(15)
                        else:
                            st.error("Error adding documents to vectorstore")
                        # clear container
                        reload_add_doc_kb(st, ss, placeholder)

    except:
        # get the sys stack and log to gcloud
        placeholder.empty()
        text = print_stack()
        text = "Gemini add doc kb " + text
        logging.error(text)
    return


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    PROJECT_DIR = path.parent.absolute()
    DOCS_DIR = os.path.join(PROJECT_DIR, "kb", "docs")
    logging.info(f"PROJECT DIR: {PROJECT_DIR}, this folder: {ROOT_DIR}, Documents folder: {DOCS_DIR}")

    # set layout
    st.set_page_config(layout="centered", initial_sidebar_state="collapsed")
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "main.py"
        st.switch_page("main.py")

    if "salir_32" not in st.session_state:
        st.session_state["salir_32"] = False  

    if st.session_state["salir_32"] == False:  
        placeholder_32 = st.empty()
        global col1, col2
        with placeholder_32.container():

            col1, col2 = 2, 3
            # config Session
            config = dotenv_values(os.path.join(PROJECT_DIR, "keys", ".env"))
            with open(
                os.path.join(PROJECT_DIR, "keys", "complete-tube-421007-208a4862c992.json")
            ) as source:
                info = json.load(source)
            vertex_credentials = service_account.Credentials.from_service_account_info(info)
            vertexai.init(
                project=config["PROJECT"],
                location=config["REGION"],
                credentials=vertex_credentials,
            )
            google_api_key = config["GEMINI-API-KEY"]
            os.environ["GEMINI_API_KEY"] = google_api_key
            os.environ["USER_AGENT"] = "GEMINI-BOT"

            # get gemini model
            if "llm_32" not in st.session_state:
                st.session_state["llm_32"]  = init_llm(model=config.get('MODEL'), credentials=vertex_credentials) 
                logging.info(f"Model loaded: {config.get('MODEL')}")
            # get embeddings model
            if "embeddings_32" not in st.session_state:
                st.session_state["embeddings_32"] = init_google_embeddings(config=config, credentials=vertex_credentials, google_api_key=google_api_key)
                logging.info(f"Embeddings loaded: {config.get('EMBEDDINGS2')}")
            # Vectorstore
            if "vectorstore_32" not in st.session_state:
                path_faiss = os.path.join(PROJECT_DIR, "kb","faiss")
                st.session_state["vectorstore_32"] = FAISS.load_local(
                    folder_path=path_faiss,
                    embeddings=st.session_state["embeddings_32"],
                    index_name="forensic",
                    allow_dangerous_deserialization=True,
                )
                logging.info(f"Gemini Page 32: Embeddings {config.get('EMBEDDINGS2')} and Vector Store faiss loaded from {path_faiss}")
            # Initialize

            main(
                path_faiss=path_faiss,
                placeholder=placeholder_32,
            )
