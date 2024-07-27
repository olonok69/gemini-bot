import os
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.utilities.semanticscholar import SemanticScholarAPIWrapper
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_community.retrievers import WebResearchRetriever
from google.oauth2 import service_account
from dotenv import dotenv_values
import json
import vertexai
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from pathlib import Path
from kb.templates import semantic_query, combine_research_prompt
from kb.chains import (
    create_semantic_retrieval_chain,
    create_retrieval_qa_source_chain,
    create_Runnable_Parallel_chain,
    create_combine_parallel_outputs_chain,
    create_complete_chain,
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")


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


def main(api_wrapper, web_research_retriever, llm, col1, col2, placeholder):

    if "checkbox2" not in st.session_state:
        st.session_state["checkbox2"] = False

    # if "vcol1mdoc" in st.session_state and "vcol2mdoc" in st.session_state:
    #    col1 = st.session_state["vcol1mdoc"]
    #    col2 = st.session_state["vcol2mdoc"]
    row1_1, row1_2 = st.columns((2, 3))

    with row1_1:
        query = st.text_input("Enter your query here 👇")
        if st.button("Salir"):
            placeholder.empty()
            st.stop()
        if len(query) > 0:
            with row1_2:

                if query:
                    retrieval_chain = create_semantic_retrieval_chain(
                        llm=llm, api_wrapper=api_wrapper, prompt_query=semantic_query
                    )

                    qa_chain = create_retrieval_qa_source_chain(
                        llm=llm, web_research_retriever=web_research_retriever
                    )

                    user_input = f"{query} Based on your findings write a description, main symptoms and how to treat them "

                    # chain runnable parallel to run semantic and google search chains in paralell
                    map_chain = create_Runnable_Parallel_chain(
                        retrieval_chain=retrieval_chain, qa_chain=qa_chain
                    )
                    # create combine chain to combine output of parallel chains
                    combine_parallel_chain = create_combine_parallel_outputs_chain(
                        prompt_last=combine_research_prompt, llm=llm
                    )
                    # create complete sequential chain, which run all chains created before
                    complete_chain = create_complete_chain(
                        map_chain=map_chain, second_chain=combine_parallel_chain
                    )
                    if complete_chain:

                        # call complete chain with user query
                        response = complete_chain.invoke(
                            {"question": user_input, "query": query}
                        )

                        st.text_area(
                            "Knowledge Base Response 👇",
                            height=600,
                            key="kb_text1",
                            value=response["d"].content,
                        )
                        # if st.button("Ver contexto completo"):
                        #     visualiza_context(st, out)
                        del complete_chain


if __name__ == "__main__":
    global col1, col2

    col1, col2 = 2, 3
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    path = path.parent.absolute()
    # Set page layout
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    placeholder_kb_1 = st.empty()
    with placeholder_kb_1.container():
        config = dotenv_values(os.path.join(path, "keys", ".env"))
        with open(
            os.path.join(path, "keys", "complete-tube-421007-208a4862c992.json")
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
        os.environ["GOOGLE_API_KEY"] = config.get("GOOGLE_API_KEY")
        os.environ["GOOGLE_CSE_ID"] = config.get("GOOGLE_CSE_ID")
        os.environ["USER_AGENT"] = "GEMINI-BOT"
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-001", credentials=vertex_credentials
        )
        # api Semantic search
        api_wrapper = SemanticScholarAPIWrapper(
            doc_content_chars_max=10000, top_k_results=10
        )
        # api google search
        search = GoogleSearchAPIWrapper()

        # Vectorstore

        vectorstore = Chroma(
            embedding_function=GoogleGenerativeAIEmbeddings(
                model=config.get("EMBEDDINGS2"),
                credentials=vertex_credentials,
                google_api_key=google_api_key,
            ),
        )  # persist_directory="chroma_db_google",
        # Initialize

        web_research_retriever = WebResearchRetriever.from_llm(
            vectorstore=vectorstore, llm=llm, search=search
        )

        main(
            api_wrapper=api_wrapper,
            web_research_retriever=web_research_retriever,
            llm=llm,
            col1=col1,
            col2=col2,
            placeholder=placeholder_kb_1,
        )
