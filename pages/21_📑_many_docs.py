import streamlit as st
import os.path
from streamlit import session_state as ss
from src.pdf_utils import count_pdf_pages, upload_files
from google.oauth2 import service_account
import vertexai
from pathlib import Path
from dotenv import dotenv_values
import json
from src.work_gemini import get_chat_response, prepare_prompt, init_model
from src.helpers import (
    reload_page_many_docs,
)
from src.utils import create_client_logging, print_stack
from src.files import open_table_answers, create_folders, open_table_answers_no_case
import copy
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
pname_no_case, pname2_no_case, df_answers_no_case = open_table_answers_no_case(
    ANSWERS_DIR
)



def change_state_21(session, pp):
    """
    change state after leave conversation
    params:
    session (streamlit): streamlit object
    pp (streamlit.empty): placeholder

    """
    reset_session_num(session,"21")
    pp.empty()
    del pp
    session.empty()
    session.stop()
    return

def main( col1, col2, placeholder):
    """
    main loop. Get Model
    Args:
        model (vertexai.generative_models.GenerativeModel): model
        col1 (int): size col 1
        col2 (int): size col 2
        placeholder (streamlit.empty): placeholder
    """
    with placeholder.container():
        if "vcol1doc_21" in st.session_state and "vcol2doc_21" in st.session_state:
            col1 = st.session_state["vcol1doc_21"]
            col2 = st.session_state["vcol2doc_21"]
        # Configure columns layout
        row1_1, row1_2 = st.columns((col1, col2))
        try:
            # Initialize Vars
            if "init_run_21" not in st.session_state:
                st.session_state["init_run_21"] = False
            if st.session_state["init_run_21"] == False:
                init_session_num(st, ss, "21", col1, col2, conf["21"]["config_21"], None)
            # Col 1 Upload file and write prompt
            with row1_1:
                # if salir kill placeholder
                if st.button("Salir", on_click=change_state_21, args=(st, placeholder)):
                    logging.info("Salir and writing history")

                # Access the uploaded ref via a key.
                if st.session_state['value_21'] >= 0:
                    uploaded_files = st.file_uploader(
                        "Upload PDF file",
                        type=("pdf"),
                        key="pdf",
                        accept_multiple_files=True,
                        disabled=st.session_state["buttom_send_not_clicked_21"],
                    )  # accept_multiple_files=True,
                    if uploaded_files:
                        logging.info(
                            f"Gemini multi Page: Files Uploaded {len(uploaded_files)}"
                        )
                    if uploaded_files:
                        # To read file as bytes:
                        for file in uploaded_files:
                            im_bytes = file.read()
                            # save file in tmp folder
                            file_path = f"{TMP_FOLDER}/{file.name}"
                            with open(file_path, "wb") as f:
                                f.write(im_bytes)
                                f.close()
                            if file.name not in st.session_state["multi_file_name_21"]:
                                st.session_state["multi_file_name_21"].append(file.name)
                                st.session_state["multi_file_pages_21"].append(
                                    count_pdf_pages(file_path)
                                )
                            if ss.pdf:
                                ss.pdf_ref_21 = im_bytes

                        texto = ""
                        # write in status Area Text
                        for i, j in zip(
                            st.session_state["multi_file_name_21"],
                            st.session_state["multi_file_pages_21"],
                        ):
                            texto = texto + f"file: {i} {j} paginas\n"
                        st.session_state["upload_state_21"] = (
                            f"Number of files uploaded {len(st.session_state['multi_file_name_21'])}\n{texto}"
                        )
                    st.session_state['value_21'] = 1  # file uploaded

            # Now you can access "pdf_ref" anywhere in your app.
            if ss.pdf_ref_21:
                with row1_1:
                    if st.session_state['value_21'] >= 1:
                        # if file uploaded
                        if len(
                            st.session_state["multi_file_name_21"]
                        ) > 0 and st.session_state['value_21'] in [1, 2, 3]:
                            st.session_state['value_21'] = 2
                            introduce_prompt = st.text_input(
                                "Introduce instruccion a mandar a gemini 👇",
                                key="introduce_prompt_21",
                                disabled=st.session_state["buttom_send_not_clicked_21"],
                            )
                            # checkbox  to decide if the answer go to case or not
                            checkbox1 = st.checkbox("Case Query")
                            if checkbox1:
                                st.session_state["case_query_21"] = True
                            else:
                                st.session_state["case_query_21"] = False
                            # placeholder=f"Extraer fechas, nombre y apellidos de todos los {len(st.session_state['multi_file_name'])} ficheros",
                            if introduce_prompt and st.session_state['value_21'] in [2, 3]:
                                # print(st.session_state["case_query"])
                                logging.info(
                                    f"Gemini multi Page: Intruccion introduced, session state {st.session_state['value_21']}"
                                )
                                # call upload fuction to read the pdf file
                                upload_files(st, "21")
                                st.session_state["upload_state_21"] = (
                                    f"Instruccion introducida\n{introduce_prompt}"
                                )
                                st.session_state["prompt_introduced_21"] = introduce_prompt
                                # send not clicked but send file and initial prompt to Gemini
                                if (
                                    st.session_state["buttom_send_not_clicked_21"] == True
                                    and st.session_state["chat_true_21"] == "chat activo"
                                ):
                                    # chat active session 5
                                    st.session_state['value_21'] = 5
                                    col1 = 1
                                    col2 = 4
                                    st.session_state["vcol1doc_21"] = 1
                                    st.session_state["vcol2doc_21"] = 4
                                    st.session_state["expander_21"] = False
                                    logging.info(
                                        f"Gemini multi Page: Session Initialized, first prompt send, session state {st.session_state['value_21']}"
                                    )
                                # update status
                                if st.session_state["initialized_21"] == "True":
                                    st.session_state["upload_state_21"] = (
                                        f"Instruccion introducida\n {st.session_state['prompt_introduced_21']}"
                                    )
                # Col 2 Status box, write prompt, Conversation with Model
                with row1_2:
                    # expander contains text area with status and button send instruction to Gemini
                    with st.expander(
                        "���️Instruccion to send to Gemini 👇",
                        expanded=st.session_state["expander_21"],
                    ):
                        upload_state = st.text_area(
                            "Status selection", "", key="upload_state_21", height=130
                        )
                    # Dedice when to show butten send instruction
                    if st.session_state['value_21'] == 3 and introduce_prompt:
                        if st.button(
                            "Send Promt to Gemini",
                            on_click=prepare_prompt,
                            args=[
                                st.session_state["list_images_multi_21"],
                                st.session_state["prompt_introduced_21"],
                                "all",
                                st,
                                "21",
                            ],
                            key="buttom_send_21",
                            disabled=st.session_state["buttom_send_not_clicked_21"],
                        ):
                            # Prompt send to Gemini
                            logging.info("Page 21 after_click_buttom_send")
                            st.session_state["chat_true_21"] = "chat activo"
                            st.session_state["buttom_has_send_21"] = "buttom_Send"
                            st.session_state['value_21'] = 5
                            st.session_state["buttom_send_not_clicked_21"] = True
                            col1 = 1
                            col2 = 4
                            st.session_state["vcol1doc_21"] = 1
                            st.session_state["vcol2doc_21"] = 4
                            st.session_state["expander_21"] = False
                    # if chat active
                    if st.session_state["chat_true_21"] == "chat activo":
                        logging.info(
                            f"Gemini multi Page: Chat active session {st.session_state['value_21']}"
                        )
                        st.session_state["chat_true_21"] = "chat activo"
                        # chat object to speak with Gemini
                        prompt = st.chat_input(
                            "Enter your questions here", disabled=not input
                        )

                        # first send to google is what we introduce in the input text
                        if prompt == "terminar":
                            logging.info(
                                f"Gemini multi Page: Terminar Chat session {st.session_state['value_21']}"
                            )
                            # reload page and delete temp files
                            if st.session_state["case_query_21"] == True:
                                reload_page_many_docs(st, ss,  df_answers, pname, placeholder, num="21")
                            else:
                                reload_page_many_docs(
                                    st,
                                    ss,
                                    df_answers_no_case,
                                    pname_no_case,
                                    placeholder,
                                    num="21",
                                )
                        else:
                            # check if chat initialized

                            if st.session_state["initialized_21"] == "False":
                                # in first prompt we send the document and the prompt introduced manually
                                response = get_chat_response(
                                    st.session_state["llm_21"], st.session_state["prompt_21"]
                                )
                                st.session_state["chat_answers_history_21"].append(response)
                                st.session_state["user_prompt_history_21"].append(
                                    st.session_state["prompt_introduced_21"]
                                )
                                st.session_state["chat_history_21"].append(
                                    (st.session_state["prompt_introduced_21"], response)
                                )
                                st.session_state["initialized_21"] = "True"
                                st.session_state["buttom_send_clicked_21"] = True

                            # next sends to google we take it from chat object
                            elif st.session_state["initialized_21"] == "True":
                                prompt1 = [f"""{prompt} """]
                                # actualiza status
                                st.session_state["prompt_introduced_21"] = prompt
                                logging.info(
                                    f"Gemini multi Page: Session Initialized, second prompt session state {st.session_state['value_21']}"
                                )
                                response = get_chat_response(
                                    st.session_state["llm_21"], prompt1
                                )
                                # actualiza buffer chat
                                st.session_state["chat_answers_history_21"].append(response)
                                st.session_state["user_prompt_history_21"].append(prompt1[0])
                                st.session_state["chat_history_21"].append(
                                    (prompt1[0], response)
                                )
                                st.session_state["buttom_send_clicked_21"] = True
                                st.session_state["buttom_resfresh_clicked_21"] = True

                            # write chat in window
                            if len(st.session_state["chat_answers_history_21"]) > 0:
                                list1 = copy.deepcopy(
                                    st.session_state["chat_answers_history_21"]
                                )
                                list2 = copy.deepcopy(
                                    st.session_state["user_prompt_history_21"]
                                )

                                if len(st.session_state["chat_answers_history_21"]) > 1:
                                    list1.reverse()

                                if len(st.session_state["user_prompt_history_21"]) > 1:
                                    list2.reverse()

                                for i, j in zip(list1, list2):
                                    message1 = st.chat_message("user")
                                    message1.write(j)
                                    message2 = st.chat_message("assistant")
                                    message2.write(i)
        except:
            st.session_state["salir_21"] = True
            # if exception log error to google for debugging purposes
            placeholder.empty()
            # get the sys stack and log to gcloud
            text = print_stack()
            text = "Gemini Page 21 " + text
            logging.error(text)
        return


if __name__ == "__main__":
    # setup environtment
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

    if "salir_21" not in st.session_state:
        st.session_state["salir_21"] = False  

    if st.session_state["salir_21"] == False:  
        placeholder_21 = st.empty()
        with placeholder_21.container():
            col1, col2 = 2, 3
            config = dotenv_values(os.path.join(PROJECT_DIR, "keys", ".env"))
            with open(
                os.path.join(PROJECT_DIR, "keys", "complete-tube-421007-208a4862c992.json")
            ) as source:
                info = json.load(source)

            vertex_credentials = service_account.Credentials.from_service_account_info(info)
            # Disable Gcloud logging
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
            if "llm_21" not in st.session_state:
                st.session_state["llm_21"]  = init_model(config)
                st.session_state["llm_21"] = st.session_state["llm_21"].start_chat(response_validation=False)
                
            logging.info(f"Model loaded: {config.get('MODEL')}")
            main(

                col1=col1,
                col2=col2,
                placeholder=placeholder_21,
            )
