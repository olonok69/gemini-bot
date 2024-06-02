from st_pages import Page, show_pages, Section
import os
import subprocess
import sys

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


show_pages(
    [
        Page("home.py", "Home", "🏠"),
        Section("Prompts", "📃"),
        Page("prompts/add.py", "Add prompt", "➕", is_section=False, in_section=True),
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
        Page("1_doc.py", "1 Documento", "✏️", is_section=False, in_section=True),
        Page("1_doc_esp.py", "1 Doc+prompt", "📝", is_section=False, in_section=True),
        Page(
            "many_docs.py",
            "1+ Documentos",
            ":books:",
            is_section=False,
            in_section=True,
        ),
        Page("display.py", "Ver Respuestas", ":eye:", in_section=False),
        Section("Pubmed", "🩻"),
        Page(
            "pubmed/search.py",
            "Search in Pubmed",
            "🔍",
            is_section=False,
            in_section=True,
        ),
        Page(
            "pubmed/retrieve.py",
            "Search many in Pubmed",
            "👀",
            is_section=False,
            in_section=True,
        ),
    ]
)
# Page("1_doc.py", "1 Documento", ":books:"),
