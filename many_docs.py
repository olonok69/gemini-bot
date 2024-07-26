import streamlit as st
import os.path
from streamlit import session_state as ss
from src.pdf_utils import count_pdf_pages, upload_files
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from dotenv import dotenv_values
import json
from src.work_gemini import get_chat_response, prepare_prompt
from src.helpers import (
    init_session_multi,
    reload_page_many_docs,
    change_status,
)
from src.utils import create_client_logging, print_stack
from src.files import open_table_answers, create_folders, open_table_answers_no_case
import copy
import logging


# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(ROOT_DIR)
# open table with all prompts
pname, pname2, df_answers = open_table_answers(ANSWERS_DIR)
pname_no_case, pname2_no_case, df_answers_no_case = open_table_answers_no_case(
    ANSWERS_DIR
)


def main(model, col1, col2, placeholder):
    """
    main loop. Get Model
    Args:
        model (vertexai.generative_models.GenerativeModel): model
        col1 (int): size col 1
        col2 (int): size col 2
        placeholder (streamlit.empty): placeholder
    """

    if "vcol1mdoc" in st.session_state and "vcol2mdoc" in st.session_state:
        col1 = st.session_state["vcol1mdoc"]
        col2 = st.session_state["vcol2mdoc"]
    row1_1, row1_2 = st.columns((2, 3))
    try:
        # Initialize Vars
        if "init_run_2" not in st.session_state:
            st.session_state["init_run_2"] = False
        if st.session_state["init_run_2"] == False:
            init_session_multi(st, ss, model, col1, col2)
        # Col 1 Upload file and write prompt
        with row1_1:
            # if salir kill placeholder
            if st.button("Salir"):
                placeholder.empty()
                st.stop()

            # Access the uploaded ref via a key.
            if st.session_state.value >= 0:
                uploaded_files = st.file_uploader(
                    "Upload PDF file",
                    type=("pdf"),
                    key="pdf",
                    accept_multiple_files=True,
                    disabled=st.session_state["buttom_send_not_clicked"],
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
                        if file.name not in st.session_state["multi_file_name"]:
                            st.session_state["multi_file_name"].append(file.name)
                            st.session_state["multi_file_pages"].append(
                                count_pdf_pages(file_path)
                            )
                        if ss.pdf:
                            ss.pdf_ref = im_bytes

                    texto = ""
                    # write in status Area Text
                    for i, j in zip(
                        st.session_state["multi_file_name"],
                        st.session_state["multi_file_pages"],
                    ):
                        texto = texto + f"file: {i} {j} paginas\n"
                    st.session_state["upload_state"] = (
                        f"Number of files uploaded {len(st.session_state['multi_file_name'])}\n{texto}"
                    )
                st.session_state.value = 1  # file uploaded

        # Now you can access "pdf_ref" anywhere in your app.
        if ss.pdf_ref:
            with row1_1:
                if st.session_state.value >= 1:
                    # if file uploaded
                    if len(
                        st.session_state["multi_file_name"]
                    ) > 0 and st.session_state.value in [1, 2, 3]:
                        st.session_state.value = 2
                        introduce_prompt = st.text_input(
                            "Introduce instruccion a mandar a gemini 👇",
                            key="introduce_prompt",
                            disabled=st.session_state["buttom_send_not_clicked"],
                        )
                        # checkbox  to decide if the answer go to case or not
                        checkbox1 = st.checkbox("Case Query")
                        if checkbox1:
                            st.session_state["case_query"] = True
                        else:
                            st.session_state["case_query"] = False
                        # placeholder=f"Extraer fechas, nombre y apellidos de todos los {len(st.session_state['multi_file_name'])} ficheros",
                        if introduce_prompt and st.session_state.value in [2, 3]:
                            # print(st.session_state["case_query"])
                            logging.info(
                                f"Gemini multi Page: Intruccion introduced, session state {st.session_state.value}"
                            )
                            # call upload fuction to read the pdf file
                            upload_files(st)
                            st.session_state["upload_state"] = (
                                f"Instruccion introducida\n{introduce_prompt}"
                            )
                            st.session_state["prompt_introduced"] = introduce_prompt
                            # send not clicked but send file and initial prompt to Gemini
                            if (
                                st.session_state["buttom_send_not_clicked"] == True
                                and st.session_state["chat_true"] == "chat activo"
                            ):
                                # chat active session 5
                                st.session_state.value = 5
                                col1 = 1
                                col2 = 4
                                st.session_state["vcol1mdoc"] = 1
                                st.session_state["vcol2mdoc"] = 4
                                st.session_state["expander_3"] = False
                                logging.info(
                                    f"Gemini multi Page: Session Initialized, first prompt send, session state {st.session_state.value}"
                                )
                            # update status
                            if st.session_state["initialized"] == "True":
                                st.session_state["upload_state"] = (
                                    f"Instruccion introducida\n {st.session_state['prompt_introduced']}"
                                )
            # Col 2 Status box, write prompt, Conversation with Model
            with row1_2:
                # expander contains text area with status and button send instruction to Gemini
                with st.expander(
                    "���️Instruccion to send to Gemini 👇",
                    expanded=st.session_state["expander_3"],
                ):
                    upload_state = st.text_area(
                        "Status selection", "", key="upload_state", height=130
                    )
                # Dedice when to show butten send instruction
                if st.session_state.value == 3 and introduce_prompt:
                    if st.button(
                        "Send Promt to Gemini",
                        on_click=prepare_prompt,
                        args=[
                            st.session_state["list_images_multi"],
                            st.session_state["prompt_introduced"],
                            "all",
                            st,
                        ],
                        key="buttom_send",
                        disabled=st.session_state["buttom_send_not_clicked"],
                    ):
                        # Prompt send to Gemini
                        print("after_click_buttom_send")
                        st.session_state["chat_true"] = "chat activo"
                        st.session_state["buttom_has_send"] = "buttom_Send"
                        st.session_state.value = 5
                        st.session_state["buttom_send_not_clicked"] = True
                        col1 = 1
                        col2 = 4
                        st.session_state["vcol1mdoc"] = 1
                        st.session_state["vcol2mdoc"] = 4
                        st.session_state["expander_3"] = False
                # if chat active
                if st.session_state["chat_true"] == "chat activo":
                    logging.info(
                        f"Gemini multi Page: Chat active session {st.session_state.value}"
                    )
                    st.session_state["chat_true"] = "chat activo"
                    # chat object to speak with Gemini
                    prompt = st.chat_input(
                        "Enter your questions here", disabled=not input
                    )

                    # first send to google is what we introduce in the input text
                    if prompt == "terminar":
                        logging.info(
                            f"Gemini multi Page: Terminar Chat session {st.session_state.value}"
                        )
                        # reload page and delete temp files
                        if st.session_state["case_query"] == True:
                            reload_page_many_docs(st, ss, model, df_answers, pname)
                        else:
                            reload_page_many_docs(
                                st,
                                ss,
                                model,
                                df_answers_no_case,
                                pname_no_case,
                                placeholder,
                            )
                    else:
                        # check if chat initialized

                        if st.session_state["initialized"] == "False":
                            # in first prompt we send the document and the prompt introduced manually
                            response = get_chat_response(
                                st.session_state["chat"], st.session_state["prompt"]
                            )
                            st.session_state["chat_answers_history"].append(response)
                            st.session_state["user_prompt_history"].append(
                                st.session_state["prompt_introduced"]
                            )
                            st.session_state["chat_history"].append(
                                (st.session_state["prompt_introduced"], response)
                            )
                            st.session_state["initialized"] = "True"
                            st.session_state["buttom_send_clicked"] = True

                        # next sends to google we take it from chat object
                        elif st.session_state["initialized"] == "True":
                            prompt1 = [f"""{prompt} """]
                            # actualiza status
                            st.session_state["prompt_introduced"] = prompt
                            logging.info(
                                f"Gemini multi Page: Session Initialized, second prompt session state {st.session_state.value}"
                            )
                            response = get_chat_response(
                                st.session_state["chat"], prompt1
                            )
                            # actualiza buffer chat
                            st.session_state["chat_answers_history"].append(response)
                            st.session_state["user_prompt_history"].append(prompt1[0])
                            st.session_state["chat_history"].append(
                                (prompt1[0], response)
                            )
                            st.session_state["buttom_send_clicked"] = True
                            st.session_state["buttom_resfresh_clicked"] = True

                        # write chat in window
                        if len(st.session_state["chat_answers_history"]) > 0:
                            list1 = copy.deepcopy(
                                st.session_state["chat_answers_history"]
                            )
                            list2 = copy.deepcopy(
                                st.session_state["user_prompt_history"]
                            )

                            if len(st.session_state["chat_answers_history"]) > 1:
                                list1.reverse()

                            if len(st.session_state["user_prompt_history"]) > 1:
                                list2.reverse()

                            for i, j in zip(list1, list2):
                                message1 = st.chat_message("user")
                                message1.write(j)
                                message2 = st.chat_message("assistant")
                                message2.write(i)
    except:
        # if exception log error to google for debugging purposes
        placeholder.empty()
        # get the sys stack and log to gcloud
        text = print_stack()
        text = "Gemini multi Page: " + text
        logging.error(text)
    return


if __name__ == "__main__":
    global col1, col2

    col1, col2 = 2, 3
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    placeholder = st.empty()
    with placeholder.container():
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
        model = GenerativeModel(
            config["MODEL"],
            system_instruction=[
                """You a helpful agent who helps to extract relevant information from documents"""
            ],
            safety_settings={
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            },
            generation_config={
                "max_output_tokens": 8192,
                "temperature": 0.1,
                "top_p": 0.95,
            },
        )
        logging.info("Gemini multi Page:  Model loaded")
        main(
            model=model,
            col1=col1,
            col2=col2,
            placeholder=placeholder,
        )
