import streamlit as st
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
import logging
import time
from src.files import (
    open_table_answers,
    create_folders,
    open_table_prompts,
)

# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(ROOT_DIR)

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


def selected_seccion_add_kb(st):
    st.session_state["add_file_kb_selected"] = True


def main(vectorstore, path_faiss, placeholder):
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
        if "init_run_add_kb" not in st.session_state:
            st.session_state["init_run_add_kb"] = False
        if st.session_state["init_run_add_kb"] == False:
            init_session_add_kb(st, ss, vectorstore)

        if st.button("Salir"):
            placeholder.empty()
            st.stop()

        # Access the uploaded ref via a key.
        if st.session_state.value >= 0:
            uploaded_files = st.file_uploader(
                "Upload PDF file",
                type=("pdf"),
                key="pdf",
                accept_multiple_files=False,
            )  # accept_multiple_files=True,
            if uploaded_files:
                logging.info(f"Gemini 1 Page: file uploaded {uploaded_files.name}")
            if uploaded_files:
                # To read file as bytes:
                im_bytes = uploaded_files.getvalue()
                file_path = f"{TMP_FOLDER}/{uploaded_files.name}"
                with open(file_path, "wb") as f:
                    f.write(im_bytes)
                    f.close()
                if ss.pdf:
                    ss.pdf_ref = im_bytes
                numpages = count_pdf_pages(file_path)
                st.session_state["file_name"] = file_path
                st.session_state["file_history"] = uploaded_files.name
                st.session_state["upload_state"] = (
                    f"Numero de paginas del fichero {uploaded_files.name} : {numpages}"
                )
            st.session_state.value = 1  # file uploaded

        # Now you can access "pdf_ref" anywhere in your app.
        if ss.pdf_ref:

            if st.session_state.value >= 1:
                binary_data = ss.pdf_ref

                pdf_viewer(input=binary_data, width=700, height=300)
                # logging.info(f"Gemini 1 Page: pdf viewer {uploaded_files.name}")
                _ = st.selectbox(
                    "Choose category 👇",
                    key="selectbox_category",
                    index=None,
                    options=secciones,
                    on_change=selected_seccion_add_kb,
                    args=[st],
                )
                if st.session_state["add_file_kb_selected"]:

                    # load the pdf and split in Langchain Documents. 1 per pages
                    if len(st.session_state["pages"]) == 0:
                        st.session_state["pages"] = load_file(
                            st.session_state["file_name"]
                        )
                        pages = st.session_state["pages"]
                        #  get embeddings, ids and text to add to vectorestore
                        documents, ids, metadatas = get_docs_to_add_vectorstore_faiss(
                            pages=pages,
                            file=st.session_state["file_history"],
                            category=st.session_state["selectbox_category"],
                        )
                        st.session_state["documents"] = documents
                        st.session_state["ids"] = ids
                        st.session_state["metadatas"] = metadatas
                    else:
                        pages = st.session_state["pages"]
                        documents = st.session_state["documents"]
                        ids = st.session_state["ids"]
                        metadatas = st.session_state["metadatas"]
                    #  get embeddings, ids and text to add to vectorestore

                    if st.button("Add to vectorstore"):
                        # add documents to contentstore
                        st.session_state["add_file_kb_selected"] = False
                        num_documents = len(documents)
                        vector_store_length_before = st.session_state[
                            "faiss_vectorstore"
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
                            st.session_state["faiss_vectorstore"].save_local(
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

    # set layout
    st.set_page_config(layout="centered", initial_sidebar_state="collapsed")
    #go to login page if not authenticated
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "pages/home.py"
        st.switch_page("pages/home.py")
    placeholder_add_kb = st.empty()

    with placeholder_add_kb.container():

        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        path = Path(ROOT_DIR)
        path = path.parent.absolute()

        config = dotenv_values(os.path.join(path, "keys", ".env"))
        with open(
            os.path.join(path, "keys", "complete-tube-421007-208a4862c992.json")
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

        # Vectorstore
        path_faiss = os.path.join(ROOT_DIR, "faiss")
        vectorstore = FAISS.load_local(
            folder_path=path_faiss,
            embeddings=GoogleGenerativeAIEmbeddings(
                model=config.get("EMBEDDINGS2"),
                credentials=vertex_credentials,
                google_api_key=google_api_key,
            ),
            index_name="forensic",
            allow_dangerous_deserialization=True,
        )
        # Initialize

        main(
            vectorstore=vectorstore,
            path_faiss=path_faiss,
            placeholder=placeholder_add_kb,
        )
