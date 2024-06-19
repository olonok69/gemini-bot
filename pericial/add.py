import streamlit as st
import os
from pathlib import Path
import uuid
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


def save_text(
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
    print(index[0])
    # check if id already exists, if not add to dataframe

    df = pd.concat([df, temp_df], ignore_index=True)
    df.to_csv(fname, index=False)
    return


def main(embeddings, index, vectorstore):
    """
    main function to add prompts
    params:
    embeddings (GoogleGenerativeAIEmbeddings): model to generate embeddings
    index (Pinecone.Index): vector store to save embeddings
    vectorstore (PineconeVectorStore): vector store to save embeddings
    """
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

    if "embeddings" not in st.session_state:
        st.session_state["embeddings"] = embeddings
    if "index" not in st.session_state:
        st.session_state["index"] = index
    if "vectorstore" not in st.session_state:
        st.session_state["vectorstore"] = vectorstore
    st.title("Add Pericial")
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
                st.button(
                    "Save",
                    type="primary",
                    key="save_button",
                    on_click=save_text,
                    args=[
                        title,
                        text,
                        seccion,
                        df,
                        fname,
                        st.session_state["vectorstore"],
                    ],
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
