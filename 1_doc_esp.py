import streamlit as st
import os.path
from pathlib import Path
from streamlit_pdf_viewer import pdf_viewer
from streamlit import session_state as ss
from src.pdf_utils import count_pdf_pages, upload
from google.oauth2 import service_account
from streamlit_js_eval import streamlit_js_eval
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from dotenv import dotenv_values
import json
from src.work_gemini import get_chat_response, prepare_prompt, start_chat
from src.helpers import write_history_1, reset_session_1
from src.utils import create_client_logging, print_stack
import logging
import copy
import pandas as pd


# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FOLDER = os.path.join(ROOT_DIR, "out")
TMP_FOLDER = os.path.join(ROOT_DIR, "tmp")

DICTS_DIR = os.path.join(ROOT_DIR, "prompts", "dicts")
DATA_DIR = os.path.join(ROOT_DIR, "prompts", "table")

os.makedirs(DICTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# open table with all prompts
fname = os.path.join(DATA_DIR, "prompts.csv")
fname2 = os.path.join(DATA_DIR, "prompts_backup.csv")

if os.path.isfile(fname):
    df = pd.read_csv(fname)
    df.to_csv(fname2, index=False)
else:
    df = pd.DataFrame(columns=["id", "name_prompt", "prompt", "keywords"])
    df.to_csv(fname, index=False)

# all names of the prompts
onlyfiles = df["name_prompt"].to_list()


@st.experimental_dialog("Choose prompt?")
def visualiza(st, df, page_select, numpages):
    """
    Visualize the prompt
    Args:
        st (streamlit): streamlit object
        df (pd.DataFrame): dataframe with all prompts
        page_select (int): page selected
        numpages (int): number of pages
    """
    # get the name of the file
    file = st.session_state["select_box"]
    # transform the row into a dictionary
    prompt_dict = df[df.name_prompt == file].to_dict(orient="records")[0]
    id_ = prompt_dict["id"]

    txt = st.text_area(
        "Introduce name of the prompt",
        value=prompt_dict.get("name_prompt"),
        key="name_prompt",
    )
    txt3 = st.text_area(
        "Introduce keywords",
        value=prompt_dict.get("keywords"),
        key="keywords",
    )
    txt2 = st.text_area(
        "Introduce prompt",
        height=300,
        key="prompt",
        value=prompt_dict.get("prompt"),
    )
    if st.button("Accept"):
        st.session_state["prompt_introduced"] = (
            prompt_dict.get("name_prompt") + "\n" + prompt_dict.get("prompt")
        )
        st.session_state["file_prompt_selected"] = True
        upload(page_select, numpages, st)
        st.session_state.value == 3
        st.rerun()

    if st.button("No accept"):
        st.session_state["prompt_introduced"] = ""
        st.session_state["file_prompt_selected"] = False
        st.session_state.value == 2
        st.rerun()


def selected(st):
    st.session_state["file_prompt_selected"] = True


def reload_page(st, ss, model):
    """
    reload page

    """
    # delete files
    write_history_1(st)
    chat = start_chat(model)
    reset_session_1(st, ss, chat)
    files = [f.unlink() for f in Path(f"{TMP_FOLDER}").glob("*") if f.is_file()]
    files = [f.unlink() for f in Path(f"{OUT_FOLDER}").glob("*") if f.is_file()]
    streamlit_js_eval(js_expressions="parent.window.location.reload()")


def main(model):
    # two columns
    st.set_page_config(layout="wide")
    row1_1, row1_2 = st.columns((2, 3))
    try:
        # Initialize Vars
        if "user_prompt_history" not in st.session_state:
            st.session_state["user_prompt_history"] = []
        if "chat_answers_history" not in st.session_state:
            st.session_state["chat_answers_history"] = []
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        if "initialized" not in st.session_state:
            st.session_state["initialized"] = "False"
        if "chat" not in st.session_state:
            st.session_state["chat"] = start_chat(model)
        if "list_images" not in st.session_state:
            st.session_state["list_images"] = []
        # placeholder for multiple files
        if "file_name" not in st.session_state:
            st.session_state["file_name"] = "no file"
        if "file_history" not in st.session_state:
            st.session_state["file_history"] = "no file"
        if "prompt_introduced" not in st.session_state:
            st.session_state["prompt_introduced"] = ""
        if "prompt" not in st.session_state:
            st.session_state["prompt"] = ""
        if "chat_true" not in st.session_state:
            st.session_state["chat_true"] = "no_chat"
        if "buttom_popup" not in st.session_state:
            st.session_state["buttom_popup"] = "no_buttom"
        if "buttom_has_send" not in st.session_state:
            st.session_state["buttom_has_send"] = "no_buttom"
        if "pdf_ref" not in ss:
            ss.pdf_ref = None
        if "value" not in st.session_state:
            st.session_state.value = 0
        # buttom send to gemini
        if "buttom_send_not_clicked" not in st.session_state:
            st.session_state["buttom_send_not_clicked"] = False
        if "file_prompt_selected" not in st.session_state:
            st.session_state["file_prompt_selected"] = False

        with row1_1:
            # st.header("File Picker")

            # Access the uploaded ref via a key.
            if st.session_state.value >= 0:
                uploaded_files = st.file_uploader(
                    "Upload PDF file",
                    type=("pdf"),
                    key="pdf",
                    accept_multiple_files=False,
                    disabled=st.session_state["buttom_send_not_clicked"],
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
            with row1_1:
                if st.session_state.value >= 1:
                    binary_data = ss.pdf_ref
                    pdf_viewer(input=binary_data, width=700, height=400)
                    logging.info(f"Gemini 1 Page: pdf viewer {uploaded_files.name}")
                    page_select = st.text_input(
                        "Elige paginas a extraer 👇",
                        key="page_select",
                        placeholder="Selecciona paginas seguidas por comas. Ejemplo 1,3,4,5",
                        disabled=st.session_state["buttom_send_not_clicked"],
                    )

                    if page_select and st.session_state.value >= 1:
                        st.session_state.value = 2  # pages selected
                        st.session_state["upload_state"] = (
                            f"paginas seleccionadas {page_select}"
                        )
                        st.selectbox(
                            "select prompt 👇",
                            onlyfiles,
                            on_change=selected,
                            args=[st],
                            key="select_box",
                            disabled=st.session_state["buttom_send_not_clicked"],
                        )
                    if (
                        st.session_state["file_prompt_selected"] == True
                        and st.session_state["prompt_introduced"] == ""
                    ):
                        visualiza(st, df, page_select, numpages)

                    if st.session_state[
                        "prompt_introduced"
                    ] != "" and st.session_state.value in [2, 3]:
                        st.session_state["upload_state"] = (
                            f"Instruccion introducida\n{st.session_state['prompt_introduced'] }"
                        )
                        st.session_state.value = 3

                    if (
                        st.session_state["buttom_send_not_clicked"] == True
                        and st.session_state["chat_true"] == "chat activo"
                    ):
                        # chat active session 5
                        st.session_state.value = 5
                        print(st.session_state.value)
                        logging.info(
                            f"Gemini 1 Page: Session Initialized, first prompt send, session state {st.session_state.value}"
                        )
                    if st.session_state["initialized"] == "True":
                        st.session_state["upload_state"] = (
                            f"Instruccion introducida\n {st.session_state['prompt_introduced']}"
                        )

            with row1_2:

                upload_state = st.text_area(
                    "Status selection", "", key="upload_state", height=120
                )
                if (
                    st.session_state.value == 3
                    and st.session_state["file_prompt_selected"] == True
                ):
                    if st.button(
                        "Send Promt to Gemini",
                        on_click=prepare_prompt,
                        args=[
                            st.session_state["list_images"],
                            st.session_state["prompt_introduced"],
                            page_select,
                            st,
                        ],
                        key="buttom_send",
                        disabled=st.session_state["buttom_send_not_clicked"],
                    ):
                        print("after_click_buttom_send")
                        st.session_state["chat_true"] = "chat activo"
                        st.session_state["buttom_has_send"] = "buttom_Send"
                        st.session_state.value = 5
                        st.session_state["buttom_send_not_clicked"] = True

                if st.session_state["chat_true"] == "chat activo":
                    logging.info(
                        f"Gemini 1 Page: Chat active session {st.session_state.value}"
                    )
                    st.session_state["chat_true"] = "chat activo"
                    prompt = st.chat_input(
                        "Enter your questions here", disabled=not input
                    )

                    # first send to google is what we introduce in the input text
                    if prompt == "terminar":
                        logging.info(
                            f"Gemini 1 Page: Terminar Chat session {st.session_state.value}"
                        )
                        # reload page and delete temp files
                        reload_page(st, ss, model)
                    else:
                        if st.session_state["initialized"] == "False":

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
                                f"Gemini 1 Page: Session Initialized, second prompt session state {st.session_state.value}"
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

        # get the sys stack and log to gcloud
        text = print_stack()
        text = "Gemini 1 Page " + text
        logging.error(text)


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
    model = GenerativeModel(
        "gemini-1.5-flash-preview-0514",
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
    logging.info("Gemini 1 Page: Model loaded")
    main(model=model)