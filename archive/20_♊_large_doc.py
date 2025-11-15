import streamlit as st
import os
import logging
import copy
import json
from pathlib import Path
from typing import Tuple, Dict, List, Any, Optional

from dotenv import dotenv_values
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import Part, GenerativeModel

from src.components.pdf_viewer import render_pdf
from streamlit import session_state as ss

from src.pdf_utils import count_pdf_pages
from src.model import init_model
from src.utils import print_stack, upload_blob
from src.maps import config as conf, init_session_num, reset_session_num
from src.files import open_table_answers, create_folders, open_table_prompts
from src.helpers import visualiza_1_prompt_no_upload, reload_page_1_doc

# Constants and setup
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = Path(ROOT_DIR).parent.absolute().as_posix()
BUCKET_NAME = "gemini-bot-data"
DESTINATION_BLOB_FOLDER = "input"
SESSION_KEY = "200"  # Session identifier

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.info(f"PROJECT DIR: {PROJECT_DIR}, this folder: {ROOT_DIR}")

# Create necessary folders
OUT_FOLDER, TMP_FOLDER, ANSWERS_DIR, PROMPTS_DIR, DICTS_DIR = create_folders(
    PROJECT_DIR
)

# Load prompt and answer tables
pname, pname2, df_answers = open_table_answers(ANSWERS_DIR)
fname, fname2, df_prompts = open_table_prompts(PROMPTS_DIR)
AVAILABLE_PROMPTS = df_prompts["name_prompt"].to_list()


class SessionState:
    """Helper class to handle session state variables consistently"""

    @staticmethod
    def init_if_not_exists(key: str, default_value: Any) -> None:
        """Initialize a session state variable if it doesn't exist"""
        if key not in st.session_state:
            st.session_state[key] = default_value

    @staticmethod
    def get_key(base_key: str) -> str:
        """Get a session-specific key name"""
        return f"{base_key}_{SESSION_KEY}"

    @staticmethod
    def initialize_chat_state() -> None:
        """Initialize all required session variables for the chat"""
        keys_with_defaults = {
            "init_run": False,
            "file_prompt_selected": False,
            "file_uploaded_gcs": False,
            "buttom_send_not_clicked": True,
            "chat_true": "",
            "buttom_has_send": "",
            "value": 0,
            "vcol1doc": 40,
            "vcol2doc": 60,
            "expander": True,
            "upload_state": "",
            "pdf_ref": None,
            "file_name": "",
            "file_history": "",
            "buttom_send_clicked": False,
            "buttom_resfresh_clicked": False,
            "initialized": "False",
            "prompt_introduced": "",
            "chat_answers_history": [],
            "user_prompt_history": [],
            "chat_history": [],
            "pdf_dialog_open": False,
        }

        for key, default_value in keys_with_defaults.items():
            SessionState.init_if_not_exists(SessionState.get_key(key), default_value)


def setup_vertex_ai() -> GenerativeModel:
    """Initialize Vertex AI and return the generative model"""
    config = dotenv_values(os.path.join(PROJECT_DIR, "keys", ".env"))
    credentials_path = os.path.join(
        PROJECT_DIR, "keys", "complete-tube-421007-208a4862c992.json"
    )

    # Load credentials
    with open(credentials_path) as source:
        info = json.load(source)
    vertex_credentials = service_account.Credentials.from_service_account_info(info)

    # Initialize Vertex AI
    vertexai.init(
        project=config["PROJECT"],
        location=config["REGION"],
        credentials=vertex_credentials,
    )

    # Set environment variables if needed
    if "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = config.get("GEMINI-API-KEY")
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = config.get("GEMINI-API-KEY")

    return init_model()


def on_file_upload(uploaded_file) -> None:
    """Handle file upload process"""
    # Get the file binary data
    file_bytes = uploaded_file.getvalue()

    # Save file to temporary location
    file_path = os.path.join(TMP_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Count pages and update session state
    num_pages = count_pdf_pages(file_path)

    # Update session state
    sk = SESSION_KEY
    st.session_state[f"pdf_ref_{sk}"] = file_bytes
    st.session_state[f"file_name_{sk}"] = file_path
    st.session_state[f"file_history_{sk}"] = uploaded_file.name
    st.session_state[f"upload_state_{sk}"] = (
        f"Número de páginas del fichero {uploaded_file.name}: {num_pages}"
    )
    st.session_state[f"value_{sk}"] = 1  # file uploaded
    st.session_state[f"buttom_send_not_clicked_{sk}"] = False


def upload_to_gcs(file_name: str) -> None:
    """Upload the file to Google Cloud Storage"""
    sk = SESSION_KEY
    # Check if we have a file to upload
    if not st.session_state.get(f"pdf_ref_{sk}"):
        return

    # Upload the file to GCS
    credentials_path = os.path.join(
        PROJECT_DIR, "keys", "complete-tube-421007-208a4862c992.json"
    )
    upload_blob(
        BUCKET_NAME,
        st.session_state[f"file_name_{sk}"],
        os.path.join(DESTINATION_BLOB_FOLDER, file_name),
        credentials_path,
    )

    # Update status
    st.session_state[f"upload_state_{sk}"] = f"Fichero {file_name} subido a GCS"
    st.session_state[f"file_uploaded_gcs_{sk}"] = True
    if st.session_state[f"value_{sk}"] < 3:
        st.session_state[f"value_{sk}"] = 2  # pages selected


def display_pdf_dialog(
    binary_data: bytes, width: int = 2000, height: int = 1000
) -> None:
    """Display PDF in a dialog window"""
    sk = SESSION_KEY
    dialog_key = f"pdf_dialog_open_{sk}"

    if st.session_state.get(dialog_key, False):
        render_pdf(
            binary_data,
            width=width,
            height=height,
            key=f"pdf_viewer_dialog_{sk}",
            title="PDF preview dialog",
        )
        if st.button("Close"):
            st.session_state[dialog_key] = False
            st.rerun()


def handle_initial_prompt(model: GenerativeModel, pdf_uri: str) -> None:
    """Process the initial prompt with the PDF"""
    sk = SESSION_KEY
    # Use the selected prompt directly without user query
    initial_prompt = st.session_state[f"prompt_{sk}"]
    pdf_part = Part.from_uri(pdf_uri, mime_type="application/pdf")
    text_part = Part.from_text(initial_prompt)

    # Get response from the model
    response = model.generate_content([pdf_part, text_part])

    # Update chat history
    st.session_state[f"chat_answers_history_{sk}"].append(response.text)
    st.session_state[f"user_prompt_history_{sk}"].append(
        st.session_state[f"prompt_introduced_{sk}"]
    )
    st.session_state[f"chat_history_{sk}"].append(
        (st.session_state[f"prompt_introduced_{sk}"], response.text)
    )

    # Update session state
    st.session_state[f"initialized_{sk}"] = "True"
    st.session_state[f"buttom_send_clicked_{sk}"] = True
    st.session_state[f"expander_{sk}"] = False


def handle_followup_prompt(
    model: GenerativeModel, pdf_uri: str, user_prompt: str
) -> None:
    """Process follow-up prompts with conversation history"""
    sk = SESSION_KEY

    # Format the conversation history
    conversation_history = ""
    for user_msg, assistant_msg in st.session_state[f"chat_history_{sk}"]:
        conversation_history += f"User: {user_msg}\nAssistant: {assistant_msg}\n\n"

    # Create a new prompt with conversation history
    prompt_with_history = f"""
    Previous conversation:
    {conversation_history}

    New question: {user_prompt}
    """

    # Prepare parts for the model
    pdf_part = Part.from_uri(pdf_uri, mime_type="application/pdf")
    text_part = Part.from_text(prompt_with_history)

    # Get response from the model
    response = model.generate_content([pdf_part, text_part])

    # Update chat history
    st.session_state[f"chat_answers_history_{sk}"].append(response.text)
    st.session_state[f"user_prompt_history_{sk}"].append(user_prompt)
    st.session_state[f"chat_history_{sk}"].append((user_prompt, response.text))

    # Update session state
    st.session_state[f"buttom_send_clicked_{sk}"] = True
    st.session_state[f"buttom_resfresh_clicked_{sk}"] = True
    st.session_state[f"expander_{sk}"] = False

    # Log the interaction
    logger.info(f"Processed follow-up prompt: {user_prompt[:50]}...")


def display_chat_history() -> None:
    """Display the chat history in the Streamlit interface"""
    sk = SESSION_KEY

    if len(st.session_state[f"chat_answers_history_{sk}"]) > 0:
        # Create deep copies to avoid modifying the original lists
        answers = copy.deepcopy(st.session_state[f"chat_answers_history_{sk}"])
        prompts = copy.deepcopy(st.session_state[f"user_prompt_history_{sk}"])

        # Reverse lists to show most recent messages first
        if len(answers) > 1:
            answers.reverse()
        if len(prompts) > 1:
            prompts.reverse()

        # Display messages
        for assistant_msg, user_msg in zip(answers, prompts):
            message1 = st.chat_message("user")
            message1.write(user_msg)
            message2 = st.chat_message("assistant")
            message2.write(assistant_msg)


def render_sidebar() -> None:
    """Render the sidebar with file upload and prompt selection"""
    sk = SESSION_KEY

    # Exit button
    if st.button("Salir"):
        reset_session_num(st, SESSION_KEY)
        st.rerun()

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload PDF file",
        type=["pdf"],
        key=f"pdf_page_{sk}",
        accept_multiple_files=False,
    )

    if uploaded_file:
        on_file_upload(uploaded_file)

        # Show PDF viewer button
        if st.button("Open PDF in Dialog"):
            st.session_state[f"pdf_dialog_open_{sk}"] = True
            display_pdf_dialog(st.session_state[f"pdf_ref_{sk}"])

        # Upload to GCS button
        if st.button("Upload PDF to GCS"):
            upload_to_gcs(uploaded_file.name)

        # Prompt selection after file upload
        if st.session_state[f"file_uploaded_gcs_{sk}"]:
            st.selectbox(
                "Select prompt 👇",
                AVAILABLE_PROMPTS,
                index=None,
                key=f"select_box_{sk}",
                on_change=lambda: setattr(
                    st.session_state, f"file_prompt_selected_{sk}", True
                ),
            )

    # Display prompt details if selected
    if st.session_state.get(f"file_prompt_selected_{sk}") and not st.session_state.get(
        f"prompt_introduced_{sk}"
    ):
        visualiza_1_prompt_no_upload(st, df_prompts, num=SESSION_KEY)


def render_main_area(model: GenerativeModel) -> None:
    """Render the main chat area"""
    sk = SESSION_KEY

    # Show status in expander
    with st.expander(
        "⚙️ Instructions to send to Gemini 👇",
        expanded=st.session_state[f"expander_{sk}"],
    ):
        st.text_area("Status selection", "", key=f"upload_state_{sk}", height=150)

    # Show send button if prompt is selected
    if st.session_state[f"file_prompt_selected_{sk}"]:
        if st.button(
            "Send Prompt to Gemini",
            key=f"buttom_send_{sk}",
            disabled=st.session_state[f"buttom_send_not_clicked_{sk}"],
        ):
            st.session_state[f"chat_true_{sk}"] = "chat activo"
            st.session_state[f"buttom_has_send_{sk}"] = "buttom_Send"
            st.session_state[f"value_{sk}"] = 5
            st.session_state[f"buttom_send_not_clicked_{sk}"] = False
            st.session_state[f"vcol1doc_{sk}"] = 20
            st.session_state[f"vcol2doc_{sk}"] = 80
            st.session_state[f"expander_{sk}"] = False

    # Show chat interface if activated
    if st.session_state[f"chat_true_{sk}"] == "chat activo":
        # Chat input
        user_prompt = st.chat_input(
            "Enter your questions here",
            disabled=not input,
            key=f"chat_input_{sk}",
        )

        # Check for termination command
        if user_prompt == "terminar":
            logger.info(f"Terminating chat session {st.session_state[f'value_{sk}']}")
            reload_page_1_doc(
                st, ss, df_answers, pname, None, TMP_FOLDER, OUT_FOLDER, SESSION_KEY
            )

        # Process user prompt if provided
        elif user_prompt:
            pdf_uri = f"gs://{BUCKET_NAME}/{DESTINATION_BLOB_FOLDER}/{st.session_state[f'file_history_{sk}']}"
            logger.info(f"Processing file: {pdf_uri}")

            # Initial prompt or follow-up
            if st.session_state[f"initialized_{sk}"] == "False":
                handle_initial_prompt(model, pdf_uri)
            else:
                handle_followup_prompt(model, pdf_uri, user_prompt)

        # Display chat history
        display_chat_history()


def main():
    """Main application function"""
    # Basic page setup
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

    # Check authentication
    if not st.session_state.get("authentication_status", False):
        st.session_state.runpage = "main.py"
        st.switch_page("main.py")

    # Initialize session state
    SessionState.init_if_not_exists("salir_200", False)
    if st.session_state["salir_200"]:
        return

    # Initialize chat state variables
    SessionState.initialize_chat_state()

    # Initialize Vertex AI if needed
    model_key = f"llm_{SESSION_KEY}"
    if model_key not in st.session_state:
        st.session_state[model_key] = setup_vertex_ai()

    # Create main container
    placeholder = st.empty()
    with placeholder.container():
        # Initialize session if needed
        if st.session_state[f"init_run_{SESSION_KEY}"] == False:
            init_session_num(
                st,
                ss,
                SESSION_KEY,
                40,
                60,
                conf[SESSION_KEY][f"config_{SESSION_KEY}"],
                None,
            )
            st.session_state[f"init_run_{SESSION_KEY}"] = True

        # Set up columns based on session state
        col1 = st.session_state.get(f"vcol1doc_{SESSION_KEY}", 40)
        col2 = st.session_state.get(f"vcol2doc_{SESSION_KEY}", 60)

        # Create two-column layout
        left_col, right_col = st.columns((col1, col2))

        try:
            # Render sidebar in left column
            with left_col:
                render_sidebar()

            # Render main chat area in right column
            with right_col:
                render_main_area(st.session_state[model_key])

        except Exception as e:
            logger.error(f"Error: {e}")
            st.error(f"Error: {e}")
            print_stack()


if __name__ == "__main__":
    main()
