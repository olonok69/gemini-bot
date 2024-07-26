import os
from st_pages import Page, show_pages, Section
import shutil
import streamlit as st
from dotenv import dotenv_values


def main():
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")

    st.title("Forensic Reports Tools. Powered by Gemini y Langchain")

    show_pages(
        [
            Page("pages/home.py", "Home", "🏠"),
            Section("--Sec-- Maintenance", "📃"),
            Page("add.py", "Add Entrance", "➕", is_section=False, in_section=True),
            Page(
                "modifica.py",
                "Modify entrance",
                "💱",
                is_section=False,
                in_section=True,
            ),
            Page(
                "delete.py",
                "Delete entrance",
                "❌",
                is_section=False,
                in_section=True,
            ),
            Section("--Sec-- Chat Gemini", "♊"),
            Page(
                "1_doc_esp.py", "1 Doc+prompt", "📝", is_section=False, in_section=True
            ),
            Page(
                "many_docs.py",
                "1+ Documentos",
                ":books:",
                is_section=False,
                in_section=True,
            ),
            Page(
                "combina.py",
                "Combine periciales",
                ":eye:",
                is_section=False,
                in_section=True,
            ),
            Page(
                "combina_nocase.py",
                "Combine KB",
                "🧿",
                is_section=False,
                in_section=True,
            ),
            Section("--Sec-- Periciales", "🧑‍⚕️"),
            Page(
                "pericial/search.py",
                "Similarity Search",
                "🕵️",
            ),
            Section("--Sec-- Knowledge Base", "🩻"),
            Page(
                "kb/kb_semantic_faiss.py",
                "Search in KB",
                "👀",
                is_section=False,
                in_section=True,
            ),
            Page(
                "kb/kb_semantic.py",
                "Google Scholar",
                "📖",
                is_section=False,
                in_section=True,
            ),
            Page(
                "kb/add_doc_kb.py",
                "Add Doc to Kb",
                "🖲️",
                is_section=False,
                in_section=True,
            ),
        ]
    )


if __name__ == "__main__":
    # setup environtment
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    OUT_FOLDER = os.path.join(ROOT_DIR, "out")
    TMP_FOLDER = os.path.join(ROOT_DIR, "tmp")
    ANSWERS_FOLDER = os.path.join(ROOT_DIR, "answers")
    # create folders if they don't exist
    os.makedirs(OUT_FOLDER, exist_ok=True)
    os.makedirs(TMP_FOLDER, exist_ok=True)
    os.makedirs(ANSWERS_FOLDER, exist_ok=True)
    # read env file
    config = dotenv_values(os.path.join(ROOT_DIR, "keys", ".env"))
    folder_path = "chroma_db_google"
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
    # key access gemini
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = config.get("GEMINI-API-KEY")
    if "PINECONE_API_KEY" not in os.environ:
        os.environ["PINECONE_API_KEY"] = config.get("PINECONE_API_KEY")
    if "PINECONE_INDEX_NAME" not in os.environ:
        os.environ["PINECONE_INDEX_NAME"] = "forensic"

    main()
