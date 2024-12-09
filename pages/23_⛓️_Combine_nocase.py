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
    open_table_answers_no_case,
)
from dotenv import dotenv_values
from google.oauth2 import service_account
import vertexai
from src.utils import create_client_logging
from src.helpers import (
    visualiza_display_page,
    visualiza_pericial,
    init_visualiza,
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

# OPen Necessary tables
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
# open table answer final no case
pname_no_case, pname2_no_case, df_answers_no_case = open_table_answers_no_case(
    ANSWERS_DIR
)
# open periciales table
DATA_DIR = os.path.join(PROJECT_DIR, "pericial", "table")
fname, fname2, df = open_table_periciales(DATA_DIR)
logging.info(f"PROJECT DIR: {PROJECT_DIR}, this folder: {ROOT_DIR}, Data folder: {DATA_DIR}")

# fill the selector with name of the prompt and timestamp
def concat_date_row(row):
    return f"{row['filename']} - {row['timestamp']}"


# create list of files and answers concatenate filename + timestamp
df_answers_no_case["file_and_answer"] = df_answers_no_case.apply(
    concat_date_row, axis=1
)

def change_state_23(session, pp):
    """
    change state after leave conversation
    params:
    st (streamlit): streamlit object
    pp (streamlit.empty): placeholder

    """
    reset_session_num(session,"23")
    pp.empty()
    del pp
    session.empty()
    session.stop()
    return

def main( col1, col2, placeholder):
    """
    main loop
    Params:

        param col1: column 1
        param col2: column 2
        param placeholder: placeholder
    """
    with placeholder.container():
        if "vcol1doc_23" in st.session_state and "vcol2doc_23" in st.session_state:
            col1 = st.session_state["vcol1doc_23"]
            col2 = st.session_state["vcol2doc_23"]

        row1_1, row1_2 = st.columns((col1, col2))
        # Initialice state
        if "init_run_23" not in st.session_state:
            st.session_state["init_run_23"] = False
        if st.session_state["init_run_23"] == False:
            init_session_num(st, ss, "23", col1, col2, conf["23"]["config_23"], None)

        with row1_1:
            # columna 1
            if st.button("Salir", on_click=change_state_23, args=(st, placeholder)):
                    logging.info("Salir and writing history")

            selection_dict = file_selector(st, df_answers_no_case, "23")
            if (
                len(selection_dict.keys()) >= 5
                and st.session_state["file_prompt_selected_visualiza_23"] == False
                and st.session_state["file_and_answer_select_has_changed_23"] == True
            ):

                visualiza_display_page(st=st, selection_dict=selection_dict, num="23")

            elif (
                st.session_state["file_and_answer_select_has_changed_23"] == True
                and st.session_state["file_prompt_selected_visualiza_23"] == True
                and st.session_state["chat_true_23"] == "no_chat"
            ):
                title = st.text_area(
                    "Introduce texto a Buscar Pericial separa con una # y dame el numero de documentos a buscar 👇",
                    height=100,
                    key="search_pericial_23",
                    placeholder="Ejemplo: texto a buscar aqui y no puede haber este caracter--># 10",
                    disabled=st.session_state["buttom_send_visualiza_23"],
                )

                if len(title) > 0:
                    seccion = st.selectbox(
                        "selecciona seccion 👇",
                        secciones,
                        index=None,
                        key="select_box_231",
                        on_change=section_prompt_selected,
                        args=[st, "23"],
                        disabled=st.session_state["buttom_send_visualiza_23"],
                    )
                    if seccion and st.session_state["section_prompt_selected_23"] == True:

                        numero = title.split("#")[-1].strip()
                        title = title.split("#")[0].strip()
                        st.session_state["prompt_introduced_23"] = title
                        v_query = st.session_state["embeddings_23"].embed_query(title)
                        r = st.session_state["index_23"].query(
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
                            seccion2 = st.selectbox(
                                "selecciona match 👇",
                                list_matches_textos,
                                index=None,
                                key="select_box_23",
                                on_change=pericial_prompt_selected,
                                args=[st, "23"],
                                disabled=st.session_state["buttom_send_visualiza_23"],
                            )
                            # and st.session_state["pericial_prompt_selected"] == True
                            if (
                                st.session_state["pericial_prompt_selected_23"] == True
                                and st.session_state["chat_true_23"] == "no_chat"
                                and st.session_state["b_accept_inside_pericial_23"] == False
                            ):

                                visualiza_pericial(
                                    st, df, list_matches_textos, list_matches, "23"
                                )
                                file = (
                                    st.session_state["answer_introduced_23"].get("filename")
                                    + f" + prompt: {title}"
                                    + f" + Seccion: {seccion}"
                                )
                                st.session_state["prompt_combined_filename_23"] = file

            if (
                st.session_state["chat_true_23"] == "chat activo"
                and st.session_state["b_accept_inside_pericial_23"] == True
            ):
                col1 = 30
                col2 = 70
                st.session_state["chat_true_23"] = "chat activo"
                st.session_state["b_accept_inside_pericial_23"] = True
                st.session_state["buttom_send_visualiza_23"] = True

        with row1_2:
            if (
                len(st.session_state["seccion_introduced_23"]) > 10
                and len(st.session_state["answer_introduced_23"].keys()) >= 5
            ):
                with st.expander(
                    "���️Instruccion to send to Gemini 👇",
                    expanded=st.session_state["expander_23"],
                ):
                    st.session_state["instruction_to_be_send_23"] = (
                        "Formatear este texto: \n"
                        + st.session_state["answer_introduced_23"].get("respuesta_chat")
                        + "\n\n"
                        + "Usa este Ejemplo:"
                        + "\n\n"
                        + st.session_state["seccion_introduced_23"]
                    )
                    st.text_area(
                        "Intruction to be send to gemini Gemini",
                        height=300,
                        key="prompt_1_sample_23",
                        value=st.session_state["instruction_to_be_send_23"],
                        disabled=st.session_state["buttom_send_visualiza_23"],
                    )
                if st.button(
                    "Send Instruction",
                    disabled=st.session_state["buttom_send_visualiza_23"],
                ):
                    st.session_state["chat_true_23"] = "chat activo"
                    st.session_state["vcol1doc_23"] = 30
                    st.session_state["vcol2doc_23"] = 70
                    st.session_state["buttom_send_visualiza_23"] = True
                    st.session_state["expander_23"] = False
                    st.rerun()
                # Conversacion con el modelo
                if st.session_state["chat_true_23"] == "chat activo":
                    # change status
                    st.session_state["expander_23"] = False
                    st.session_state["chat_true_23"] = "chat activo"
                    st.session_state["buttom_send_visualiza_23"] = True

                    prompt = st.chat_input("Enter your questions here", disabled=not input)
                    if prompt == "terminar":
                        # write answer and reset page pfname, pfname2, df_answers_final
                        reload_page_combina(
                            st,
                            pfname,
                            df_answers_final,
                            placeholder,
                            num="23",
                        )
                    else:
                        if st.session_state["initialized_23"] == "False":

                            response = get_chat_response(
                                st.session_state["llm_23"],
                                st.session_state["instruction_to_be_send_23"],
                            )
                            st.session_state["chat_answers_history_23"].append(response)
                            st.session_state["user_prompt_history_23"].append(
                                st.session_state["instruction_to_be_send_23"]
                            )
                            st.session_state["chat_history_23"].append(
                                (st.session_state["instruction_to_be_send_23"], response)
                            )
                            st.session_state["initialized_23"] = "True"
                            st.session_state["buttom_send_visualiza_23"] = True
                        elif st.session_state["initialized_23"] == "True":
                            prompt1 = [f"""{prompt} """]
                            # actualiza status
                            st.session_state["instruction_to_be_send_23"] = prompt
                            response = get_chat_response(st.session_state["llm_23"], prompt1)
                            # actualiza buffer chat
                            st.session_state["chat_answers_history_23"].append(response)
                            st.session_state["user_prompt_history_23"].append(prompt1[0])
                            st.session_state["chat_history_23"].append((prompt1[0], response))
                            st.session_state["buttom_send_visualiza_23"] = True
                        # write chat in window
                        if len(st.session_state["chat_answers_history_23"]) > 0:
                            list1 = copy.deepcopy(st.session_state["chat_answers_history_23"])
                            list2 = copy.deepcopy(st.session_state["user_prompt_history_23"])

                            if len(st.session_state["chat_answers_history_23"]) > 1:
                                list1.reverse()

                            if len(st.session_state["user_prompt_history_23"]) > 1:
                                list2.reverse()

                            for i, j in zip(list1, list2):
                                message1 = st.chat_message("user")
                                message1.write(j)
                                message2 = st.chat_message("assistant")
                                message2.write(i)
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

    if "salir_23" not in st.session_state:
        st.session_state["salir_23"] = False  

    if st.session_state["salir_23"] == False:  
    # create container
        placeholder_23 = st.empty()
        with placeholder_23.container():
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
            if "llm_23" not in st.session_state:
                st.session_state["llm_23"]  = init_model(config)
                st.session_state["llm_23"] = st.session_state["llm_23"].start_chat(response_validation=False)
                logging.info(f"Model loaded: {config.get('MODEL')}")

            # get embeddings model
            if "embeddings_23" not in st.session_state:
                st.session_state["embeddings_23"] = get_embeddings_model(model_name=config.get("EMBEDDINGS"))
                logging.info(f"Embeddings loaded: {config.get('EMBEDDINGS')}")
            
            if "index_23" not in st.session_state:
                # get Pinecone objects
                st.session_state["index_23"], st.session_state["vectorstore_23"] = get_pinecone_objects(
                config=config, embeddings=st.session_state["embeddings_23"], index_name="forensic"
            )
                logging.info("Gemini Page 23: Embeddings and Pinecone loaded")
            main(

                col1=col1,
                col2=col2,
                placeholder=placeholder_23,
            )
