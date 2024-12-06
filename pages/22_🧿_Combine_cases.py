import streamlit as st
from streamlit import session_state as ss
import os
import json
import copy
from src.files import (
    open_table_answers,
    create_folders,
    open_table_answers_final,
    file_selector,
    open_table_periciales,
)
from dotenv import dotenv_values
from google.oauth2 import service_account
import vertexai
from src.utils import create_client_logging
from src.helpers import (
    visualiza_display_page,
    visualiza_pericial,
    reload_page_combina,
)
from src.work_gemini import init_model, get_chat_response
from pericial.gemini_fn import (
    secciones,
    get_embeddings_model,
    get_pinecone_objects,
    pericial_prompt_selected,
    section_prompt_selected,
)
import logging
from pathlib import Path
from src.utils import print_stack
from src.maps import config as conf, init_session_num, reset_session_num
from IPython import embed

# OPEN necessary tables
# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT_DIR)
PROJECT_DIR = path.parent.absolute().as_posix()
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(PROJECT_DIR)
# open table with all prompts
pname, pname2, df_answers = open_table_answers(ANSWERS_DIR)
# open table answer final
pfname, pfname2, df_answers_final = open_table_answers_final(ANSWERS_DIR)
# open periciales table
DATA_DIR = os.path.join(PROJECT_DIR, "pericial", "table")
fname, fname2, df = open_table_periciales(DATA_DIR)

logging.info(f"PROJECT DIR: {PROJECT_DIR}, this folder: {ROOT_DIR}, Data folder: {DATA_DIR}")


# fill the selector with name of the prompt and timestamp
def concat_date_row(row):
    return f"{row['filename']} - {row['timestamp']}"


# create list of files and answers concatenate filename + timestamp
df_answers["file_and_answer"] = df_answers.apply(concat_date_row, axis=1)

def change_state_22(session, placeholder):
    """
    change state after leave conversation
    params:
    st (streamlit): streamlit object
    placeholder (streamlit.empty): placeholder

    """
    placeholder.empty()
    del placeholder
    reset_session_num(session,"22")
    st.stop()
    return

def main(col1, col2, placeholder):
    """
    main loop
    Params:
        param model: gemini model
        param embeddings: embeddings model
        param index: pinecone index
        param vectorstore: pinecone vectorstore
        param col1: column 1
        param col2: column 2
        param placeholder: placeholder
    """

    if "vcol1doc_22" in st.session_state and "vcol2doc_22" in st.session_state:
        col1 = st.session_state["vcol1doc_22"]
        col2 = st.session_state["vcol2doc_22"]

    row1_1, row1_2 = st.columns((col1, col2))
    # Initialice state
    if "init_run_22" not in st.session_state:
        st.session_state["init_run_22"] = False
    if st.session_state["init_run_22"] == False:

        init_session_num(st, ss, "22", col1, col2, conf["22"]["config_22"], None)
    try:
        with row1_1:
            # columna 1
            if st.button("Salir", on_click=change_state_22, args=(st, placeholder)):
                    logging.info("Salir and writing history")

            selection_dict = file_selector(st, df_answers, num="22")
            if (
                len(selection_dict.keys()) >= 5
                and st.session_state["file_prompt_selected_visualiza_22"] == False
                and st.session_state["file_and_answer_select_has_changed_22"] == True
            ):

                visualiza_display_page(st=st, selection_dict=selection_dict, num="22")

            elif (
                st.session_state["file_and_answer_select_has_changed_22"] == True
                and st.session_state["file_prompt_selected_visualiza_22"] == True
                and st.session_state["chat_true_22"] == "no_chat"
            ):
                title = st.text_area(
                    "Introduce texto a Buscar Pericial separa con una # y dame el numero de documentos a buscar 👇",
                    height=100,
                    key="search_pericial_22",
                    placeholder="Ejemplo: texto a buscar aqui y no puede haber este caracter--># 10",
                    disabled=st.session_state["buttom_send_visualiza_22"],
                )

                if len(title) > 0:
                    seccion = st.selectbox(
                        "selecciona seccion 👇",
                        secciones,
                        index=None,
                        key="select_box_221",
                        on_change=section_prompt_selected,
                        args=[st, "22"],
                        disabled=st.session_state["buttom_send_visualiza_22"],
                    )
                    if seccion and st.session_state["section_prompt_selected_22"] == True:

                        numero = title.split("#")[-1].strip()
                        title = title.split("#")[0].strip()
                        st.session_state["prompt_introduced_22"] = title
                        v_query = st.session_state["embeddings_22"].embed_query(title)
                        r = st.session_state["index_22"].query(
                            vector=list(v_query),
                            top_k=int(numero),
                            include_metadata=True,
                            filter={"sections": seccion},
                        )
                        if len(r["matches"]) > 0:
                            list_matches = []
                            list_matches_textos = []
                            for match in r["matches"]:

                                list_matches.append(match["id"])
                                itemlist = (
                                    str(match["score"]) + ", " + match["metadata"]["text"]
                                )

                                list_matches_textos.append(itemlist)
                            _ = st.selectbox(
                                "selecciona match 👇",
                                list_matches_textos,
                                index=None,
                                key="select_box_22",
                                on_change=pericial_prompt_selected,
                                args=[st, "22"], # here is the number of the key selector which is select_box_22
                                disabled=st.session_state["buttom_send_visualiza_22"],
                            )
                            # and st.session_state["pericial_prompt_selected_22"] == True
                            if (
                                st.session_state["pericial_prompt_selected_22"] == True
                                and st.session_state["chat_true_22"] == "no_chat"
                                and st.session_state["b_accept_inside_pericial_22"] == False
                            ):

                                visualiza_pericial(
                                    st, df, list_matches_textos, list_matches, "22"
                                )
                                file = (
                                    st.session_state["answer_introduced_22"].get("filename")
                                    + f" + prompt: {title}"
                                    + f" + Seccion: {seccion}"
                                )
                                st.session_state["prompt_combined_filename_22"] = file

            if (
                st.session_state["chat_true_22"] == "chat activo"
                and st.session_state["b_accept_inside_pericial_22"] == True
            ):
                col1 = 30
                col2 = 70
                st.session_state["chat_true_22"] = "chat activo"
                st.session_state["b_accept_inside_pericial_22"] = True
                st.session_state["buttom_send_visualiza_22"] = True

        with row1_2:
            if (
                len(st.session_state["seccion_introduced_22"]) > 10
                and len(st.session_state["answer_introduced_22"].keys()) >= 5
            ):
                with st.expander(
                    "���️Instruccion to send to Gemini 👇",
                    expanded=st.session_state["expander_22"],
                ):
                    st.session_state["instruction_to_be_send_22"] = (
                        "Formatear este texto: \n"
                        + st.session_state["answer_introduced_22"].get("respuesta_chat")
                        + "\n\n"
                        + "Usa este Ejemplo:"
                        + "\n\n"
                        + st.session_state["seccion_introduced_22"]
                    )
                    st.text_area(
                        "Intruction to be send to gemini Gemini",
                        height=300,
                        key="prompt_1_sample_22",
                        value=st.session_state["instruction_to_be_send_22"],
                        disabled=st.session_state["buttom_send_visualiza_22"],
                    )
                if st.button(
                    "Send Instruction",
                    disabled=st.session_state["buttom_send_visualiza_22"],
                ):
                    st.session_state["chat_true_22"] = "chat activo"
                    st.session_state["vcol1doc_22"] = 30
                    st.session_state["vcol2doc_22"] = 70
                    st.session_state["buttom_send_visualiza_22"] = True
                    st.session_state["expander_22"] = False
                    st.rerun()
                # Conversacion con el modelo
                if st.session_state["chat_true_22"] == "chat activo":
                    # change status
                    st.session_state["expander_22"] = False
                    st.session_state["chat_true_22"] = "chat activo"
                    st.session_state["buttom_send_visualiza_22"] = True

                    prompt = st.chat_input("Enter your questions here", disabled=not input)
                    if prompt == "terminar":
                        # write answer and reset page pfname, pfname2, df_answers_final
                        reload_page_combina(
                            st,
                            model,
                            embeddings,
                            index,
                            vectorstore,
                            pfname,
                            df_answers_final,
                            placeholder,
                            num="22",
                        )
                    else:
                        if st.session_state["initialized_22"] == "False":

                            response = get_chat_response(
                                st.session_state["llm_22"],
                                st.session_state["instruction_to_be_send_22"],
                            )
                            st.session_state["chat_answers_history_22"].append(response)
                            st.session_state["user_prompt_history_22"].append(
                                st.session_state["instruction_to_be_send_22"]
                            )
                            st.session_state["chat_history_22"].append(
                                (st.session_state["instruction_to_be_send_22"], response)
                            )
                            st.session_state["initialized_22"] = "True"
                            st.session_state["buttom_send_visualiza_22"] = True
                        elif st.session_state["initialized_22"] == "True":
                            prompt1 = [f"""{prompt} """]
                            # actualiza status
                            st.session_state["instruction_to_be_send_22"] = prompt
                            response = get_chat_response(st.session_state["llm_22"], prompt1)
                            # actualiza buffer chat
                            st.session_state["chat_answers_history_22"].append(response)
                            st.session_state["user_prompt_history_22"].append(prompt1[0])
                            st.session_state["chat_history_22"].append((prompt1[0], response))
                            st.session_state["buttom_send_visualiza_22"] = True
                        # write chat in window
                        if len(st.session_state["chat_answers_history_22"]) > 0:
                            list1 = copy.deepcopy(st.session_state["chat_answers_history_22"])
                            list2 = copy.deepcopy(st.session_state["user_prompt_history_22"])

                            if len(st.session_state["chat_answers_history_22"]) > 1:
                                list1.reverse()

                            if len(st.session_state["user_prompt_history_22"]) > 1:
                                list2.reverse()

                            for i, j in zip(list1, list2):
                                message1 = st.chat_message("user")
                                message1.write(j)
                                message2 = st.chat_message("assistant")
                                message2.write(i)
    except Exception as e:
        st.session_state["salir_22"] = True
        # get the sys stack and log to gcloud
        placeholder.empty()
        text = print_stack()
        text = "Gemini Page 22" + text
        logging.error(text)           
    return


if __name__ == "__main__":
    global col1, col2

    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
   # access to keys and service account
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    PROJECT_DIR = path.parent.absolute().as_posix()
    #go to login page if not authenticated
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "main.py"
        st.switch_page("main.py")

    if "salir_22" not in st.session_state:
        st.session_state["salir_22"] = False  

    if st.session_state["salir_22"] == False:  
    # create container
        placeholder_22 = st.empty()
        with placeholder_22.container():
            col1, col2 = 50, 50
            config = dotenv_values(os.path.join(PROJECT_DIR, "keys", ".env"))
            with open(
                os.path.join(PROJECT_DIR, "keys", "complete-tube-421007-208a4862c992.json")
            ) as source:
                info = json.load(source)

            vertex_credentials = service_account.Credentials.from_service_account_info(info)
            # client = create_client_logging(vertex_credentials=vertex_credentials)
            # Retrieves a Cloud Logging handler based on the environment
            # you're running in and integrates the handler with the
            # Python logging module. By default this captures all logs
            # at INFO level and higher

            # client.setup_logging()

            vertexai.init(
                project=config["PROJECT"],
                location=config["REGION"],
                credentials=vertex_credentials,
            )
            # get gemini model
            if "llm_22" not in st.session_state:
                st.session_state["llm_22"]  = init_model(config)
                st.session_state["llm_22"] = st.session_state["llm_22"].start_chat(response_validation=False)
                logging.info(f"Model loaded: {config.get('MODEL')}")

            # get embeddings model
            if "embeddings_22" not in st.session_state:
                st.session_state["embeddings_22"] = get_embeddings_model(model_name=config.get("EMBEDDINGS"))
                logging.info(f"Embeddings loaded: {config.get('EMBEDDINGS')}")
            
            if "index_22" not in st.session_state:
                # get Pinecone objects
                st.session_state["index_22"], st.session_state["vectorstore_22"] = get_pinecone_objects(
                config=config, embeddings=st.session_state["embeddings_22"], index_name="forensic"
            )
                logging.info("Gemini Page 22: Embeddings and Pinecone loaded")
            main(

                col1=col1,
                col2=col2,
                placeholder=placeholder_22,
            )
