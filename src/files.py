import os
import pandas as pd


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


def changed_selector(st):
    st.session_state["file_and_answer_select_has_changed"] = True


def file_selector(st, df: pd.DataFrame):
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
        key="file_and_answer_select",
        on_change=changed_selector,
        args=[st],
        disabled=st.session_state["buttom_send_visualiza"],
    )
    # print(st.session_state["file_and_answer_select"])

    selection = df[df["file_and_answer"] == selected_filename]

    if not selection.empty:
        selection_dict = selection.to_dict(orient="records")[0]
    return selection_dict
