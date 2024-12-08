from .pdf_utils import extract_pdf_images, count_pdf_pages, upload, upload_files
from .work_gemini import get_chat_response, prepare_prompt, start_chat, init_model, init_llm, init_google_embeddings
from .helpers import (
    write_history_1,
    reset_session_1,
    write_history_multi,
    reset_session_multi,
    visualiza,
    save_df_many,
    get_filename_multi,
    init_session_multi,
    init_session_1_prompt,
    visualiza_1_prompt,
    visualiza_display_page,
    visualiza_pericial,
    reset_session_visualiza,
    init_visualiza,
    init_session_faiss,
    reset_session_faiss,
    reload_page_combina,
    init_session_add_kb,
    reset_session_add_kb,
    reload_page_many_docs,
    change_status,
    reload_page_1_doc,

)
from .utils import print_stack, create_client_logging
from .files import (
    open_table_answers,
    create_folders,
    open_table_prompts,
    file_selector,
    open_table_periciales,
    open_table_answers_no_case,
    open_table_answers_final,
    remove_prompts,
    remove_pericial,
    remove_anwers,
)

from .maintenance import (
    save_text_add_prompt,
    save_text_add_pericial,
    visualiza_add_prompt,
    visualiza_add_pericial,
    selected_add,
    save_text_modifica_prompt,
    visualiza_modify_prompt,
    selected_modify_prompt,
    selected_modify_percial,
    visualiza_pericial_modifica,
    visualiza_delete_prompt,
    selected_delete,
    selected_modifica,
    selected_delete_prompt,
    selected_delete_percial,
    visualiza_delete_pericial,
    selected_delete_answer_gemini,
    selected_delete_answer_gemini_nocase,
    visualiza_delete_answer_gemini_no_case,
)

from .maps import config, init_session_num, reset_session_num