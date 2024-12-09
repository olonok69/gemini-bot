import os
from langchain_chroma import Chroma
from langchain_community.utilities.semanticscholar import SemanticScholarAPIWrapper
#from langchain_google_community import GoogleSearchAPIWrapper
#from langchain_community.retrievers.web_research import WebResearchRetriever
from langchain_community.retrievers import TavilySearchAPIRetriever
from google.oauth2 import service_account
from dotenv import dotenv_values
import json
import vertexai
import streamlit as st
from streamlit import session_state as ss
from pathlib import Path
from kb.templates import semantic_query, combine_research_prompt
from kb.chains import (
    create_semantic_retrieval_chain,
    create_retrieval_qa_source_chain,
    create_Runnable_Parallel_chain,
    create_combine_parallel_outputs_chain,
    create_complete_chain,
)
from src.utils import print_stack
import logging
from src.maps import config as conf, init_session_num, reset_session_num
from src.work_gemini import init_llm, init_google_embeddings

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT_DIR)
PROJECT_DIR = path.parent.absolute().as_posix()
DOCS_DIR = os.path.join(PROJECT_DIR, "kb", "docs")
logging.info(f"PROJECT DIR: {PROJECT_DIR}, this folder: {ROOT_DIR}, Documents folder: {DOCS_DIR}")

@st.dialog("Visualiza contexto 👇", width="large")
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
                        key="kb_text312",
                        value=doc.page_content,
                    )

                    break

def change_state_31(session, pp):
    """
    change state after leave conversation
    params:
    st (streamlit): streamlit object
    pp (streamlit.empty): placeholder

    """
    reset_session_num(session,"31")
    pp.empty()
    del pp
    session.empty()
    session.stop()
    return

def main(col1, col2, placeholder):
    """
    Main function
    Argr:
        col1: column 1
        col2: column 2
        placeholder: placeholder for the app
    """

    with placeholder.container():
        if "init_run_31" not in st.session_state:
                st.session_state["init_run_31"] = False
        if st.session_state["init_run_31"] == False:
            init_session_num(st, ss, "31", col1, col2, conf["31"]["config_31"], None)

        if "checkbox_31" not in st.session_state:
            st.session_state["checkbox_31"] = False


        row1_1, row1_2 = st.columns((col1, col2))

        with row1_1:
            # if you press salir any time you close the conainer
            if st.button("Salir", on_click=change_state_31, args=(st, placeholder)):
                logging.info("Salir and writing history")
            query = st.text_input("Enter your query here 👇")

            if len(query) > 0:
                with row1_2:

                    if query:
                        st.session_state["retrieval_chain_31"] = create_semantic_retrieval_chain(
                            llm=st.session_state["llm_31"], api_wrapper=st.session_state["api_wrapper_31"], prompt_query=semantic_query
                        )

                        st.session_state["qa_chain_31"] = create_retrieval_qa_source_chain(
                            llm=st.session_state["llm_31"], web_research_retriever=st.session_state["web_research_retriever_31"] 
                        )

                        user_input = f"{query} Based on your findings write a description, main symptoms and how to treat them "

                        # chain runnable parallel to run semantic and google search chains in paralell
                        st.session_state["map_chain_31"] = create_Runnable_Parallel_chain(
                            retrieval_chain=st.session_state["retrieval_chain_31"], qa_chain=st.session_state["qa_chain_31"]
                        )
                        # create combine chain to combine output of parallel chains
                        st.session_state["combine_parallel_chain_31"] = create_combine_parallel_outputs_chain(
                            prompt_last=combine_research_prompt, llm=st.session_state["llm_31"]
                        )
                        # create complete sequential chain, which run all chains created before
                        st.session_state["complete_chain_31"] = create_complete_chain(
                            map_chain=st.session_state["map_chain_31"], second_chain=st.session_state["combine_parallel_chain_31"]
                        )
                        if st.session_state["complete_chain_31"]:

                            # call complete chain with user query
                            response = st.session_state["complete_chain_31"].invoke(
                                {"question": user_input, "query": query}
                            )

                            st.text_area(
                                "Knowledge Base Response 👇",
                                height=600,
                                key="kb_text_31",
                                value=response["d"].content,
                            )
                            # if st.button("Ver contexto completo"):
                            #     visualiza_context(st, out)
                            st.session_state["complete_chain_31"] = None


if __name__ == "__main__":
    global col1, col2
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    PROJECT_DIR = path.parent.absolute()
    
    # Set page layout
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "main.py"
        st.switch_page("main.py")

    if "salir_31" not in st.session_state:
        st.session_state["salir_31"] = False  

    if st.session_state["salir_31"] == False:  
        placeholder_30 = st.empty()
        with placeholder_30.container():
            col1, col2 = 2, 3
            config = dotenv_values(os.path.join(PROJECT_DIR, "keys", ".env"))
            with open(
                os.path.join(PROJECT_DIR, "keys", "complete-tube-421007-208a4862c992.json")
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
            os.environ["TAVILY_API_KEY"] = config.get("TAVILY_API_KEY")
            # get gemini model
            if "llm_31" not in st.session_state:
                st.session_state["llm_31"]  = init_llm(model=config.get('MODEL'), credentials=vertex_credentials) 
                logging.info(f"Model loaded: {config.get('MODEL')}")
            # get embeddings model
            if "embeddings_31" not in st.session_state:
                st.session_state["embeddings_31"] = init_google_embeddings(config=config, credentials=vertex_credentials, google_api_key=google_api_key)
                logging.info(f"Embeddings loaded: {config.get('EMBEDDINGS2')}")
            # api Semantic search
            if "api_wrapper_31" not in st.session_state:
                st.session_state["api_wrapper_31"] = SemanticScholarAPIWrapper(
                doc_content_chars_max=10000, top_k_results=10
            )   
                logging.info(f"API Scholar wrapper loaded")

            # Vectorstore
            if "vectorstore_31" not in st.session_state:
                st.session_state["vectorstore_31"] = Chroma(
                embedding_function= st.session_state["embeddings_31"],
            )  # persist_directory="chroma_db_google",
                logging.info(f"Chroma Vectorstore loaded")
            # Initialize
            if "web_research_retriever_31" not in st.session_state:
                # api google search
                #search = GoogleSearchAPIWrapper()
                st.session_state["web_research_retriever_31"] = TavilySearchAPIRetriever(k=4, api_key=config.get("TAVILY_API_KEY"))
            #     st.session_state["web_research_retriever_31"] = WebResearchRetriever.from_llm(
            #     vectorstore=st.session_state["vectorstore_31"], llm=st.session_state["llm_31"], search=search, allow_dangerous_requests=True,
            # )
                logging.info(f"Google Web Research Retriever loaded")

            main(

                col1=col1,
                col2=col2,
                placeholder=placeholder_30,
            )
