import streamlit as st
import os
from pathlib import Path
import json
from dotenv import dotenv_values
from pericial.gemini_fn import (
    secciones,
    get_embeddings_model,
    get_pinecone_objects,
    pericial_prompt_selected,
)
from google.oauth2 import service_account
import vertexai
from src.helpers import visualiza_pericial
from src.files import open_table_periciales

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "table")
# create durs if does not exists
os.makedirs(DATA_DIR, exist_ok=True)

# open periciales table
fname, fname2, df = open_table_periciales(DATA_DIR)


def main(embeddings, index, vectorstore, placeholder):
    """
    main function to add prompts
    params:
    embeddings (GoogleGenerativeAIEmbeddings): model to generate embeddings
    index (Pinecone.Index): vector store to save embeddings
    vectorstore (PineconeVectorStore): vector store to save embeddings
    placeholder (str): application container
    """

    if "embeddings" not in st.session_state:
        st.session_state["embeddings"] = embeddings
    if "index" not in st.session_state:
        st.session_state["index"] = index
    if "vectorstore" not in st.session_state:
        st.session_state["vectorstore"] = vectorstore
    if "pericial_prompt_selected" not in st.session_state:
        st.session_state["pericial_prompt_selected"] = False
    if "seccion_introduced" not in st.session_state:
        st.session_state["seccion_introduced"] = ""

    st.title("Similarity Search Forensic Reports")
    title = st.text_area(
        "Introduce texto a Buscar Pericial separa con una # y dame el numero de documentos a buscar 👇",
        height=100,
        key="search_pericial",
        placeholder="Ejemplo: texto a buscar aqui y no puede haber este caracter-->#  10",
    )
    # if salir kill container
    if st.button("Salir"):
        placeholder.empty()
        st.stop()

    if len(title) > 0:
        seccion = st.selectbox(
            "selecciona seccion 👇",
            secciones,
            index=None,
            key="select_box",
        )
        if seccion:
            numero = title.split("#")[-1].strip()
            title = title.split("#")[0].strip()
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
                    itemlist = str(match["score"]) + ", " + match["metadata"]["text"]

                    list_matches_textos.append(itemlist)
                seccion2 = st.selectbox(
                    "selecciona match 👇",
                    list_matches_textos,
                    index=None,
                    key="select_box_2",
                    on_change=pericial_prompt_selected,
                    args=[st],
                )
                if seccion2 and st.session_state["pericial_prompt_selected"] == True:
                    visualiza_pericial(st, df, list_matches_textos, list_matches)


if __name__ == "__main__":
    # read config from .env file
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    path = Path(ROOT_DIR)
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    placeholder_search = st.empty()
    with placeholder_search.container():
        config = dotenv_values(os.path.join(path.parent.absolute(), "keys", ".env"))
        # key access gemini
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = config.get("GEMINI-API-KEY")
        if "PINECONE_API_KEY" not in os.environ:
            os.environ["PINECONE_API_KEY"] = config.get("PINECONE_API_KEY")
        if "PINECONE_INDEX_NAME" not in os.environ:
            os.environ["PINECONE_INDEX_NAME"] = "forensic"
        # load GCP service account
        with open(
            os.path.join(
                path.parent.absolute(), "keys", "complete-tube-421007-208a4862c992.json"
            )
        ) as source:
            info = json.load(source)
        # Login to Vertex AI
        vertex_credentials = service_account.Credentials.from_service_account_info(info)
        vertexai.init(
            project=config["PROJECT"],
            location=config["REGION"],
            credentials=vertex_credentials,
        )
        # get embeddings model
        embeddings = get_embeddings_model(model_name=config.get("EMBEDDINGS"))
        # get Pinecone objects
        index, vectorstore = get_pinecone_objects(
            config=config, embeddings=embeddings, index_name="forensic"
        )

        main(
            embeddings=embeddings,
            index=index,
            vectorstore=vectorstore,
            placeholder=placeholder_search,
        )
