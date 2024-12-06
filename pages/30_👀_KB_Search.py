import os
from src.helpers import init_session_faiss, reset_session_faiss, save_df_many
from src.files import open_table_answers_no_case, create_folders
from google.oauth2 import service_account
from dotenv import dotenv_values
import json
import vertexai
import streamlit as st
from streamlit import session_state as ss
from langchain_community.vectorstores import FAISS
from pathlib import Path
from kb.templates import contextualize_q_prompt, qa_prompt
from kb.chains import (
    create_conversational_rag_chain,
)
from kb.controls import visualiza_context_faiss
from kb.utils import sumup_history, update_list_answers_queries
from src.utils import print_stack
import logging
from src.maps import config as conf, init_session_num, reset_session_num
from src.work_gemini import init_llm, init_google_embeddings


def reload_page_kb_faiss(st, df, fname, query, placeholder):
    """
    refresh page and initialize variables
    Args:
        st ([type]): session stramlit
        model ([type]): llm
        fname ([type]): name dataframe filename  final aswers
        df ([type]): dataframe  final aswers
        placeholder ([type]): conatiner to reset
    """

    # delete files
    # write response of model to table
    def format_prompt_awnswer(answer, prompt):
        """
        format prompt and answer
        """
        answer = answer.strip()
        answer = answer.replace("Answer:", "")
        answer = answer.replace(",", " ")
        # prompt
        prompt = prompt.strip()
        prompt = prompt.replace("prompt:", "")
        prompt = prompt.replace(",", " ")
        return answer, prompt

    splitter2 = "#"
    num_pages = query.split(splitter2)[-1]
    num_pages = num_pages.strip()
    # split answers before save
    if num_pages == "all":
        # All answers together
        answer = ""
        for ans in st.session_state["chat_answers_history_faiss"]:
            answer += ans.split("Answer:")[-1] + "\n"
        # All prompts together
        prompt = ""
        for ans in st.session_state["user_prompt_history_faiss"]:
            prompt += ans.split("prompt:")[-1] + "\n"

        answer, prompt = format_prompt_awnswer(answer, prompt)
        print(f"answer: {answer}")
        print(f"prompt: {prompt}")
    elif num_pages.isdigit():

        answer = st.session_state["chat_answers_history_faiss"][
            int(num_pages) - 1
        ].split("Answer:")[-1]
        prompt = st.session_state["user_prompt_history_faiss"][
            int(num_pages) - 1
        ].split("Prompt:")[-1]

        answer, prompt = format_prompt_awnswer(answer, prompt)
        print(f"answer: {answer}")
        print(f"prompt: {prompt}")
    else:
        raise ValueError("Invalid page number")

    # Filename
    if st.session_state["select_file_faiss_30"] != None:
        filename = st.session_state["select_file_faiss_30"]
    else:
        filename = "All files in KB"

    # save the response of Model

    save_df_many(
        list2=[answer],
        df=df,
        fname=fname,
        prompt=prompt,
        filename=filename,
    )
    del query
    reset_session_faiss(st)
    placeholder.empty()
    st.stop()
    return


def change_checkbox_faiss(st,num:int=10):
    st.session_state[f"checkbox_{num}"] = st.session_state[f"checkbox_faiss_{num}"]


def selected_file_kb(st, num:int=10):
    st.session_state[f"file_kb_faiss_selected_{num}"] = True

def change_state_30(session, placeholder):
    """
    change state after leave conversation
    params:
    st (streamlit): streamlit object
    placeholder (streamlit.empty): placeholder

    """
    placeholder.empty()
    del placeholder
    reset_session_num(session,"30")
    st.stop()
    return

def main( col1, col2, onlyfiles, fname, df, placeholder):
    """
    Main loop
    Args:

        col1 ([type]): size col 1
        col2 ([type]): size col 2
        onlyfiles ([type]): list of files to fill selectbox
        fname ([type]): name dataframe filename  final aswers
        df ([type]): dataframe  final aswers
        placeholder ([type]): conatiner to reset
    """

    try:

        # get config
        row1_1, row1_2 = st.columns((col1, col2))

        # Initialize Vars
        if "init_run_30" not in st.session_state:
            st.session_state["init_run_30"] = False
        if st.session_state["init_run_30"] == False:
            init_session_num(st, ss, "30", col1, col2, conf["30"]["config_30"], None)
        # Col 1 = row1_1
        with row1_1:
            # if you press salir any time you close the conainer
            if st.button("Salir", on_click=change_state_30, args=(st, placeholder)):
                logging.info("Salir and writing history")
            seccion = st.selectbox(
                "Selecciona fichero 👇",
                onlyfiles,
                index=None,
                key="select_file_faiss_30",
                on_change=selected_file_kb,
                args=[st, "30"],
            )
            checkbox_30 = st.checkbox(
                "Use only file seclected to search for Information",
                key="checkbox_faiss_30",
                on_change=change_checkbox_faiss,
                args=[st, "30"],
            )

            # Enter instruction
            query = st.text_input(
                "Enter your intruction here 👇. To end conversation, write terminar# then number of answer to save or all, ex. terminar#1 or terminar#all"
            )
            if (
                st.session_state["select_file_faiss_30"] != None
                and len(query) > 5
                and st.session_state["checkbox_30"]
            ) or (
                st.session_state["select_file_faiss_30"] == None
                and len(query) > 5
                and not st.session_state["checkbox_30"]
            ):
                # Col 2 = row1_2
                with row1_2:
                    if (
                        st.session_state["select_file_faiss_30"]
                        != st.session_state["name_file_kb_faiss_selected_30"]
                    ):
                        # use all files in Faiss or only one file
                        st.session_state["retriever_30"] = None
                        logging.info(f'file path vectorstore {st.session_state["select_file_faiss_30"]}')
                        if st.session_state["checkbox_30"]:
                            st.session_state["retriever_30"] = st.session_state["vectorstore_30"].as_retriever(
                                search_kwargs={"k": 3},
                                filter={
                                    "filename": str(
                                        st.session_state["select_file_faiss_30"]
                                    )
                                },
                            )
                        else:
                            st.session_state["retriever_30"] = st.session_state["vectorstore_30"].as_retriever(
                                search_kwargs={"k": 3},
                            )
                        # keep status in memory
                        
                        st.session_state["name_file_kb_faiss_selected_30"] = (
                            st.session_state["select_file_faiss_30"]
                        )
                    else:
                        st.session_state["name_file_kb_faiss_selected_30"] =  st.session_state["select_file_faiss_30"]

                    # create runnable with message history
                    if st.session_state["conversational_rag_chain_30"] == None:
                        conversational_rag_chain = create_conversational_rag_chain(
                            llm=st.session_state["llm_30"],
                            retriever=st.session_state["retriever_30"],
                            contex_q_prompt=contextualize_q_prompt,
                            qaprompt=qa_prompt,
                            store=st.session_state["store_30"],
                        )
                    else:
                        conversational_rag_chain = st.session_state[
                            "conversational_rag_chain_30"
                        ]

                    if len(query) > 5:
                        if "terminar#" in query:  # end conversation
                            reload_page_kb_faiss(
                                st,
                                df,
                                fname,
                                query,
                                placeholder_30,
                            )
                        # if new query
                        if (
                            query != st.session_state["current_prompt_30"]
                            and st.session_state["buttom_visualiza_faiss_clicked_30"]
                            == True
                        ):
                            st.session_state["docs_context_names_30"] = []
                            st.session_state["docs_context_30"] = []

                            st.session_state["buttom_visualiza_faiss_clicked_30"] = False
                        if query != st.session_state["current_prompt_30"]:
                            
                            result = conversational_rag_chain.invoke(
                                {"input": query},
                                config={
                                    "configurable": {"session_id": "abc123"}
                                },  # constructs a key "abc123" in `store`.
                            )
                            if result["answer"] == None:
                                st.write("No answer found")
                            else:
                                # update list answers and queries
                                update_list_answers_queries(st, result, query, num="30")

                                with st.expander(
                                    "Conversation with model 👇",
                                    expanded=st.session_state["expander_30"],
                                ):
                                    # create text to post in text area
                                    textvalue = sumup_history(st, num="30")
                                    st.session_state["answer_prompt_30"] = textvalue

                                    if len(result["chat_history"]) > 1:
                                        st.session_state[
                                            "history_conversation_with_model_30"
                                        ] = result["chat_history"]

                                    upload_state = st.text_area(
                                        "Status selection",
                                        value=st.session_state["answer_prompt_30"],
                                        key="text_30",
                                        height=600,
                                    )
                                    if (
                                        st.button(
                                            "Visualiza Documents Context Use",
                                            key="buttom_visualiza_faiss_30",
                                        )
                                        or st.session_state[
                                            "buttom_visualiza_faiss_clicked_30"
                                        ]
                                        == True
                                    ):
                                        st.session_state[
                                            "buttom_visualiza_faiss_clicked_30"
                                        ] = True

                                        st.session_state["current_prompt_30"] = query
                                        visualiza_context_faiss(st, result, num="30")

    except:
        st.session_state["salir_30"] = True
        # get the sys stack and log to gcloud
        placeholder.empty()
        text = print_stack()
        text = "Gemini Page 30" + text
        logging.error(text)

if __name__ == "__main__":

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    PROJECT_DIR = path.parent.absolute()
    DOCS_DIR = os.path.join(PROJECT_DIR, "kb", "docs")

    # Create folders
    OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(PROJECT_DIR)
    pname_no_case, pname2_no_case, df_answers_no_case = open_table_answers_no_case(
        ANSWERS_DIR
    )
    logging.info(f"PROJECT DIR: {PROJECT_DIR}, this folder: {ROOT_DIR}, Documents folder: {DOCS_DIR}")
    onlyfiles = [
        f for f in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, f))
    ]

    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    #go to login page if not authenticated
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "main.py"
        st.switch_page("main.py")

    if "salir_30" not in st.session_state:
        st.session_state["salir_30"] = False  

    if st.session_state["salir_30"] == False:  
        placeholder_30 = st.empty()
        global col1, col2
        with placeholder_30.container():

            col1, col2 = 2, 3
            # config Session
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
            # get gemini model
            if "llm_30" not in st.session_state:
                st.session_state["llm_30"]  = init_llm(model=config.get('MODEL'), credentials=vertex_credentials) 
                logging.info(f"Model loaded: {config.get('MODEL')}")
            # get embeddings model
            if "embeddings_30" not in st.session_state:
                st.session_state["embeddings_30"] = init_google_embeddings(config=config, credentials=vertex_credentials, google_api_key=google_api_key)
                logging.info(f"Embeddings loaded: {config.get('EMBEDDINGS2')}")
            # Vectorstore
            if "vectorstore_30" not in st.session_state:
                path_faiss = os.path.join(PROJECT_DIR, "kb","faiss")
                st.session_state["vectorstore_30"] = FAISS.load_local(
                    folder_path=path_faiss,
                    embeddings=st.session_state["embeddings_30"],
                    index_name="forensic",
                    allow_dangerous_deserialization=True,
                )
                logging.info(f"Gemini Page 30: Embeddings {config.get('EMBEDDINGS2')} and Vector Store faiss loaded from {path_faiss}")
            # Initialize

            main(

                col1=col1,
                col2=col2,
                onlyfiles=onlyfiles,
                fname=pname_no_case,
                df=df_answers_no_case,
                placeholder=placeholder_30,
            )
