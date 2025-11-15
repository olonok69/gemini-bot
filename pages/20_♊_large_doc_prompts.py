import streamlit as st
import os.path
from pathlib import Path
from vertexai.generative_models import Part
from streamlit import session_state as ss
from src.pdf_utils import count_pdf_pages
from google.oauth2 import service_account
import vertexai
from dotenv import dotenv_values
import json
from src.model import init_model
from src.utils import print_stack, upload_blob
import logging
import copy
from src.maps import config as conf, init_session_num, reset_session_num
from src.files import open_table_answers, create_folders, open_table_prompts
from src.helpers import (
    visualiza_1_prompt_no_upload,
    reload_page_1_doc,
)
from src.components.pdf_viewer import render_pdf

# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT_DIR)
PROJECT_DIR = path.parent.absolute().as_posix()
logging.info(f"PROJECT DIR: {PROJECT_DIR}, this folder: {ROOT_DIR}")
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(
    PROJECT_DIR
)
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(
    PROJECT_DIR
)
# open table with all prompts
pname, pname2, df_answers = open_table_answers(ANSWERS_DIR)


# open table with all prompts
fname, fname2, df = open_table_prompts(PROMPTS_DIR)
# all names of the prompts
onlyfiles = df["name_prompt"].to_list()


# open table with all prompts
fname, fname2, df = open_table_prompts(PROMPTS_DIR)
# all names of the prompts
onlyfiles = df["name_prompt"].to_list()


def selected(st):
    st.session_state["file_prompt_selected_200"] = True


def click_button_upload(st):
    st.session_state["file_uploaded_gcs_200"] = True


def change_state_200(session, pp):
    """
    change state after leave conversation
    params:
    st (streamlit): streamlit object
    pp (streamlit.empty): placeholder

    """
    reset_session_num(session, "200")
    pp.empty()
    del pp
    session.empty()
    session.cache_data.clear()
    session.stop()
    return


@st.dialog("Visualiza PDF 👇", width="large")
def open_pdf_dialog(binary_data, num=20, width=2000, height=1000):
    """Opens a PDF viewer in a Streamlit dialog."""
    if st.session_state.get(f"pdf_dialog_open_{num}", False):

        render_pdf(
            binary=binary_data,
            width=width,
            height=height,
            key=f"pdf_viewer_dialog_{num}",
            title="PDF preview",
        )
        if st.button("Close"):
            st.session_state[f"pdf_dialog_open_{num}"] = False
            st.rerun()  # force rerun to close the dialog.


def main(col1, col2, placeholder, bucket_name, destination_blob_folder):
    """
    main loop
    params:
    col1 (int): size col 1
    col2 (int): size col 2
    placeholder (streamlit.empty): placeholder
    """
    # two columns

    with placeholder.container():

        if "vcol1doc_200" in st.session_state and "vcol2doc_200" in st.session_state:
            col1 = st.session_state["vcol1doc_200"]
            col2 = st.session_state["vcol2doc_200"]

        row1_1, row1_2 = st.columns((col1, col2))

        try:

            # Initialize Vars
            # Initialice state
            if "init_run_200" not in st.session_state:
                st.session_state["init_run_200"] = False
            if st.session_state["init_run_200"] == False:
                init_session_num(
                    st, ss, "200", col1, col2, conf["200"]["config_200"], None
                )

            with row1_1:
                if st.button(
                    "Salir", on_click=change_state_200, args=(st, placeholder)
                ):
                    del placeholder
                    logging.info("Salir and writing history")
                uploaded_files = st.file_uploader(
                    "Upload PDF file",
                    type=("pdf"),
                    key="pdf_page_200",
                    accept_multiple_files=False,
                )  # accept_multiple_files=True,
                if uploaded_files:
                    im_bytes = uploaded_files.getvalue()
                    file_path = f"{TMP_FOLDER}/{uploaded_files.name}"
                    with open(file_path, "wb") as f:
                        f.write(im_bytes)
                        f.close()
                    if ss.pdf_page_200:
                        st.session_state["pdf_ref_200"] = im_bytes
                    numpages = count_pdf_pages(file_path)
                    st.session_state["file_name_200"] = file_path
                    st.session_state["file_history_200"] = uploaded_files.name
                    st.session_state["upload_state_200"] = (
                        f"Numero de paginas del fichero {uploaded_files.name} : {numpages}"
                    )
                    st.session_state["value_200"] = 1  # file uploaded
                    if st.button(
                        "Open PDF in Dialog",
                        disabled=st.session_state["buttom_send_not_clicked_200"],
                    ):
                        st.session_state["pdf_dialog_open_200"] = True
                        open_pdf_dialog(im_bytes, num=200)
                    if st.button(
                        "Upload PDF to GCS",
                        disabled=st.session_state["buttom_send_not_clicked_200"],
                        on_click=click_button_upload,
                        args=(st,),
                    ):
                        if st.session_state["pdf_ref_200"]:
                            # Upload the file to GCS
                            upload_blob(
                                bucket_name,
                                os.path.join(
                                    TMP_FOLDER, st.session_state["file_name_200"]
                                ),
                                os.path.join(
                                    destination_blob_folder, uploaded_files.name
                                ),
                                os.path.join(
                                    PROJECT_DIR,
                                    "keys",
                                    "complete-tube-421007-208a4862c992.json",
                                ),
                            )
                            st.session_state["upload_state_200"] = (
                                f"Fichero {uploaded_files.name} subido a GCS"
                            )
                    if (
                        st.session_state["file_uploaded_gcs_200"] == True
                        and st.session_state["value_200"] < 3
                    ):
                        st.session_state["value_200"] = 2  # pages selected

                        select_box = st.selectbox(
                            "select prompt 👇",
                            onlyfiles,
                            index=None,
                            on_change=selected,
                            args=[st],
                            key="select_box_200",
                            disabled=st.session_state["buttom_send_not_clicked_200"],
                        )

                if (
                    st.session_state["file_prompt_selected_200"] == True
                    and st.session_state["prompt_introduced_200"] == ""
                ):

                    visualiza_1_prompt_no_upload(st, df, num="200")

            with row1_2:
                with st.expander(
                    "���️Instruccion to send to Gemini 👇",
                    expanded=st.session_state["expander_200"],
                ):
                    upload_state = st.text_area(
                        "Status selection", "", key="upload_state_200", height=150
                    )
                if st.session_state["file_prompt_selected_200"] == True:
                    if st.button(
                        "Send Promt to Gemini",
                        key="buttom_send_200",
                        disabled=st.session_state["buttom_send_not_clicked_200"],
                    ):
                        logging.info("After_click_buttom_send = True")
                        st.session_state["chat_true_200"] = "chat activo"
                        st.session_state["buttom_has_send_200"] = "buttom_Send"
                        st.session_state["value_200"] = 5
                        st.session_state["buttom_send_not_clicked_200"] = False

                        st.session_state["vcol1doc_200"] = 20
                        st.session_state["vcol2doc_200"] = 80
                        st.session_state["expander_200"] = False

                    if st.session_state["chat_true_200"] == "chat activo":
                        logging.info(
                            f"Gemini 1 Page: Chat active session {st.session_state['value_200']}"
                        )
                        st.session_state["chat_true_200"] = "chat activo"
                        prompt = st.chat_input(
                            "Enter your questions here",
                            disabled=not input,
                            key="chat_input_200",
                        )
                        # first send to google is what we introduce in the input text
                        if prompt == "terminar":
                            logging.info(
                                f"Gemini 1 Page: Terminar Chat session {st.session_state['value_200']}"
                            )
                            # reload page and delete temp files

                            reload_page_1_doc(
                                st,
                                ss,
                                df_answers,
                                pname,
                                placeholder,
                                TMP_FOLDER,
                                OUT_FOLDER,
                                "200",
                            )

                        else:
                            # Add user message to chat history
                            pdf_uri = f"gs://{bucket_name}/{destination_blob_folder}/{st.session_state['file_history_200']}"
                            logging.info(f"file_path = {pdf_uri}")

                            # Create parts for the PDF and the selected prompt
                            pdf_part = Part.from_uri(
                                pdf_uri, mime_type="application/pdf"
                            )

                            if st.session_state["initialized_200"] == "False":
                                st.session_state["expander_200"] = False
                                # Use the selected prompt directly without user query
                                initial_prompt = st.session_state[f"prompt_200"]
                                text_part = Part.from_text(initial_prompt)

                                # Get response from the model using both parts
                                response = st.session_state["llm_200"].generate_content(
                                    [pdf_part, text_part]
                                )

                                st.session_state["chat_answers_history_200"].append(
                                    response.text
                                )
                                st.session_state["user_prompt_history_200"].append(
                                    st.session_state["prompt_introduced_200"]
                                )
                                st.session_state["chat_history_200"].append(
                                    (
                                        st.session_state["prompt_introduced_200"],
                                        response.text,
                                    )
                                )
                                st.session_state["initialized_200"] = "True"
                                st.session_state["buttom_send_clicked_200"] = True
                            # next sends to google we take it from chat object
                            elif st.session_state["initialized_200"] == "True":
                                conversation_history = ""
                                for user_msg, assistant_msg in st.session_state[
                                    "chat_history_200"
                                ]:
                                    conversation_history += f"User: {user_msg}\nAssistant: {assistant_msg}\n\n"

                                # Create a new prompt with conversation history
                                prompt_with_history = f"""
                                    Previous conversation:
                                    {conversation_history}

                                    New question: {prompt}
                                    """

                                # actualiza status
                                st.session_state["prompt_introduced_200"] = (
                                    prompt_with_history
                                )
                                logging.info(
                                    f"Gemini Bot Page 200: Session Initialized, second prompt session state {prompt_with_history}"
                                )
                                text_part = Part.from_text(prompt_with_history)

                                # Get response from the model using both parts
                                response = st.session_state["llm_200"].generate_content(
                                    [pdf_part, text_part]
                                )
                                # actualiza buffer chat
                                st.session_state["chat_answers_history_200"].append(
                                    response.text
                                )
                                st.session_state["user_prompt_history_200"].append(
                                    prompt
                                )
                                st.session_state["chat_history_200"].append(
                                    (prompt, response.text)
                                )
                                st.session_state["buttom_send_clicked_200"] = True
                                st.session_state["buttom_resfresh_clicked_200"] = True
                                st.session_state["expander_200"] = False

                            # write chat in window
                            if len(st.session_state["chat_answers_history_200"]) > 0:
                                list1 = copy.deepcopy(
                                    st.session_state["chat_answers_history_200"]
                                )
                                list2 = copy.deepcopy(
                                    st.session_state["user_prompt_history_200"]
                                )

                                if (
                                    len(st.session_state["chat_answers_history_200"])
                                    > 1
                                ):
                                    list1.reverse()
                                if len(st.session_state["user_prompt_history_200"]) > 1:
                                    list2.reverse()

                                for i, j in zip(list1, list2):
                                    message1 = st.chat_message("user")
                                    message1.write(j)
                                    message2 = st.chat_message("assistant")
                                    message2.write(i)

        except Exception as e:
            logging.error(f"Error: {e}")
            st.error(f"Error: {e}")
            print_stack()


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

    if "salir_200" not in st.session_state:
        st.session_state["salir_200"] = False

    if st.session_state["salir_200"] == False:

        placeholder_200 = st.empty()
        with placeholder_200.container():
            col1, col2 = 40, 60

            # Load the configuration and Initialize the Vertex AI client
            config = dotenv_values(os.path.join(PROJECT_DIR, "keys", ".env"))
            credentials_path = os.path.join(
                PROJECT_DIR, "keys", "complete-tube-421007-208a4862c992.json"
            )
            with open(credentials_path) as source:
                info = json.load(source)
            # Create a service account credentials object
            vertex_credentials = service_account.Credentials.from_service_account_info(
                info
            )
            vertexai.init(
                project=config["PROJECT"],
                location=config["REGION"],
                credentials=vertex_credentials,
            )

            if "GEMINI_API_KEY" not in os.environ:
                os.environ["GEMINI_API_KEY"] = config.get("GEMINI-API-KEY")
            if "GOOGLE_API_KEY" not in os.environ:
                os.environ["GOOGLE_API_KEY"] = config.get("GEMINI-API-KEY")
            # create the model
            if "llm_200" not in st.session_state:
                st.session_state["llm_200"] = init_model()
            bucket_name = "gemini-bot-data"  # Replace with your bucket name
            destination_blob_folder = "input"  # Replace with the desired name in the bucket (can include folders)
            main(
                col1=col1,
                col2=col2,
                placeholder=placeholder_200,
                bucket_name=bucket_name,
                destination_blob_folder=destination_blob_folder,
            )
