import streamlit as st
import os.path
from pathlib import Path
from streamlit_pdf_viewer import pdf_viewer
from streamlit import session_state as ss
from src.pdf_utils import count_pdf_pages
from google.oauth2 import service_account
import vertexai
from dotenv import dotenv_values
import json
from src.work_gemini import get_chat_response, prepare_prompt, init_model
from src.helpers import (

    visualiza_1_prompt,
    reload_page_1_doc,
)
from src.utils import create_client_logging, print_stack
import logging
import copy
from src.files import open_table_answers, create_folders, open_table_prompts
import logging
from src.utils import print_stack
from src.maps import config as conf, init_session_num, reset_session_num
from IPython import embed

# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT_DIR)
PROJECT_DIR = path.parent.absolute().as_posix()
logging.info(f"PROJECT DIR: {PROJECT_DIR}, this folder: {ROOT_DIR}")
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(PROJECT_DIR)
# open table with all prompts
pname, pname2, df_answers = open_table_answers(ANSWERS_DIR)

# open table with all prompts
fname, fname2, df = open_table_prompts(PROMPTS_DIR)

# all names of the prompts
onlyfiles = df["name_prompt"].to_list()


def selected(st):
    st.session_state["file_prompt_selected_20"] = True


def change_state_20(session, placeholder):
    """
    change state after leave conversation
    params:
    st (streamlit): streamlit object
    placeholder (streamlit.empty): placeholder

    """
    placeholder.empty()
    del placeholder
    reset_session_num(session,"20")
    st.stop()
    return

def main( col1, col2, placeholder):
    """
    main loop
    params:
    col1 (int): size col 1
    col2 (int): size col 2
    placeholder (streamlit.empty): placeholder
    """
    # two columns

    if "vcol1doc_20" in st.session_state and "vcol2doc_20" in st.session_state:
        col1 = st.session_state["vcol1doc_20"]
        col2 = st.session_state["vcol2doc_20"]

    row1_1, row1_2 = st.columns((col1, col2))
    try:
        # Initialize Vars
        # Initialice state
        if "init_run_20" not in st.session_state:
            st.session_state["init_run_20"] = False
        if st.session_state["init_run_20"] == False:
            init_session_num(st, ss, "20", col1, col2, conf["20"]["config_20"], None)

        with row1_1:
            if st.button("Salir", on_click=change_state_20, args=(st, placeholder)):
                logging.info("Salir and writing history")

            # Access the uploaded ref via a key.
            if st.session_state['value_20'] >= 0:
                uploaded_files = st.file_uploader(
                    "Upload PDF file",
                    type=("pdf"),
                    key="pdf",
                    accept_multiple_files=False,
                    disabled=st.session_state["buttom_send_not_clicked_20"],
                )  # accept_multiple_files=True,
                if uploaded_files:
                    logging.info(f"Gemini Bot 20: file uploaded {uploaded_files.name}")
                if uploaded_files:
                    # To read file as bytes:
                    im_bytes = uploaded_files.getvalue()
                    file_path = f"{TMP_FOLDER}/{uploaded_files.name}"
                    with open(file_path, "wb") as f:
                        f.write(im_bytes)
                        f.close()
                    if ss.pdf:
                        ss.pdf_ref_20 = im_bytes
                    numpages = count_pdf_pages(file_path)
                    st.session_state["file_name_20"] = file_path
                    st.session_state["file_history_20"] = uploaded_files.name
                    st.session_state["upload_state_20"] = (
                        f"Numero de paginas del fichero {uploaded_files.name} : {numpages}"
                    )
                st.session_state['value_20'] = 1  # file uploaded

        # Now you can access "pdf_ref" anywhere in your app.
        if ss.pdf_ref_20:
            with row1_1:
                if st.session_state['value_20'] >= 1:
                    binary_data = ss.pdf_ref_20
                    if st.session_state["vcol1doc_20"] == 40:
                        width = 700
                    elif st.session_state["vcol1doc_20"] == 20:
                        width = 350
                    else:
                        width = 700
                    pdf_viewer(input=binary_data, width=width, height=400)
                    logging.info(f"Gemini Bot Page 20: pdf viewer {uploaded_files.name}")
                    page_select = st.text_input(
                        "Elige paginas a extraer 👇",
                        key="page_select",
                        placeholder="Selecciona paginas seguidas por comas. Ejemplo 1,3,4,5",
                        disabled=st.session_state["buttom_send_not_clicked_20"],
                    )
                    # if page select TODO control that page is all or a number
                    if page_select and st.session_state['value_20'] >= 1:
                        st.session_state['value_20'] = 2  # pages selected
                        st.session_state["upload_state_20"] = (
                            f"paginas seleccionadas {page_select}"
                        )
                        st.selectbox(
                            "select prompt 👇",
                            onlyfiles,
                            index=None,
                            on_change=selected,
                            args=[st],
                            key="select_box_20",
                            disabled=st.session_state["buttom_send_not_clicked_20"],
                        )
                    if (
                        st.session_state["file_prompt_selected_20"] == True
                        and st.session_state["prompt_introduced_20"] == ""
                    ):
                        visualiza_1_prompt(st, df, page_select, numpages, num="20")

                    if st.session_state[
                        "prompt_introduced_20"
                    ] != "" and st.session_state['value_20'] in [2, 3]:
                        st.session_state["upload_state_20"] = (
                            f"Instruccion introducida\n{st.session_state['prompt_introduced_20'] }"
                        )
                        st.session_state['value_20'] = 3

                    if (
                        st.session_state["buttom_send_not_clicked_20"] == True
                        and st.session_state["chat_true_20"] == "chat activo"
                    ):
                        # chat active session 5
                        st.session_state['value_20'] = 5
                        col1 = 20
                        col2 = 80
                        st.session_state["vcol1doc_20"] = 20
                        st.session_state["vcol2doc_20"] = 80
                        st.session_state["expander_20"] = False

                        logging.info(
                            f"Gemini 1 Page: Session Initialized, first prompt send, session state {st.session_state['value_20']}"
                        )
                    if st.session_state["initialized_20"] == "True":
                        st.session_state["upload_state_20"] = (
                            f"Instruccion introducida\n {st.session_state['prompt_introduced_20']}"
                        )

            with row1_2:
                with st.expander(
                    "���️Instruccion to send to Gemini 👇",
                    expanded=st.session_state["expander_20"],
                ):
                    upload_state = st.text_area(
                        "Status selection", "", key="upload_state_20", height=200
                    )
                if (
                    st.session_state['value_20'] == 3
                    and st.session_state["file_prompt_selected_20"] == True
                ):
                    if st.button(
                        "Send Promt to Gemini",
                        on_click=prepare_prompt,
                        args=[
                            st.session_state["list_images_20"],
                            st.session_state["prompt_introduced_20"],
                            page_select,
                            st,
                            "20",
                        ],
                        key="buttom_send_20",
                        disabled=st.session_state["buttom_send_not_clicked_20"],
                    ):
                        logging.info("After_click_buttom_send = True")
                        st.session_state["chat_true_20"] = "chat activo"
                        st.session_state["buttom_has_send_20"] = "buttom_Send"
                        st.session_state['value_20'] = 5
                        st.session_state["buttom_send_not_clicked_20"] = True
                        col1 = 20
                        col2 = 80
                        st.session_state["vcol1doc_20"] = 20
                        st.session_state["vcol2doc_20"] = 80
                        st.session_state["expander_20"] = False

                if st.session_state["chat_true_20"] == "chat activo":
                    logging.info(
                        f"Gemini 1 Page: Chat active session {st.session_state['value_20']}"
                    )
                    st.session_state["chat_true_20"] = "chat activo"
                    prompt = st.chat_input(
                        "Enter your questions here", disabled=not input
                    )

                    # first send to google is what we introduce in the input text
                    if prompt == "terminar":
                        logging.info(
                            f"Gemini 1 Page: Terminar Chat session {st.session_state['value_20']}"
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
                            "20",
                        )

                    else:
                        if st.session_state["initialized_20"] == "False":

                            response = get_chat_response(
                                st.session_state["llm_20"], st.session_state["prompt_20"]
                            )
                            st.session_state["chat_answers_history_20"].append(response)
                            st.session_state["user_prompt_history_20"].append(
                                st.session_state["prompt_introduced_20"]
                            )
                            st.session_state["chat_history_20"].append(
                                (st.session_state["prompt_introduced_20"], response)
                            )
                            st.session_state["initialized_20"] = "True"
                            st.session_state["buttom_send_clicked_20"] = True

                        # next sends to google we take it from chat object
                        elif st.session_state["initialized_20"] == "True":
                            prompt1 = [f"""{prompt} """]
                            # actualiza status
                            st.session_state["prompt_introduced_20"] = prompt
                            logging.info(
                                f"Gemini Bot Page 20: Session Initialized, second prompt session state {st.session_state['value_20']}"
                            )
                            response = get_chat_response(
                                st.session_state["llm_20"], prompt1
                            )
                            # actualiza buffer chat
                            st.session_state["chat_answers_history_20"].append(response)
                            st.session_state["user_prompt_history_20"].append(prompt1[0])
                            st.session_state["chat_history_20"].append(
                                (prompt1[0], response)
                            )
                            st.session_state["buttom_send_clicked_20"] = True
                            st.session_state["buttom_resfresh_clicked_20"] = True

                        # write chat in window
                        if len(st.session_state["chat_answers_history_20"]) > 0:
                            list1 = copy.deepcopy(
                                st.session_state["chat_answers_history_20"]
                            )
                            list2 = copy.deepcopy(
                                st.session_state["user_prompt_history_20"]
                            )

                            if len(st.session_state["chat_answers_history_20"]) > 1:
                                list1.reverse()

                            if len(st.session_state["user_prompt_history_20"]) > 1:
                                list2.reverse()

                            for i, j in zip(list1, list2):
                                message1 = st.chat_message("user")
                                message1.write(j)
                                message2 = st.chat_message("assistant")
                                message2.write(i)
    except:
        st.session_state["salir_20"] = True
        # get the sys stack and log to gcloud
        placeholder.empty()
        text = print_stack()
        text = "Gemini Page 20" + text
        logging.error(text)
    return


if __name__ == "__main__":
    global col1, col2

    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
   # access to keys and service account
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    PROJECT_DIR = path.parent.absolute().as_posix()
    #go to login page if not authenticated
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "main.py"
        st.switch_page("main.py")

    if "salir_20" not in st.session_state:
        st.session_state["salir_20"] = False  

    if st.session_state["salir_20"] == False:  

        placeholder_20 = st.empty()
        with placeholder_20.container():
            col1, col2 = 40, 60
            config = dotenv_values(os.path.join(PROJECT_DIR, "keys", ".env"))
            with open(
                os.path.join(PROJECT_DIR, "keys", "complete-tube-421007-208a4862c992.json")
            ) as source:
                info = json.load(source)

            vertex_credentials = service_account.Credentials.from_service_account_info(info)
            # client = create_client_logging(vertex_credentials=vertex_credentials)

            # Retrieves a Cloud Logging handler based on the environment
            # you're running in and integrates the handler with the
            # Python logging module. By default this captures all logs
            # at INFO level and higher
            # client.setup_logging()

            vertexai.init(
                project=config["PROJECT"],
                location=config["REGION"],
                credentials=vertex_credentials,
            )
            if "llm_20" not in st.session_state:
                st.session_state["llm_20"]  = init_model(config)
                st.session_state["llm_20"] = st.session_state["llm_20"].start_chat(response_validation=False)
                
            logging.info(f"Model loaded: {config.get('MODEL')}")
            main(
                col1=col1,
                col2=col2,
                placeholder=placeholder_20,
            )
