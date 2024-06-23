import os
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from google.oauth2 import service_account
from dotenv import dotenv_values
import json
import vertexai
import chromadb.utils.embedding_functions as embedding_functions
import streamlit as st
from pathlib import Path
from kb.templates import first_prompt, second_prompt, query_prompt
from kb.chains import get_complete_chain, get_retrieval_chain

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")

onlyfiles = [
    f for f in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, f))
]


@st.experimental_dialog("Visualiza contexto 👇", width="large")
def visualiza_context(st, out):
    docs = out["context"]
    context = []
    for doc in docs:
        context.append(
            f"{doc.metadata.get('filename')}_page_{doc.metadata.get('page')}"
        )
    seccion2 = st.selectbox(
        "Selecciona documento 👇",
        context,
        index=None,
        key="select_context",
    )
    if seccion2:
        with st.expander("Contexto", expanded=True):
            for doc in docs:
                if (
                    f"{doc.metadata.get('filename')}_page_{doc.metadata.get('page')}"
                    == seccion2
                ):
                    st.text_area(
                        f"documento {doc.metadata.get('filename')}_page_{doc.metadata.get('page')}  👇",
                        height=300,
                        key="kb_text2",
                        value=doc.page_content,
                    )

                    break


def main(retriever, embeddings_retriever, embedding_function, llm, col1, col2):

    if "checkbox2" not in st.session_state:
        st.session_state["checkbox2"] = False

    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    # if "vcol1mdoc" in st.session_state and "vcol2mdoc" in st.session_state:
    #    col1 = st.session_state["vcol1mdoc"]
    #    col2 = st.session_state["vcol2mdoc"]
    row1_1, row1_2 = st.columns((2, 3))

    with row1_1:
        seccion = st.selectbox(
            "Selecciona fichero 👇",
            onlyfiles,
            index=None,
            key="select_file",
        )
        checkbox2 = st.checkbox("Use only file seclected to search for Information")
        query = st.text_input("Enter your intruction here 👇")
        if seccion and checkbox2:
            with row1_2:

                st.session_state["checkbox2"] = True
                if query:
                    complete_chain = get_complete_chain(
                        llm, vectorstore, query_prompt, second_prompt
                    )
                    out = complete_chain.invoke({"filename": seccion, "input": query})
                    st.text_area(
                        "Knowledge Base Response 👇",
                        height=300,
                        key="kb_text1",
                        value=out["output"].content,
                    )
                    if st.button("Ver contexto completo"):
                        visualiza_context(st, out)

        elif not checkbox2:
            with row1_2:
                st.session_state["checkbox2"] = False

                if query:
                    retrieval_chain = get_retrieval_chain(llm, second_prompt, retriever)
                    response = retrieval_chain.invoke({"input": query})
                    st.text_area(
                        "Knowledge Base Response 👇",
                        height=600,
                        key="kb_text2",
                        value=response["answer"],
                    )


if __name__ == "__main__":
    global col1, col2

    col1, col2 = 2, 3
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    path = path.parent.absolute()
    print(path)

    config = dotenv_values(os.path.join(path, "keys", ".env"))
    with open(
        os.path.join(path, "keys", "complete-tube-421007-9a7c35cd44e2.json")
    ) as source:
        info = json.load(source)

    vertex_credentials = service_account.Credentials.from_service_account_info(info)
    vertexai.init(
        project=config["PROJECT"],
        location=config["REGION"],
        credentials=vertex_credentials,
    )
    google_api_key = config["GEMINI-API-KEY"]
    os.environ["GEMINI_API_KEY"] = google_api_key

    # client = chromadb.PersistentClient(path="./chroma_db")

    embeddings_retriever = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        credentials=vertex_credentials,
        google_api_key=google_api_key,
    )

    google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key=google_api_key
    )

    vectorstore = Chroma(
        persist_directory=os.path.join(ROOT_DIR, "chroma_db"),
        embedding_function=embeddings_retriever,
        collection_name="forensic",
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 5}
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-001", credentials=vertex_credentials
    )
    main(
        retriever=retriever,
        embeddings_retriever=embeddings_retriever,
        embedding_function=google_ef,
        llm=llm,
        col1=col1,
        col2=col2,
    )
