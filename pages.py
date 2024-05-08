from st_pages import Page, show_pages, add_page_title
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


# def apt_get_update():
#     subprocess.call(["apt-get", "update"])


# def apt_get_install():
#     subprocess.call(
#         ["apt-get", "install", "python3-pip", "libpoppler-dev", "poppler-utils"]
#     )


# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("home.py", "Home", "🏠"),
        Page("1_doc.py", "1 Documento", "✏️"),
        Page("many_docs.py", "1+ Documentos", ":books:"),
        Page("display.py", "Ver Respuestas", ":eye:"),
    ]
)
# Page("1_doc.py", "1 Documento", ":books:"),
