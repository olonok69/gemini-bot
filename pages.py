from st_pages import Page, show_pages, Section
import os

import streamlit as st
from dotenv import dotenv_values


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Optional -- adds the title and icon to the current page
# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FOLDER = os.path.join(ROOT_DIR, "out")
TMP_FOLDER = os.path.join(ROOT_DIR, "tmp")
ANSWERS_FOLDER = os.path.join(ROOT_DIR, "answers")
# create folders if they don't exist
os.makedirs(OUT_FOLDER, exist_ok=True)
os.makedirs(TMP_FOLDER, exist_ok=True)
os.makedirs(ANSWERS_FOLDER, exist_ok=True)

st.title("Forensic Reports Tools. Powered by Gemini, Langchain and Pinecone")


def main():

    show_pages(
        [
            Page("home.py", "Home", "🏠"),
            Section("Prompts", "📃"),
            Page(
                "prompts/add.py", "Add prompt", "➕", is_section=False, in_section=True
            ),
            Page(
                "prompts/modify.py",
                "Modify prompt",
                "💱",
                is_section=False,
                in_section=True,
            ),
            Page(
                "prompts/delete.py",
                "Delete prompt",
                "❌",
                is_section=False,
                in_section=True,
            ),
            Section("Chat Gemini", "♊"),
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
                "display.py",
                "Combina Respuestas",
                ":eye:",
                is_section=False,
                in_section=True,
            ),
            Section("Periciales", "🧑‍⚕️"),
            Page(
                "pericial/add.py",
                "Add Section Pericial",
                "➕",
                is_section=False,
                in_section=True,
            ),
            Page(
                "pericial/modify.py",
                "Modify Section Pericial",
                "💱",
                is_section=False,
                in_section=True,
            ),
            Page(
                "pericial/delete.py",
                "Delete Section Pericial",
                "❌",
                is_section=False,
                in_section=True,
            ),
            Page(
                "pericial/search.py",
                "Similarity Search",
                "🕵️",
                is_section=False,
                in_section=True,
            ),
            Section("Knowledge Base", "🩻"),
            # Page(
            #     "pubmed/search.py",
            #     "Search in Pubmed",
            #     "🔍",
            #     is_section=False,
            #     in_section=True,
            # ),
            Page(
                "kb/kb_look.py",
                "Search in KB",
                "👀",
                is_section=False,
                in_section=True,
            ),
        ]
    )


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    config = dotenv_values(os.path.join(ROOT_DIR, "keys", ".env"))

    # key access gemini
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = config.get("GEMINI-API-KEY")
    if "PINECONE_API_KEY" not in os.environ:
        os.environ["PINECONE_API_KEY"] = config.get("PINECONE_API_KEY")
    if "PINECONE_INDEX_NAME" not in os.environ:
        os.environ["PINECONE_INDEX_NAME"] = "forensic"

    main()
