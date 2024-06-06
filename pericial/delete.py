import streamlit as st
import os
from pathlib import Path
import json
from dotenv import dotenv_values
import pandas as pd
from google.oauth2 import service_account
import vertexai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore


st.title("Borra Seccion Pericial")

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


def remove(
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


def visualiza(df: pd.DataFrame, fname: str, vectorstore: PineconeVectorStore):
    """
    Visualize Seccion
    Args:
        df (pd.DataFrame): dataframe with all prompts
        fname (str): name of the file
        vectorstore (PineconeVectorStore): vectorstore with all prompts
    """
    file = st.session_state["select_box_pm"]

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
    st.button(
        "Delete",
        type="primary",
        key="save_button",
        on_click=remove,
        args=[df, id_, pine_id, fname, vectorstore],
    )


def main(embeddings, index, vectorstore):
    """
    main function to delete secciones
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
