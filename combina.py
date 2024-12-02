import streamlit as st
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

# OPEN necessary tables
# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Create folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(ROOT_DIR)
# open table with all prompts
pname, pname2, df_answers = open_table_answers(ANSWERS_DIR)
# open table answer final
pfname, pfname2, df_answers_final = open_table_answers_final(ANSWERS_DIR)
# open periciales table
DATA_DIR = os.path.join(ROOT_DIR, "pericial", "table")
fname, fname2, df = open_table_periciales(DATA_DIR)


# fill the selector with name of the prompt and timestamp
def concat_date_row(row):
    return f"{row['filename']} - {row['timestamp']}"


# create list of files and answers concatenate filename + timestamp
df_answers["file_and_answer"] = df_answers.apply(concat_date_row, axis=1)


def main(model, embeddings, index, vectorstore, col1, col2, placeholder):
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

    if "vcol1" in st.session_state and "vcol2" in st.session_state:
        col1 = st.session_state["vcol1"]
        col2 = st.session_state["vcol2"]

    row1_1, row1_2 = st.columns((col1, col2))
    # Initialice state
    if "init_run" not in st.session_state:
        st.session_state["init_run"] = False
    if st.session_state["init_run"] == False:
        init_visualiza(st, model, embeddings, index, vectorstore, col1, col2)

    with row1_1:
        # columna 1
        if st.button("Salir"):
            placeholder.empty()
            st.stop()
        selection_dict = file_selector(st, df_answers)
        if (
            len(selection_dict.keys()) >= 5
            and st.session_state["file_prompt_selected_visualiza"] == False
            and st.session_state["file_and_answer_select_has_changed"] == True
        ):

            visualiza_display_page(st=st, selection_dict=selection_dict)

        elif (
            st.session_state["file_and_answer_select_has_changed"] == True
            and st.session_state["file_prompt_selected_visualiza"] == True
            and st.session_state["chat_true"] == "no_chat"
        ):
            title = st.text_area(
                "Introduce texto a Buscar Pericial separa con una # y dame el numero de documentos a buscar 👇",
                height=100,
                key="search_pericial",
                placeholder="Ejemplo: texto a buscar aqui y no puede haber este caracter--># 10",
                disabled=st.session_state["buttom_send_visualiza"],
            )

            if len(title) > 0:
                seccion = st.selectbox(
                    "selecciona seccion 👇",
                    secciones,
                    index=None,
                    key="select_box",
                    on_change=section_prompt_selected,
                    args=[st],
                    disabled=st.session_state["buttom_send_visualiza"],
                )
                if seccion and st.session_state["section_prompt_selected"] == True:

                    numero = title.split("#")[-1].strip()
                    title = title.split("#")[0].strip()
                    st.session_state["prompt_introduced"] = title
                    v_query = embeddings.embed_query(title)
                    r = index.query(
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
                            key="select_box_2",
                            on_change=pericial_prompt_selected,
                            args=[st],
                            disabled=st.session_state["buttom_send_visualiza"],
                        )
                        # and st.session_state["pericial_prompt_selected"] == True
                        if (
                            st.session_state["pericial_prompt_selected"] == True
                            and st.session_state["chat_true"] == "no_chat"
                            and st.session_state["b_accept_inside_pericial"] == False
                        ):

                            visualiza_pericial(
                                st, df, list_matches_textos, list_matches
                            )
                            file = (
                                st.session_state["answer_introduced"].get("filename")
                                + f" + prompt: {title}"
                                + f" + Seccion: {seccion}"
                            )
                            st.session_state["prompt_combined_filename"] = file

        if (
            st.session_state["chat_true"] == "chat activo"
            and st.session_state["b_accept_inside_pericial"] == True
        ):
            col1 = 30
            col2 = 70
            st.session_state["chat_true"] = "chat activo"
            st.session_state["b_accept_inside_pericial"] = True
            st.session_state["buttom_send_visualiza"] = True

    with row1_2:
        if (
            len(st.session_state["seccion_introduced"]) > 10
            and len(st.session_state["answer_introduced"].keys()) >= 5
        ):
            with st.expander(
                "���️Instruccion to send to Gemini 👇",
                expanded=st.session_state["expander_1"],
            ):
                st.session_state["instruction_to_be_send"] = (
                    "Formatear este texto: \n"
                    + st.session_state["answer_introduced"].get("respuesta_chat")
                    + "\n\n"
                    + "Usa este Ejemplo:"
                    + "\n\n"
                    + st.session_state["seccion_introduced"]
                )
                st.text_area(
                    "Intruction to be send to gemini Gemini",
                    height=300,
                    key="prompt_1_sample",
                    value=st.session_state["instruction_to_be_send"],
                    disabled=st.session_state["buttom_send_visualiza"],
                )
            if st.button(
                "Send Instruction",
                disabled=st.session_state["buttom_send_visualiza"],
            ):
                st.session_state["chat_true"] = "chat activo"
                st.session_state["vcol1"] = 30
                st.session_state["vcol2"] = 70
                st.session_state["buttom_send_visualiza"] = True
                st.session_state["expander_1"] = False
                st.rerun()
            # Conversacion con el modelo
            if st.session_state["chat_true"] == "chat activo":
                # change status
                st.session_state["expander_1"] = False
                st.session_state["chat_true"] = "chat activo"
                st.session_state["buttom_send_visualiza"] = True

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
                    )
                else:
                    if st.session_state["initialized"] == "False":

                        response = get_chat_response(
                            st.session_state["chat"],
                            st.session_state["instruction_to_be_send"],
                        )
                        st.session_state["chat_answers_history"].append(response)
                        st.session_state["user_prompt_history"].append(
                            st.session_state["instruction_to_be_send"]
                        )
                        st.session_state["chat_history"].append(
                            (st.session_state["instruction_to_be_send"], response)
                        )
                        st.session_state["initialized"] = "True"
                        st.session_state["buttom_send_visualiza"] = True
                    elif st.session_state["initialized"] == "True":
                        prompt1 = [f"""{prompt} """]
                        # actualiza status
                        st.session_state["instruction_to_be_send"] = prompt
                        response = get_chat_response(st.session_state["chat"], prompt1)
                        # actualiza buffer chat
                        st.session_state["chat_answers_history"].append(response)
                        st.session_state["user_prompt_history"].append(prompt1[0])
                        st.session_state["chat_history"].append((prompt1[0], response))
                        st.session_state["buttom_send_visualiza"] = True
                    # write chat in window
                    if len(st.session_state["chat_answers_history"]) > 0:
                        list1 = copy.deepcopy(st.session_state["chat_answers_history"])
                        list2 = copy.deepcopy(st.session_state["user_prompt_history"])

                        if len(st.session_state["chat_answers_history"]) > 1:
                            list1.reverse()

                        if len(st.session_state["user_prompt_history"]) > 1:
                            list2.reverse()

                        for i, j in zip(list1, list2):
                            message1 = st.chat_message("user")
                            message1.write(j)
                            message2 = st.chat_message("assistant")
                            message2.write(i)
    return


if __name__ == "__main__":
    global col1, col2
    col1, col2 = 50, 50
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    #go to login page if not authenticated
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "pages/home.py"
        st.switch_page("pages/home.py")
    # create container
    placeholder_combina = st.empty()
    with placeholder_combina.container():
        config = dotenv_values("keys/.env")
        with open("keys/complete-tube-421007-208a4862c992.json") as source:
            info = json.load(source)

        vertex_credentials = service_account.Credentials.from_service_account_info(info)
        client = create_client_logging(vertex_credentials=vertex_credentials)
        # Retrieves a Cloud Logging handler based on the environment
        # you're running in and integrates the handler with the
        # Python logging module. By default this captures all logs
        # at INFO level and higher

        client.setup_logging()

        vertexai.init(
            project=config["PROJECT"],
            location=config["REGION"],
            credentials=vertex_credentials,
        )
        # get gemini model
        model = init_model(config)
        logging.info("Gemini display Page: Model loaded")

        # get embeddings model
        embeddings = get_embeddings_model(model_name=config.get("EMBEDDINGS"))
        # get Pinecone objects
        index, vectorstore = get_pinecone_objects(
            config=config, embeddings=embeddings, index_name="forensic"
        )
        logging.info("Gemini display Page: Embeddings and Pinecone loaded")
        main(
            model=model,
            embeddings=embeddings,
            index=index,
            vectorstore=vectorstore,
            col1=col1,
            col2=col2,
            placeholder=placeholder_combina,
        )
