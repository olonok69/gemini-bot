import streamlit as st
import os.path
from pathlib import Path
from streamlit import session_state as ss
from src.pdf_utils import count_pdf_pages, upload_files
from google.oauth2 import service_account
from streamlit_js_eval import streamlit_js_eval
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from dotenv import dotenv_values
import json
from src.work_gemini import get_chat_response, prepare_prompt, start_chat
from src.helpers import write_history_multi, reset_session_multi
import copy


# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FOLDER = os.path.join(ROOT_DIR, "out")
TMP_FOLDER = os.path.join(ROOT_DIR, "tmp")


def reload_page(st, ss, model):
    # delete files
    write_history_multi(st)
    chat = start_chat(model)
    reset_session_multi(st, ss, chat)
    files = [f.unlink() for f in Path(f"{TMP_FOLDER}").glob("*") if f.is_file()]
    files = [f.unlink() for f in Path(f"{OUT_FOLDER}").glob("*") if f.is_file()]
    streamlit_js_eval(js_expressions="parent.window.location.reload()")


def change_status(st, status):
    st.session_state.value = status
    st.session_state["prompt_enter_press"] = True


def main(model):
    st.set_page_config(layout="wide")
    row1_1, row1_2 = st.columns((2, 3))

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
    if "list_images_multi" not in st.session_state:
        st.session_state["list_images_multi"] = []

    # placeholder for multiple files
    if "multi_file_name" not in st.session_state:
        st.session_state["multi_file_name"] = []
    if "multi_file_pages" not in st.session_state:
        st.session_state["multi_file_pages"] = []
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
    if "prompt_enter_press" not in st.session_state:
        st.session_state["prompt_enter_press"] = False

    with row1_1:
        # st.header("File Picker")

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
                print("files uploaded")
            if uploaded_files:
                # To read file as bytes:
                for file in uploaded_files:
                    im_bytes = file.read()
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
                binary_data = ss.pdf_ref
                # pdf_viewer(input=binary_data, width=700, height=400)

                if len(
                    st.session_state["multi_file_name"]
                ) > 0 and st.session_state.value in [1, 2, 3]:
                    st.session_state.value = 2
                    introduce_prompt = st.text_input(
                        "Introduce instruccion a mandar a gemini 👇",
                        key="introduce_prompt",
                        disabled=st.session_state["buttom_send_not_clicked"],
                    )
                    # placeholder=f"Extraer fechas, nombre y apellidos de todos los {len(st.session_state['multi_file_name'])} ficheros",
                    if introduce_prompt and st.session_state.value in [2, 3]:
                        print(st.session_state.value)
                        upload_files(st)
                        st.session_state["upload_state"] = (
                            f"Instruccion introducida\n{introduce_prompt}"
                        )
                        st.session_state["prompt_introduced"] = introduce_prompt

                        if (
                            st.session_state["buttom_send_not_clicked"] == True
                            and st.session_state["chat_true"] == "chat activo"
                        ):
                            # chat active session 5
                            st.session_state.value = 5
                        if st.session_state["initialized"] == "True":
                            st.session_state["upload_state"] = (
                                f"Instruccion introducida\n {st.session_state['prompt_introduced']}"
                            )

        with row1_2:

            upload_state = st.text_area(
                "Status selection", "", key="upload_state", height=130
            )
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
                    print("after_click_buttom_send")
                    st.session_state["chat_true"] = "chat activo"
                    st.session_state["buttom_has_send"] = "buttom_Send"
                    st.session_state.value = 5
                    st.session_state["buttom_send_not_clicked"] = True

            if st.session_state["chat_true"] == "chat activo":
                print(st.session_state.value)
                st.session_state["chat_true"] = "chat activo"
                prompt = st.chat_input("Enter your questions here", disabled=not input)

                # first send to google is what we introduce in the input text
                if prompt == "terminar":
                    print("terminar")
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
                        print(prompt1)
                        response = get_chat_response(st.session_state["chat"], prompt1)
                        # actualiza buffer chat
                        st.session_state["chat_answers_history"].append(response)
                        st.session_state["user_prompt_history"].append(prompt1[0])
                        st.session_state["chat_history"].append((prompt1[0], response))
                        st.session_state["buttom_send_clicked"] = True
                        st.session_state["buttom_resfresh_clicked"] = True

                    # write chat in window
                    if len(st.session_state["chat_answers_history"]) > 0:
                        list1 = copy.deepcopy(st.session_state["chat_answers_history"])
                        list2 = copy.deepcopy(st.session_state["user_prompt_history"])

                        if len(st.session_state["chat_answers_history"]) > 1:
                            list1.reverse()

                        if len(st.session_state["user_prompt_history"]) > 1:
                            list2.reverse()

                        for i, j in zip(list1, list2):
                            message1 = st.chat_message("user")
                            message1.write(j)
                            message2 = st.chat_message("assistant")
                            message2.write(i)


if __name__ == "__main__":
    config = dotenv_values("keys/.env")
    with open("keys/complete-tube-421007-9a7c35cd44e2.json") as source:
        info = json.load(source)

    vertex_credentials = service_account.Credentials.from_service_account_info(info)

    vertexai.init(
        project=config["PROJECT"],
        location=config["REGION"],
        credentials=vertex_credentials,
    )
    model = GenerativeModel(
        "gemini-1.5-pro-preview-0409",
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

    main(model=model)
