import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from src.helpers import init_session_faiss, reset_session_faiss, save_df_many
from src.files import open_table_answers_no_case, create_folders
from google.oauth2 import service_account
from dotenv import dotenv_values
import json
import vertexai
import streamlit as st
from langchain_community.vectorstores import FAISS
from pathlib import Path
from kb.templates import contextualize_q_prompt, qa_prompt
from kb.chains import (
    create_conversational_rag_chain,
)
from kb.controls import visualiza_context_faiss
from kb.utils import sumup_history, update_list_answers_queries
from src.utils import print_stack


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
    if st.session_state["select_file_faiss"] != None:
        filename = st.session_state["select_file_faiss"]
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


def change_checkbox_faiss(st):
    st.session_state["checkbox3"] = st.session_state["checkbox_faiss"]


def selected_file_kb(st):
    st.session_state["file_kb_faiss_selected"] = True


def main(vectorstore, llm, col1, col2, onlyfiles, fname, df, placeholder):
    """
    Main loop
    Args:
        st ([type]): session stramlit
        model ([type]): llm
        col1 ([type]): size col 1
        col2 ([type]): size col 2
        onlyfiles ([type]): list of files to fill selectbox
        fname ([type]): name dataframe filename  final aswers
        df ([type]): dataframe  final aswers
        placeholder ([type]): conatiner to reset
    """

    try:

        # if "vcol1mdoc" in st.session_state and "vcol2mdoc" in st.session_state:
        #    col1 = st.session_state["vcol1mdoc"]
        #    col2 = st.session_state["vcol2mdoc"]
        row1_1, row1_2 = st.columns((2, 3))

        # Initialize Vars
        if "init_run_faiss" not in st.session_state:
            st.session_state["init_run_faiss"] = False
        # if st.session_state["init_run_faiss"] == False:
        init_session_faiss(st, col1, col2, llm)
        if st.session_state["llm"] == None:
            st.session_state["llm"] = llm
        # Col 1 = row1_1
        with row1_1:
            seccion = st.selectbox(
                "Selecciona fichero 👇",
                onlyfiles,
                index=None,
                key="select_file_faiss",
                on_change=selected_file_kb,
                args=[st],
            )
            checkbox3 = st.checkbox(
                "Use only file seclected to search for Information",
                key="checkbox_faiss",
                on_change=change_checkbox_faiss,
                args=[st],
            )

            # Enter instruction
            query = st.text_input(
                "Enter your intruction here 👇. To end conversation, write terminar# then number of answer to save or all, ex. terminar#1 or terminar#all"
            )
            # if you press salir any time you close the conainer
            if st.button("Salir"):
                placeholder.empty()
                st.stop()
            if (
                st.session_state["select_file_faiss"] != None
                and len(query) > 5
                and st.session_state["checkbox3"]
            ) or (
                st.session_state["select_file_faiss"] == None
                and len(query) > 5
                and not st.session_state["checkbox3"]
            ):
                # Col 2 = row1_2
                with row1_2:
                    if (
                        st.session_state["select_file_faiss"]
                        != st.session_state["name_file_kb_faiss_selected"]
                    ):
                        # use all files in Faiss or only one file
                        retriever = None
                        print(st.session_state["select_file_faiss"])
                        if st.session_state["checkbox3"]:
                            retriever = vectorstore.as_retriever(
                                search_kwargs={"k": 3},
                                filter={
                                    "filename": str(
                                        st.session_state["select_file_faiss"]
                                    )
                                },
                            )
                        else:
                            retriever = vectorstore.as_retriever(
                                search_kwargs={"k": 3},
                            )
                        # keep status in memory
                        st.session_state["kb_faiss_retriever"] = retriever
                        st.session_state["name_file_kb_faiss_selected"] = (
                            st.session_state["select_file_faiss"]
                        )
                    else:
                        retriever = st.session_state["kb_faiss_retriever"]
                        st.session_state["name_file_kb_faiss_selected"] = (
                            st.session_state["select_file_faiss"]
                        )

                    # create runnable with message history
                    if st.session_state["conversational_rag_chain"] == None:
                        conversational_rag_chain = create_conversational_rag_chain(
                            llm=st.session_state["llm"],
                            retriever=st.session_state["kb_faiss_retriever"],
                            contex_q_prompt=contextualize_q_prompt,
                            qaprompt=qa_prompt,
                            store=st.session_state["store"],
                        )
                    else:
                        conversational_rag_chain = st.session_state[
                            "conversational_rag_chain"
                        ]

                    if len(query) > 5:
                        if "terminar#" in query:  # end conversation
                            reload_page_kb_faiss(
                                st,
                                df,
                                fname,
                                query,
                                placeholder_kb,
                            )
                        # if new query
                        if (
                            query != st.session_state["current_prompt"]
                            and st.session_state["buttom_visualiza_faiss_clicked"]
                            == True
                        ):
                            st.session_state["docs_context_names"] = []
                            st.session_state["docs_context"] = []

                            st.session_state["buttom_visualiza_faiss_clicked"] = False
                        if query != st.session_state["current_prompt"]:
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
                                update_list_answers_queries(st, result, query)

                                with st.expander(
                                    "Conversation with model 👇",
                                    expanded=st.session_state["expander_4"],
                                ):
                                    # create text to post in text area
                                    textvalue = sumup_history(st)
                                    st.session_state["answer_prompt"] = textvalue

                                    if len(result["chat_history"]) > 1:
                                        st.session_state[
                                            "history_conversation_with_model"
                                        ] = result["chat_history"]

                                    upload_state = st.text_area(
                                        "Status selection",
                                        value=st.session_state["answer_prompt"],
                                        key="text",
                                        height=600,
                                    )
                                    if (
                                        st.button(
                                            "Visualiza Documents Context Use",
                                            key="buttom_visualiza_faiss",
                                        )
                                        or st.session_state[
                                            "buttom_visualiza_faiss_clicked"
                                        ]
                                        == True
                                    ):
                                        st.session_state[
                                            "buttom_visualiza_faiss_clicked"
                                        ] = True

                                        st.session_state["current_prompt"] = query
                                        visualiza_context_faiss(st, result)

    except Exception as e:
        placeholder_kb.empty()
        # get the sys stack and log to gcloud
        text = print_stack()
        print(text)


if __name__ == "__main__":

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    DOCS_DIR = os.path.join(ROOT_DIR, "docs")
    path = Path(ROOT_DIR)
    path = path.parent.absolute()

    # Create folders
    OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(path)
    pname_no_case, pname2_no_case, df_answers_no_case = open_table_answers_no_case(
        ANSWERS_DIR
    )

    onlyfiles = [
        f for f in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, f))
    ]

    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    #go to login page if not authenticated
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "pages/home.py"
        st.switch_page("pages/home.py")
        
    placeholder_kb = st.empty()
    global col1, col2
    with placeholder_kb.container():

        col1, col2 = 2, 3
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        path = Path(ROOT_DIR)
        path = path.parent.absolute()

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

        # Vectorstore
        path_faiss = os.path.join(ROOT_DIR, "faiss")
        vectorstore = FAISS.load_local(
            folder_path=path_faiss,
            embeddings=GoogleGenerativeAIEmbeddings(
                model=config.get("EMBEDDINGS2"),
                credentials=vertex_credentials,
                google_api_key=google_api_key,
            ),
            index_name="forensic",
            allow_dangerous_deserialization=True,
        )
        # Initialize

        main(
            vectorstore=vectorstore,
            llm=llm,
            col1=col1,
            col2=col2,
            onlyfiles=onlyfiles,
            fname=pname_no_case,
            df=df_answers_no_case,
            placeholder=placeholder_kb,
        )
