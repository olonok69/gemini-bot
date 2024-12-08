import os
import pandas as pd
from langchain_pinecone import PineconeVectorStore


def open_table_answers(answers_dir: str):
    """
    open or create table withs answers and restore backup if exists
    params:
        answers_dir: str - directory where the table is stored
    """
    fname = os.path.join(answers_dir, "answers.csv")
    fname2 = os.path.join(answers_dir, "answers_backup.csv")
    # Open Table
    if os.path.isfile(fname):
        df = pd.read_csv(fname)
        df.to_csv(fname2, index=False)
    else:
        df = pd.DataFrame(
            columns=["id", "filename", "timestamp", "prompt", "respuesta_chat"]
        )
        df.to_csv(fname, index=False)
    return fname, fname2, df


def open_table_answers_no_case(answers_dir: str):
    """
    open or create table withs answers and restore backup if exists
    for Documents that are not aprt of a case
    params:
        answers_dir: str - directory where the table is stored
    """
    fname = os.path.join(answers_dir, "answers_no_case.csv")
    fname2 = os.path.join(answers_dir, "answers_no_case_backup.csv")
    # Open Table
    if os.path.isfile(fname):
        df = pd.read_csv(fname)
        df.to_csv(fname2, index=False)
    else:
        df = pd.DataFrame(
            columns=["id", "filename", "timestamp", "prompt", "respuesta_chat"]
        )
        df.to_csv(fname, index=False)
    return fname, fname2, df


def open_table_answers_final(answers_dir: str):
    """
    open or create table withs answers and restore backup if exists
    for answers that come from a combine prompt of a case +  a pericial section
    params:
        answers_dir: str - directory where the table is stored
    """
    fname = os.path.join(answers_dir, "answers_final.csv")
    fname2 = os.path.join(answers_dir, "answers_final_backup.csv")
    # Open Table
    if os.path.isfile(fname):
        df = pd.read_csv(fname)
        df.to_csv(fname2, index=False)
    else:
        df = pd.DataFrame(
            columns=["id", "filename", "timestamp", "prompt", "respuesta_chat"]
        )
        df.to_csv(fname, index=False)
    return fname, fname2, df


def open_table_prompts(prompts_dir: str):
    """
    open or create table withs promts and restore backup if exists
    params:
        prompts_dir: str - directory where the table is stored
    """
    fname = os.path.join(prompts_dir, "prompts.csv")
    fname2 = os.path.join(prompts_dir, "prompts_backup.csv")

    if os.path.isfile(fname):
        df = pd.read_csv(fname)
        df.to_csv(fname2, index=False)
    else:
        df = pd.DataFrame(columns=["id", "name_prompt", "prompt", "keywords"])
        df.to_csv(fname, index=False)
    return fname, fname2, df


def open_table_periciales(peridicales_dir: str):
    """
    open or create table withs promts and restore backup if exists
    params:
        prompts_dir: str - directory where the table is stored
    """
    # open table with all prompts
    fname = os.path.join(peridicales_dir, "periciales.csv")
    fname2 = os.path.join(peridicales_dir, "periciales_backup.csv")

    if os.path.isfile(fname):
        df = pd.read_csv(fname)
        df.to_csv(fname2, index=False)
    else:
        df = pd.DataFrame(columns=["id", "Title", "Text", "pinecone_id"])
        df.to_csv(fname, index=False)

    return fname, fname2, df


def create_folders(root_dir: str):
    """
    create folders for the project
    """
    OUT_FOLDER = os.path.join(root_dir, "out")
    TMP_FOLDER = os.path.join(root_dir, "tmp")
    ANSWERS_DIR = os.path.join(root_dir, "answers")
    DICTS_DIR = os.path.join(root_dir, "prompts", "dicts")
    PROMPTS_DIR = os.path.join(root_dir, "prompts", "table")
    os.makedirs(TMP_FOLDER, exist_ok=True)
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    os.makedirs(OUT_FOLDER, exist_ok=True)
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    os.makedirs(DICTS_DIR, exist_ok=True)
    return OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR


def changed_selector(st,num:int=10):
    st.session_state[f"file_and_answer_select_has_changed_{num}"] = True


def file_selector(st, df: pd.DataFrame, num:int=10):
    """
    select row from dataframe and return as dict
    st: session object
    df: dataframe with answers
    returns:
        selection_dict: dict - dictionary with the selected row
    """
    selection_dict = {}
    filenames = df["file_and_answer"].tolist()
    selected_filename = st.selectbox(
        "Select a file and an Answer from Gemini 👇",
        filenames,
        placeholder="Select a file",
        index=None,
        key="file_and_answer_select_{}".format(num),
        on_change=changed_selector,
        args=[st, num],
        disabled=st.session_state[f"buttom_send_visualiza_{num}"],
    )
    # print(st.session_state["file_and_answer_select"])

    selection = df[df["file_and_answer"] == selected_filename]

    if not selection.empty:
        selection_dict = selection.to_dict(orient="records")[0]
    return selection_dict


def remove_prompts(df, id_, fname):
    """
    delete prompt from dataframe and save to csv file
    :param df: dataframe
    :param id_: id of prompt
    :param fname: csv file name
    :return: dataframe
    """
    df = df.drop(df[df["id"] == id_].index)
    df.to_csv(fname, index=False)
    return


def remove_anwers(df, id_, fname):
    """
    delete prompt from dataframe and save to csv file
    :param df: dataframe
    :param id_: id of prompt
    :param fname: csv file name
    :return: dataframe
    """
    df = df.drop(df[df["id"] == id_].index)
    df.to_csv(fname, index=False)
    return


def remove_pericial(
    df: pd.DataFrame,
    id_: str,
    pine_id: str,
    fname: str,
    vectorstore: PineconeVectorStore,
):
    """
    Delete section Pericial from Datafrane and Vectorstore
    Args:
    df (pd.DataFrame): dataframe with all sections
    id_ (str): id of the section to delete
    pine_id (str): id of the vector in pinecone
    fname (str): name of the file
    vectorstore (PineconeVectorStore): vectorstore of the sections
    """
    # get id of the prompt

    try:
        vectorstore.delete([pine_id])
        df = df.drop(df[df["id"] == id_].index)
        df.to_csv(fname, index=False)
    except:
        raise AttributeError(
            f"Error al borrar la seccion dataframe: {id}, Pinecone: {pine_id}"
        )
    return
