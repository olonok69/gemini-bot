import streamlit as st
import os
from pathlib import Path
import json
from dotenv import dotenv_values
import pandas as pd
from pericial.gemini_fn import secciones
from google.oauth2 import service_account
import vertexai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from typing import Dict

st.title("Modifica Seccion Pericial")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "table")
# create durs if does not exists
os.makedirs(DATA_DIR, exist_ok=True)

# open table with all prompts
fname = os.path.join(DATA_DIR, "periciales.csv")
fname2 = os.path.join(DATA_DIR, "periciales_backup.csv")

if os.path.isfile(fname):
    df = pd.read_csv(fname)
    df.to_csv(fname2, index=False)
else:
    df = pd.DataFrame(columns=["id", "Title", "Text", "pinecone_id"])
    df.to_csv(fname, index=False)

# all names of the prompts
onlyfiles = df["Title"].to_list()


def save_text(
    fname: str, prompt_dict: Dict, df: pd.DataFrame, vectorstore: PineconeVectorStore
):
    """
    Save text after modification
    Args:
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
            print(st.session_state["tt_title"])

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
    except:
        raise AttributeError("Error al guardar el archivo")
    return


def visualiza(df: pd.DataFrame, fname: str, vectorstore: PineconeVectorStore):
    """
    Visualize prompt
    Args:
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
    """
    file = st.session_state["select_box_pm"]

    # transform the row into a dictionary
    prompt_dict = df[df.Title == file].to_dict(orient="records")[0]
    txt, txt2 = "-1", "-1"
    txt = st.text_area(
        "Modify Title 👇",
        value=prompt_dict.get("Title"),
        key="tt_title",
        on_change=save_text,
        args=[fname, prompt_dict, df, vectorstore],
    )

    txt2 = st.text_area(
        "Modify Content Section 👇",
        height=300,
        key="tt_text",
        value=prompt_dict.get("Text"),
        on_change=save_text,
        args=[fname, prompt_dict, df, vectorstore],
    )


def main(embeddings, index, vectorstore):
    """
    main function to add prompts
    params:
    embeddings (GoogleGenerativeAIEmbeddings): model to generate embeddings
    index (Pinecone.Index): vector store to save embeddings
    vectorstore (PineconeVectorStore): vector store to save embeddings
    """

    if "embeddings" not in st.session_state:
        st.session_state["embeddings"] = embeddings
    if "index" not in st.session_state:
        st.session_state["index"] = index
    if "vectorstore" not in st.session_state:
        st.session_state["vectorstore"] = vectorstore

    option = st.selectbox(
        "select prompt",
        onlyfiles,
        on_change=visualiza,
        args=[df, fname, st.session_state["vectorstore"]],
        key="select_box_pm",
    )


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    config = dotenv_values(os.path.join(path.parent.absolute(), "keys", ".env"))
    with open(
        os.path.join(
            path.parent.absolute(), "keys", "complete-tube-421007-9a7c35cd44e2.json"
        )
    ) as source:
        info = json.load(source)

    vertex_credentials = service_account.Credentials.from_service_account_info(info)
    vertexai.init(
        project=config["PROJECT"],
        location=config["REGION"],
        credentials=vertex_credentials,
    )
    # key access gemini
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = config.get("GEMINI-API-KEY")
    if "PINECONE_API_KEY" not in os.environ:
        os.environ["PINECONE_API_KEY"] = config.get("PINECONE_API_KEY")
    if "PINECONE_INDEX_NAME" not in os.environ:
        os.environ["PINECONE_INDEX_NAME"] = "forensic"
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    pc = Pinecone(api_key=config.get("PINECONE_API_KEY"))
    index = pc.Index("forensic")

    vectorstore = PineconeVectorStore(embedding=embeddings, index_name="forensic")

    main(embeddings, index, vectorstore)
