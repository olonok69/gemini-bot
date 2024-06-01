import copy
import datetime
import os
import json
import streamlit as st


def write_history_1(st):
    """
    Write history to file 1 doc
    param: st  session
    """
    text = ""
    list1 = copy.deepcopy(st.session_state["chat_answers_history"])
    list2 = copy.deepcopy(st.session_state["user_prompt_history"])

    if len(st.session_state["chat_answers_history"]) > 1:
        list1.reverse()

    if len(st.session_state["user_prompt_history"]) > 1:
        list2.reverse()

    for i, j in zip(list1, list2):
        text = text + "user :" + j + "\n"
        text = text + "assistant :" + i + "\n"

    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d_%H-%M-%S")

    with open(
        f"answers/{st.session_state['file_history']}_{now}_history.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(text)
        f.close()
    return


def write_history_multi(st):
    """
    Write history to multi files option
    param: st  session
    """
    text = ""
    list1 = copy.deepcopy(st.session_state["chat_answers_history"])
    list2 = copy.deepcopy(st.session_state["user_prompt_history"])

    if len(st.session_state["chat_answers_history"]) > 1:
        list1.reverse()

    if len(st.session_state["user_prompt_history"]) > 1:
        list2.reverse()

    for i, j in zip(list1, list2):
        text = text + "user :" + j + "\n"
        text = text + "assistant :" + i + "\n"
    text0 = ""
    for file in st.session_state["multi_file_name"]:
        text0 = text0 + file.replace(".pdf", "") + "_"
    text0 = text0[:-1]
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"answers/{text0}_{now}_history.txt", "w", encoding="utf-8") as f:
        f.write(text)
        f.close()
    return


def open_popup(st):
    """
    Open popup to save content
    """
    if st.session_state["buttom_popup"] != "no_buttom":
        with st.popover("Open popover"):
            st.markdown("Pega Contenido a Salvar de este fichero👇")
            txt = st.text_input("Paste here the content you want to save")
        if len(txt) > 0:
            with open(f"answers/test.txt", "w") as f:
                f.write(txt)
                f.close()


def reset_session_1(st, ss, chat):
    """
    Reset session
    param: st  session
    param: ss  session state
    param: chat  chat (gemini model)
    """
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_answers_history"] = []
    st.session_state["chat_history"] = []
    st.session_state["initialized"] = "False"
    st.session_state["chat"] = chat
    st.session_state["list_images"] = []
    st.session_state["file_name"] = "no file"
    st.session_state["file_history"] = "no file"
    st.session_state["prompt_introduced"] = ""
    st.session_state["prompt"] = ""
    st.session_state["chat_true"] = "no_chat"
    st.session_state["buttom_popup"] = "no_buttom"
    st.session_state["buttom_has_send"] = "no_buttom"
    ss.pdf_ref = None
    st.session_state.value = 0
    st.session_state["buttom_send_not_clicked"] = False
    return


def reset_session_multi(st, ss, chat):
    """
    Reset session
    param: st  session
    param: ss  session state
    param: chat  chat (gemini model)
    """
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_answers_history"] = []
    st.session_state["chat_history"] = []
    st.session_state["initialized"] = "False"
    st.session_state["chat"] = chat
    st.session_state["list_images_multi"] = []
    st.session_state["multi_file_name"] = []
    st.session_state["multi_file_pages"] = []
    st.session_state["prompt_introduced"] = ""
    st.session_state["prompt"] = ""
    st.session_state["chat_true"] = "no_chat"
    st.session_state["buttom_popup"] = "no_buttom"
    st.session_state["buttom_has_send"] = "no_buttom"
    ss.pdf_ref = None
    st.session_state.value = 0
    st.session_state["buttom_send_not_clicked"] = False
    st.session_state["prompt_enter_press"] = False
    return


@st.experimental_dialog("Choose prompt?")
def visualiza(st, path):
    file = st.session_state["select_box"]
    with open(os.path.join(path, file), "r") as f:
        prompt_dict = json.load(f)

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
        return
    if st.button("No accept"):
        st.session_state["prompt_introduced"] = ""
        return
