import uuid
import pandas as pd
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from typing import Dict
from src.files import remove_prompts, remove_pericial, remove_anwers
import logging

def selected_add(st, num:int=10):
    st.session_state[f"selector_selected_add_{num}"] = True


def selected_modifica(st, num:int=10):
    st.session_state[f"selector_selected_modifica_{num}"] = True


def selected_delete(st, num):
    st.session_state[f"selector_selected_delete_{num}"] = True


# this is for modifica
def selected_modify_prompt(st, num):
    st.session_state[f"selector_selected_section_{num}"] = True


def selected_modify_percial(st, num):
    st.session_state[f"selector_selected_pericial_{num}"] = True


# this is for delete.py
def selected_delete_prompt(st, num):
    st.session_state[f"selector_selected_section_delete_{num}"] = True


def selected_delete_percial(st,num):
    st.session_state[f"selector_selected_pericial_delete_{num}"] = True


def selected_delete_answer_gemini(st,num):
    st.session_state[f"selector_selected_answer_delete_{num}"] = True


def selected_delete_answer_gemini_nocase(st,num):
    st.session_state[f"selector_selected_answer_delete_no_case_{num}"] = True


def save_text_add_prompt(
    name_prompt: str, prompt: str, keywords: str, df: pd.DataFrame, fname: str
):
    """
    Save prompt to a json file
    :param name_prompt: name of the prompt
    :param prompt: prompt
    :param keywords: keywords
    :param df: dataframe with all prompts
    """
    p_dict = {}
    p_dict["id"] = str(uuid.uuid4())
    p_dict["name_prompt"] = name_prompt.lower()
    p_dict["prompt"] = prompt
    p_dict["keywords"] = keywords.replace(" ", "")

    # check if id already exists, if not add to dataframe
    ids = df["name_prompt"].tolist()
    if p_dict["name_prompt"] in ids:
        df = df.drop(df[df["name_prompt"] == p_dict["name_prompt"]].index)
    row = pd.DataFrame(p_dict, index=[0])
    df = pd.concat([df, row], ignore_index=True)
    df.to_csv(fname, index=False)

    return


def visualiza_add_prompt(st, df_prompts, fname, num: int = 10):
    """
    Visualiza add prompt
    args:
    st (_type_): session streamlit
    df_prompts (pd.DataFrame): dataframe with all prompts
    fname (str): filename to save the dataframe
    """
    txt = st.text_input("Introduce name of the prompt", key="name_prompt")

    txt3 = st.text_input(
        "Introduce keywords",
        placeholder="introduce palabras clave separadas por una coma. Ejemplo: informe,revision",
        key="keywords",
    )
    txt2 = st.text_area(
        "Introduce prompt",
        height=300,
        key="prompt",
    )
    # pname, pname2, df_answers # Prompts
    if (
        st.session_state.name_prompt
        and st.session_state.prompt
        and st.session_state.keywords
    ):

        if st.button(
            "Save",
            type="primary",
            key="save_button",
            on_click=save_text_add_prompt,
            args=[
                st.session_state.name_prompt,
                st.session_state.prompt,
                st.session_state.keywords,
                df_prompts,
                fname,
            ],
        ):
            st.session_state[f"selector_selected_add_{num}"] = False

    return


def visualiza_add_pericial(st, df_pericial, fname, secciones, num="10"):
    """
    Visualiza add prompt
    args:
    st (_type_): session streamlit
    df_pericial (pd.DataFrame): dataframe with all periciales reports
    fname (str): filename to save the dataframe
    """
    title = st.text_area("Introduce Titulo Pericial 👇", height=100, key="title")

    if len(title) > 0:
        text = st.text_area(
            "Introduce Texto seccion Pericial 👇", height=300, key="text"
        )
        if text:
            seccion = st.selectbox(
                "selecciona seccion 👇",
                secciones,
                key="select_box",
            )
            if seccion:
                if st.button(
                    "Save",
                    type="primary",
                    key="save_button",
                    on_click=save_text_add_pericial,
                    args=[
                        title,
                        text,
                        seccion,
                        df_pericial,
                        fname,
                        st.session_state[f"vectorstore_{num}"],
                    ],
                ):

                    st.session_state[f"selector_selected_add_{num}"] = False

    return


def save_text_add_pericial(
    title: str,
    text: str,
    seccion: str,
    df: pd.DataFrame,
    fname: str,
    vectorstore: PineconeVectorStore,
):
    """
    save text in the dataframe and generate embeddings
    params:
    title (str): text to save
    text (str): text to save
    seccion (str): seccion to save
    df (pd.DataFrame): dataframe with all sections
    fname (str): filename to save dataframe
    index (PineconeVectorStore): vector store to save embeddings
    """
    if len(seccion + " - " + title + text) > 4500:
        text = text[:4500]

    p_dict = {}
    p_dict["id"] = str(uuid.uuid4())
    p_dict["Title"] = seccion + " - " + title
    p_dict["Text"] = text
    temp_df = pd.DataFrame([p_dict], columns=["id", "Title", "Text"])

    d = Document(
        page_content=title.strip() + "\n" + text.strip(),
        metadata={"text": text.strip(), "title": title.strip(), "sections": seccion},
    )
    index = vectorstore.add_documents(documents=[d])
    temp_df["pinecone_id"] = index[0]
    logging.info(f"Pericial add to index {index[0]}")
    # check if id already exists, if not add to dataframe

    df = pd.concat([df, temp_df], ignore_index=True)
    df.to_csv(fname, index=False)

    return


def save_text_modifica_prompt(st, fname: str, prompt_dict: Dict, df: pd.DataFrame):
    """
    Save text after modification
    Args:
        st (_type_): session streamlit
        fname (str): name of the file
        prompt_dict (dict): dictionary with the new prompt
        df (pd.DataFrame): dataframe with all prompts
    """
    # get id of the prompt
    id_ = prompt_dict["id"]

    p_dict = {}
    # if name_prompt_change
    if st.session_state["name_prompt"] != prompt_dict.get("name_prompt"):

        p_dict["name_prompt"] = st.session_state["name_prompt"]
    else:

        p_dict["name_prompt"] = prompt_dict.get("name_prompt")

    # if prompt_change
    if st.session_state["prompt"] != prompt_dict.get("prompt"):
        p_dict["prompt"] = st.session_state["prompt"]
    else:
        p_dict["prompt"] = prompt_dict.get("prompt")
    # if keywords change
    if st.session_state["keywords"] != prompt_dict.get("keywords"):
        p_dict["keywords"] = st.session_state["keywords"]
    else:
        p_dict["keywords"] = prompt_dict.get("keywords")

    p_dict["id"] = id_

    # drop the previous records
    df = df.drop(df[df["id"] == prompt_dict["id"]].index)
    row = pd.DataFrame(p_dict, index=[0])
    df = pd.concat([df, row], ignore_index=True)
    # save the new dataframe
    df.to_csv(fname, index=False)
    st.session_state["selector_selected_modifica"] = False
    st.session_state["selector_selected_section"] = False
    st.session_state["selector_selected_pericial"] = False

    return


def visualiza_modify_prompt(st, df: pd.DataFrame, fname: str, num: int = 10):
    """
    Visualize prompt
    Args:
        st (_type_): session streamlit
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
    """
    file = st.session_state[f"select_box_modifica_prompt_{num}"]

    # transform the row into a dictionary
    prompt_dict = df[df.name_prompt == file].to_dict(orient="records")[0]
    txt, txt2, txt3 = "-1", "-1", "-1"
    txt = st.text_area(
        "Modify name of the prompt 👇",
        value=prompt_dict.get("name_prompt"),
        key="name_prompt",
        on_change=save_text_modifica_prompt,
        args=[st, fname, prompt_dict, df],
    )
    txt3 = st.text_area(
        "Modify keywords 👇",
        value=prompt_dict.get("keywords"),
        key="keywords",
        on_change=save_text_modifica_prompt,
        args=[st, fname, prompt_dict, df],
    )
    txt2 = st.text_area(
        "Modify prompt 👇",
        height=300,
        key="prompt",
        value=prompt_dict.get("prompt"),
        on_change=save_text_modifica_prompt,
        args=[st, fname, prompt_dict, df],
    )
    return


def save_text_modifica_pericial(
    st,
    fname: str,
    prompt_dict: Dict,
    df: pd.DataFrame,
    vectorstore: PineconeVectorStore,
    num: str = "10",
):
    """
    Save text after modification
    Args:
        st: session streamlit
        fname (str): name of the file
        prompt_dict (dict): dictionary with the new prompt
        df (pd.DataFrame): dataframe with all prompts
        vectorstore (PineconeVectorStore): vectorstore with all prompts
    """
    # get id of the prompt
    id_ = prompt_dict["id"]
    pine_id = prompt_dict["pinecone_id"]
    try:
        vectorstore.delete([pine_id])
        p_dict = {}
        # if Title Change
        if st.session_state["tt_title"] != prompt_dict.get("Title"):
            

            p_dict["Title"] = st.session_state["tt_title"]
        else:
            p_dict["Title"] = prompt_dict.get("Title")

        # if prompt_change
        if st.session_state["tt_text"] != prompt_dict.get("Text"):
            p_dict["Text"] = st.session_state["tt_text"]
        else:
            p_dict["Text"] = prompt_dict.get("Text")

        # create new vector
        seccion = p_dict["Title"].split("-")[0]
        title = p_dict["Title"].replace(seccion, "")
        d = Document(
            page_content=title.strip() + "\n" + p_dict["Text"].strip(),
            metadata={
                "text": p_dict["Text"].strip(),
                "title": p_dict["Title"].strip(),
                "sections": seccion.strip(),
            },
        )
        # add it to vectorstore
        index = vectorstore.add_documents(documents=[d])
        p_dict["id"] = id_
        p_dict["pinecone_id"] = index[0]
        # drop the previous records
        df = df.drop(df[df["id"] == prompt_dict["id"]].index)
        row = pd.DataFrame(p_dict, index=[0])
        df = pd.concat([df, row], ignore_index=True)
        # save the new dataframe
        df.to_csv(fname, index=False)
        logging.info(f"Pericial modify to index {index[0]}")
        st.session_state[f"selector_selected_modifica_{num}"] = False
        st.session_state[f"selector_selected_section_{num}"] = False
        st.session_state[f"selector_selected_pericial_{num}"] = False
    except:
        raise AttributeError("Error al guardar el archivo")
    return


def visualiza_pericial_modifica(
    st, df: pd.DataFrame, fname: str, vectorstore: PineconeVectorStore, num: str = "10"
):
    """
    Visualize prompt
    Args:
        st:  session streamlit
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
        vectorstore (PineconeVectorStore): vectorstore with all sections
    """
    file = st.session_state[f"select_box_modifica_pericial_{num}"]

    # transform the row into a dictionary
    prompt_dict = df[df.Title == file].to_dict(orient="records")[0]
    txt, txt2 = "-1", "-1"
    txt = st.text_area(
        "Modify Title 👇",
        value=prompt_dict.get("Title"),
        key="tt_title",
        on_change=save_text_modifica_pericial,
        args=[st, fname, prompt_dict, df, vectorstore, num],
    )

    txt2 = st.text_area(
        "Modify Content Section 👇",
        height=300,
        key="tt_text",
        value=prompt_dict.get("Text"),
        on_change=save_text_modifica_pericial,
        args=[st, fname, prompt_dict, df, vectorstore, num],
    )
    return

def visualiza_delete_prompt(st, df: pd.DataFrame, fname: str, num: int = 10):
    """
    Visualize prompt
    Args:
        st:  session streamlit
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
    """
    file = st.session_state[f"select_box_delete_prompt_{num}"]

    # transform the row into a dictionary
    prompt_dict = df[df.name_prompt == file].to_dict(orient="records")[0]
    id_ = prompt_dict["id"]

    txt = st.text_area(
        "Name of the prompt to delete",
        value=prompt_dict.get("name_prompt"),
        key="name_prompt",
    )
    txt3 = st.text_area(
        "Keywords to delete",
        value=prompt_dict.get("keywords"),
        key="keywords",
    )
    txt2 = st.text_area(
        "Detail of prompt to delete",
        height=300,
        key="prompt",
        value=prompt_dict.get("prompt"),
    )
    if st.button(
        "Delete",
        type="primary",
        key="delete_button",
        on_click=remove_prompts,
        args=[df, id_, fname],
    ):
        st.session_state[f"selector_selected_delete_{num}"] = False
        st.session_state[f"selector_selected_section_delete_{num}"] = False
        st.session_state[f"selector_selected_pericial_delete_{num}"] = False
        st.session_state[f"selector_selected_answer_delete_{num}"] = False
        st.session_state[f"selector_selected_answer_delete_no_case_{num}"] = False

    return


def visualiza_delete_pericial(
    st, df: pd.DataFrame, fname: str, vectorstore: PineconeVectorStore, num:str="10"
):
    """
    Visualize Seccion percial to delete
    Args:
        st:  session streamlit
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
        vectorstore (PineconeVectorStore): vectorstore with all prompts
    """
    file = st.session_state[f"select_box_delete_pericial_{num}"]

    # transform the row into a dictionary
    prompt_dict = df[df.Title == file].to_dict(orient="records")[0]
    id_ = prompt_dict["id"]
    pine_id = prompt_dict["pinecone_id"]
    txt = st.text_area(
        "Title 👇",
        value=prompt_dict.get("Title"),
        key="tt_title",
    )

    txt2 = st.text_area(
        "Content Section 👇",
        height=300,
        key="tt_text",
        value=prompt_dict.get("Text"),
    )
    if st.button(
        "Delete",
        type="primary",
        key="save_button",
        on_click=remove_pericial,
        args=[df, id_, pine_id, fname, vectorstore],
    ):
        st.session_state[f"selector_selected_delete_{num}"] = False
        st.session_state[f"selector_selected_section_delete_{num}"] = False
        st.session_state[f"selector_selected_pericial_delete_{num}"] = False
        st.session_state[f"selector_selected_answer_delete_{num}"] = False
        st.session_state[f"selector_selected_answer_delete_no_case_{num}"] = False


def visualiza_delete_answer_gemini(st, df: pd.DataFrame, fname: str, num:str="10"):
    """
    Visualize answer gemini  to delete
    Args:
        st:  session streamlit
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
        vectorstore (PineconeVectorStore): vectorstore with all prompts
    """
    file = st.session_state[f"select_box_delete_answers_gemini_{num}"]

    # transform the row into a dictionary
    filename = file.split("_")[0]
    timestamp = file.split("_")[1]
    prompt_dict = df[(df.filename == filename) & (df.timestamp == timestamp)].to_dict(
        orient="records"
    )[0]
    id_ = prompt_dict["id"]

    txt = st.text_area(
        "Prompt sent to gemini to delete",
        value=prompt_dict.get("prompt"),
        key="prompt_answer",
    )
    txt3 = st.text_area(
        "Filename and timestamp of the answer given by gemini to delete",
        value=f'File use: {prompt_dict.get("filename")} - Timestamp: {prompt_dict.get("timestamp")}',
        key="keywords",
    )
    txt2 = st.text_area(
        "Response given by Gemini delete",
        height=300,
        key="Response_gemini",
        value=prompt_dict.get("respuesta_chat"),
    )
    if st.button(
        "Delete",
        type="primary",
        key="delete_button_answer_gemini",
        on_click=remove_anwers,
        args=[df, id_, fname],
    ):
        st.session_state[f"selector_selected_delete_{num}"] = False
        st.session_state[f"selector_selected_section_delete_{num}"] = False
        st.session_state[f"selector_selected_pericial_delete_{num}"] = False
        st.session_state[f"selector_selected_answer_delete_{num}"] = False
        st.session_state[f"selector_selected_answer_delete_no_case_{num}"] = False

    return

def visualiza_delete_answer_gemini_no_case(st, df: pd.DataFrame, fname: str, num:str="10"):
    """
    Visualize answer gemini no case to delete
    Args:
        st:  session streamlit
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
        vectorstore (PineconeVectorStore): vectorstore with all prompts
    """
    file = st.session_state[f"select_box_delete_answers_gemini_no_case_{num}"]

    # transform the row into a dictionary
    filename = file.split("_")[0]
    timestamp = file.split("_")[1]
    prompt_dict = df[(df.filename == filename) & (df.timestamp == timestamp)].to_dict(
        orient="records"
    )[0]
    id_ = prompt_dict["id"]

    txt = st.text_area(
        "Prompt sent to gemini to delete",
        value=prompt_dict.get("prompt"),
        key="prompt_answer",
    )
    txt3 = st.text_area(
        "Filename and timestamp of the answer given by gemini to delete",
        value=f'File use: {prompt_dict.get("filename")} - Timestamp: {prompt_dict.get("timestamp")}',
        key="keywords",
    )
    txt2 = st.text_area(
        "Response given by Gemini delete",
        height=300,
        key="Response_gemini",
        value=prompt_dict.get("respuesta_chat"),
    )
    if st.button(
        "Delete",
        type="primary",
        key="delete_button_answer_gemini",
        on_click=remove_anwers,
        args=[df, id_, fname],
    ):
        st.session_state[f"selector_selected_delete_{num}"] = False
        st.session_state[f"selector_selected_section_delete_{num}"] = False
        st.session_state[f"selector_selected_pericial_delete_{num}"] = False
        st.session_state[f"selector_selected_answer_delete_{num}"] = False
        st.session_state[f"selector_selected_answer_delete_no_case_{num}"] = False
    return
