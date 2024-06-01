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
        Page("prompts/add.py", "Add prompt", "➕"),
        Page("prompts/modify.py", "Modify prompt", "💱"),
        Page("prompts/delete.py", "Delete prompt", "❌"),
        Page("1_doc.py", "1 Documento", "✏️", in_section=False),
        Page("1_doc_esp.py", "1 Doc+prompt", "📝", in_section=False),
        Page("many_docs.py", "1+ Documentos", ":books:", in_section=False),
        Page("display.py", "Ver Respuestas", ":eye:", in_section=False),
    ]
)
# Page("1_doc.py", "1 Documento", ":books:"),
