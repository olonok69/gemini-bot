import copy
import datetime
import os
import json
import streamlit as st
import pandas as pd
import uuid
import datetime
from typing import List
from src.work_gemini import start_chat
from src.pdf_utils import count_pdf_pages, upload
from pathlib import Path


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
        text = text + "user : " + j + "\n"
        text = text + "assistant : " + i + "\n"
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
            st.markdown("Pega Contenido a Salvar de este fichero 👇")
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
    st.session_state["init_run_1"] = False
    st.session_state["vcol1doc"] = 40
    st.session_state["vcol2doc"] = 60
    st.session_state["expander_2"] = True

    return


def reload_page_1_doc(
    st, ss, model, df_answers, pname, placeholder, tmp_folder, out_folder
):
    """
    reload page
    params:
    st (streamlit): streamlit object
    ss (streamlit.session_state): streamlit session state
    model (vertexai.generative_models.GenerativeModel): model
    df_answers (pd.DataFrame): dataframe with all answers

    """
    # delete files
    # write_history_1(st)
    list2 = copy.deepcopy(st.session_state["chat_answers_history"])
    # get filename
    filename = st.session_state["file_history"]
    # save the response of Model
    save_df_many(
        list2=list2,
        df=df_answers,
        fname=pname,
        prompt=st.session_state["prompt_introduced"],
        filename=filename,
    )

    chat = start_chat(model)
    reset_session_1(st, ss, chat)
    # delete files in temp
    _ = [f.unlink() for f in Path(f"{tmp_folder}").glob("*") if f.is_file()]
    _ = [f.unlink() for f in Path(f"{out_folder}").glob("*") if f.is_file()]

    placeholder.empty()
    st.stop()
    return


def init_session_1_prompt(st, ss, model, col1, col2):
    """
    initialize session state for multiple files option
    param: st  session
    param: ss  session state
    param: model  chat (gemini model)
    """
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
    if "vcol1doc" not in st.session_state:
        st.session_state["vcol1doc"] = col1
    if "vcol2doc" not in st.session_state:
        st.session_state["vcol2doc"] = col2
    if "expander_2" not in st.session_state:
        st.session_state["expander_2"] = True
    st.session_state["init_run_1"] = True
    return


def init_session_add_kb(st, ss, vectorstore):
    """
    initialize session state for multiple files option
    param: st  session
    param: ss  session state
    param: vectorstore  faiss vector store
    """
    # placeholder for multiple files
    if "file_name" not in st.session_state:
        st.session_state["file_name"] = "no file"
    if "file_history" not in st.session_state:
        st.session_state["file_history"] = "no file"
    if "upload_state" not in st.session_state:
        st.session_state["upload_state"] = ""
    if "faiss_vectorstore" not in st.session_state:
        st.session_state["faiss_vectorstore"] = vectorstore
    if "pages" not in st.session_state:
        st.session_state["pages"] = []
    if "documents" not in st.session_state:
        st.session_state["documents"] = []
    if "ids" not in st.session_state:
        st.session_state["ids"] = []
    if "metadatas" not in st.session_state:
        st.session_state["metadatas"] = []
    if "pdf_ref" not in ss:
        ss.pdf_ref = None
    if "value" not in st.session_state:
        st.session_state.value = 0

    if "add_file_kb_selected" not in st.session_state:
        st.session_state["add_file_kb_selected"] = False

    st.session_state["init_run_add_kb"] = True
    return


def reset_session_add_kb(st, ss):
    """
    initialize session state for multiple files option
    param: st  session
    param: ss  session state
    param: vectorstore  faiss vector store
    """
    # placeholder for multiple files

    st.session_state["file_name"] = "no file"
    st.session_state["file_history"] = "no file"
    st.session_state["upload_state"] = ""
    st.session_state["faiss_vectorstore"] = None
    st.session_state["pages"] = []
    st.session_state["documents"] = []
    st.session_state["ids"] = []
    st.session_state["metadatas"] = []
    ss.pdf_ref = None
    st.session_state.value = 0
    st.session_state["add_file_kb_selected"] = False
    st.session_state["init_run_add_kb"] = True
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
    st.session_state["init_run_2"] = False
    st.session_state["vcol1mdoc"] = 2
    st.session_state["vcol2mdoc"] = 3
    st.session_state["expander_3"] = True
    st.session_state["case_query"] = False
    return


def init_session_multi(st, ss, model, col1, col2):
    """
    initialize session state for multiple files option
    param: st  session
    param: ss  session state
    param: model  chat (gemini model)
    """
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
    if "vcol1mdoc" not in st.session_state:
        st.session_state["vcol1mdoc"] = col1
    if "vcol2mdoc" not in st.session_state:
        st.session_state["vcol2mdoc"] = col2
    if "expander_3" not in st.session_state:
        st.session_state["expander_3"] = True
    if "case_query" not in st.session_state:
        st.session_state["case_query"] = False
    st.session_state["init_run_2"] = True
    return


def reload_page_many_docs(st, ss, model, df, fname, placeholder):
    """
    refresh page and initialize variables page may docs
    Args:
        st ([type]): session stramlit
        model ([type]): llm
        fname ([type]): name dataframe filename  final aswers
        df ([type]): dataframe  final aswers
        placeholder ([type]): conatiner to reset
    """
    # delete files
    # write response of model to table
    list2 = copy.deepcopy(st.session_state["chat_answers_history"])
    # get filename
    filename = get_filename_multi(st)
    # save the response of Model
    save_df_many(
        list2=list2,
        df=df,
        fname=fname,
        prompt=st.session_state["prompt_introduced"],
        filename=filename,
    )
    # restart chat
    chat = start_chat(model)
    reset_session_multi(st, ss, chat)
    placeholder.empty()

    st.stop()
    return


def change_status(st, status):
    """
    change status of session state
    """
    st.session_state.value = status
    st.session_state["prompt_enter_press"] = True


def init_visualiza(st, model, embeddings, index, vectorstore, col1, col2):
    """
    Initialize session state for visualization
    param: st  session
    param: model  chat (gemini model)
    param: embeddings  embeddings model
    param: index  index of the document
    param: vectorstore  vectorstore of the document

    """
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
    if "upload_state" not in st.session_state:
        st.session_state["upload_state"] = ""
    if "file_prompt_selected_visualiza" not in st.session_state:
        st.session_state["file_prompt_selected_visualiza"] = False

    if "answer_introduced" not in st.session_state:
        st.session_state["answer_introduced"] = {}
    if "file_and_answer_select_has_changed" not in st.session_state:
        st.session_state["file_and_answer_select_has_changed"] = False
    if "embeddings" not in st.session_state:
        st.session_state["embeddings"] = embeddings
    if "index" not in st.session_state:
        st.session_state["index"] = index
    if "vectorstore" not in st.session_state:
        st.session_state["vectorstore"] = vectorstore
    if "pericial_prompt_selected" not in st.session_state:
        st.session_state["pericial_prompt_selected"] = False
    if "section_prompt_selected" not in st.session_state:
        st.session_state["section_prompt_selected"] = False
    if "seccion_introduced" not in st.session_state:
        st.session_state["seccion_introduced"] = ""
    if "expander_1" not in st.session_state:
        st.session_state["expander_1"] = True
    if "chat_true" not in st.session_state:
        st.session_state["chat_true"] = "no_chat"
    if "instruction_to_be_send" not in st.session_state:
        st.session_state["instruction_to_be_send"] = ""
    if "buttom_send_visualiza" not in st.session_state:
        st.session_state["buttom_send_visualiza"] = False
    if "chat_true_visualiza" not in st.session_state:
        st.session_state["chat_true_visualiza"] = False
    if "b_accept_inside_pericial" not in st.session_state:
        st.session_state["b_accept_inside_pericial"] = False
    if "vcol1" not in st.session_state:
        st.session_state["vcol1"] = col1
    if "vcol2" not in st.session_state:
        st.session_state["vcol2"] = col2
    if "prompt_combined_filename" not in st.session_state:
        st.session_state["prompt_combined_filename"] = "Default"
    if "prompt_introduced" not in st.session_state:
        st.session_state["prompt_introduced"] = ""
    st.session_state["init_run"] = True

    return


def reset_session_visualiza(st, model, embeddings, index, vectorstore):
    """
    reset session state for visualization
    param: st  session
    param: model  chat (gemini model)
    param: embeddings  embeddings model
    param: index  index of the document
    param: vectorstore  vectorstore of the document

    """

    st.session_state["user_prompt_history"] = []
    st.session_state["chat_answers_history"] = []
    st.session_state["chat_history"] = []
    st.session_state["initialized"] = "False"
    st.session_state["chat"] = start_chat(model)
    st.session_state["upload_state"] = ""
    st.session_state["file_prompt_selected_visualiza"] = False
    st.session_state["answer_introduced"] = {}
    st.session_state["file_and_answer_select_has_changed"] = False
    st.session_state["embeddings"] = embeddings
    st.session_state["index"] = index
    st.session_state["vectorstore"] = vectorstore
    st.session_state["pericial_prompt_selected"] = False
    st.session_state["section_prompt_selected"] = False
    st.session_state["seccion_introduced"] = ""
    st.session_state["expander_1"] = True
    st.session_state["chat_true"] = "no_chat"
    st.session_state["instruction_to_be_send"] = ""
    st.session_state["buttom_send_visualiza"] = False
    st.session_state["chat_true_visualiza"] = False
    st.session_state["init_run"] = False
    st.session_state["b_accept_inside_pericial"] = False
    st.session_state["vcol1"] = 50
    st.session_state["vcol2"] = 50
    st.session_state["prompt_combined_filename"] = "Default"
    st.session_state["prompt_introduced"] = ""
    return


def init_session_faiss(st, col1, col2, llm):
    """
    initialize session state busqueda faiss
    param: st  session
    param: ss  session state
    param: model  chat (gemini model)
    """
    # Initialize Vars
    if "user_prompt_history_faiss" not in st.session_state:
        st.session_state["user_prompt_history_faiss"] = []
    if "chat_answers_history_faiss" not in st.session_state:
        st.session_state["chat_answers_history_faiss"] = []
    if "chat_history_faiss" not in st.session_state:
        st.session_state["chat_history_faiss"] = []
    if "initialized_faiss" not in st.session_state:
        st.session_state["initialized_faiss"] = "False"
    if "checkbox3" not in st.session_state:
        st.session_state["checkbox3"] = False
    if "store" not in st.session_state:
        st.session_state["store"] = {}
    if "expander_4" not in st.session_state:
        st.session_state["expander_4"] = True
    if "history_conversation_with_model" not in st.session_state:
        st.session_state["history_conversation_with_model"] = []
    if "buttom_visualiza_faiss_clicked" not in st.session_state:
        st.session_state["buttom_visualiza_faiss_clicked"] = False
    if "docs_context_names" not in st.session_state:
        st.session_state["docs_context_names"] = []
    if "docs_context" not in st.session_state:
        st.session_state["docs_context"] = []
    if "current_prompt" not in st.session_state:
        st.session_state["current_prompt"] = ""
    if "answer_prompt" not in st.session_state:
        st.session_state["answer_prompt"] = ""
    if "file_faiss_selected" not in st.session_state:
        st.session_state["file_faiss_selected"] = False
    if "file_kb_faiss_selected" not in st.session_state:
        st.session_state["file_kb_faiss_selected"] = False
    if "name_file_kb_faiss_selected" not in st.session_state:
        st.session_state["name_file_kb_faiss_selected"] = "None"
    if "kb_faiss_retriever" not in st.session_state:
        st.session_state["kb_faiss_retriever"] = None
    if "llm" not in st.session_state:
        st.session_state["llm"] = llm
    if "conversational_rag_chain" not in st.session_state:
        st.session_state["conversational_rag_chain"] = None

    st.session_state["init_run_faiss"] = True
    return


def reset_session_faiss(st):
    """
    initialize session state busqueda faiss
    param: st  session
    """
    # Initialize Vars

    st.session_state["user_prompt_history_faiss"] = []
    st.session_state["chat_answers_history_faiss"] = []
    st.session_state["chat_history_faiss"] = []
    st.session_state["initialized_faiss"] = "False"  #
    st.session_state["checkbox3"] = False
    st.session_state["store"] = {}
    st.session_state["expander_4"] = True
    st.session_state["history_conversation_with_model"] = []
    st.session_state["buttom_visualiza_faiss_clicked"] = False
    st.session_state["docs_context_names"] = []
    st.session_state["docs_context"] = []
    st.session_state["current_prompt"] = ""
    st.session_state["answer_prompt"] = ""
    st.session_state["file_faiss_selected"] = False
    st.session_state["file_kb_faiss_selected"] = False
    st.session_state["name_file_kb_faiss_selected"] = "None"
    st.session_state["kb_faiss_retriever"] = None
    st.session_state["init_run_faiss"] = True
    st.session_state["llm"] = None
    st.session_state["conversational_rag_chain"] = None
    return


@st.experimental_dialog("Choose prompt 👇")
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


def save_df_many(list2: List, df: pd.DataFrame, fname: str, prompt: str, filename: str):
    """
    Save prompt to a json file
    :param name_prompt: name of the prompt
    :param prompt: prompt
    :param keywords: keywords
    :param df: dataframe with all prompts
    """
    if len(list2) > 1:
        list2.reverse()
    p_dict = {}
    p_dict["id"] = str(uuid.uuid4())
    p_dict["filename"] = filename
    p_dict["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p_dict["prompt"] = prompt.replace(",", "")
    p_dict["respuesta_chat"] = list2[0].replace(",", "")
    row = pd.DataFrame(p_dict, index=[0])
    df = pd.concat([df, row], ignore_index=True)
    df.to_csv(fname, index=False)

    return


def get_filename_multi(st):
    """
    extract filename from multi file name
    """

    text0 = ""
    for file in st.session_state["multi_file_name"]:
        text0 = text0 + file.replace(".pdf", "") + "_"
    filename = text0[:-1]
    return filename


@st.experimental_dialog("Choose prompt 👇", width="large")
def visualiza_1_prompt(st, df, page_select, numpages):
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
        st.session_state.value = 3
        st.rerun()

    if st.button("No accept"):
        st.session_state["prompt_introduced"] = ""
        st.session_state["file_prompt_selected"] = False
        st.session_state.value = 2
        st.rerun()


@st.experimental_dialog("Confirm Selection 👇", width="large")
def visualiza_display_page(st, selection_dict):
    """
    Visualize the answers and selected
    Args:
        st (streamlit): streamlit object
        selection_dict (dict): dictionary with the selected answers
    """
    # get the name of the file

    txt = st.text_area(
        "File and Timestamp",
        value=selection_dict.get("file_and_answer"),
        key="file_and_answer",
        height=70,
    )
    txt3 = st.text_area(
        "Prompt sent to Gemini",
        value=selection_dict.get("prompt"),
        key="prompt",
    )
    txt2 = st.text_area(
        "Response Gemini",
        height=300,
        key="respuesta_chat",
        value=selection_dict.get("respuesta_chat"),
    )
    if st.button("Accept", key="accept_inside_select_answer"):
        st.session_state["answer_introduced"] = selection_dict
        st.session_state["file_prompt_selected_visualiza"] = True
        st.rerun()

    return


@st.experimental_dialog("Confirma Pericial 👇", width="large")
def visualiza_pericial(st, df, list_matches_textos, list_matches):
    """
    Visualize the prompt
    Args:
        st (streamlit): streamlit object
        df (pd.DataFrame): dataframe with all prompts
        text_selection (text): pericial selected to visualization
    """
    # get the name of the file
    seccion2 = st.session_state["select_box_2"]
    pos = list_matches_textos.index(seccion2)
    idv = list_matches[pos]

    data = df[df["pinecone_id"] == idv]
    data = data.to_dict("records")
    text_seccion = data[0].get("Text")
    # transform the row into a dictionary

    txt = st.text_area(
        "Similarity Score",
        value=f'Score Similarity: {seccion2.split(", ")[0]}',
        key="similarity_area",
    )
    txt3 = st.text_area(
        "Title Pericial keywords",
        value=idv,
        key="title_area",
    )
    txt2 = st.text_area(
        "texto seccion Pericial",
        height=300,
        key="seccion_area",
        value=text_seccion,
    )
    if st.button("Accept", key="accept_inside_pericial"):
        st.session_state["b_accept_inside_pericial"] = True
        st.session_state["seccion_introduced"] = text_seccion
        st.session_state["pericial_prompt_selected"] = True

        st.rerun()

    return


def reload_page_combina(
    st, model, embeddings, index, vectorstore, fname, df, placeholder
):
    """
    refresh page and initialize variables
    Args:
        st ([type]): session stramlit
        model ([type]): llm
        embeddings ([type]): llm embeddings
        index ([type]): index pinecone
        vectorstore ([type]): vectorstore pinecone
        fname ([type]): name dataframe filename  final aswers
        df ([type]): dataframe  final aswers
        placeholder ([type]): conatiner to reset
    """
    # delete files
    # write response of model to table
    list2 = copy.deepcopy(st.session_state["chat_answers_history"])
    # get filename
    filename = st.session_state["prompt_combined_filename"]
    # save the response of Model
    save_df_many(
        list2=list2,
        df=df,
        fname=fname,
        prompt=st.session_state["prompt_introduced"],
        filename=filename,
    )
    # restart
    reset_session_visualiza(st, model, embeddings, index, vectorstore)
    placeholder.empty()
    st.stop()
    return
