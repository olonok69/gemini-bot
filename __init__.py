from .src.pdf_utils import extract_pdf_images, count_pdf_pages, upload, upload_files
from .src.work_gemini import get_chat_response, prepare_prompt, start_chat, init_model
from .src.helpers import (
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
)
from .src.utils import print_stack, create_client_logging
from .pericial.gemini_fn import (
    embed_fn,
    secciones,
    get_embeddings_model,
    get_pinecone_objects,
    pericial_prompt_selected,
    section_prompt_selected,
)
from .src.files import (
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

from .kb.templates import (
    second_prompt,
    first_prompt,
    query_prompt,
    semantic_query,
    combine_research_prompt,
    contextualize_q_prompt,
    qa_prompt,
)
from .kb.chains import (
    get_complete_chain,
    get_retrieval_chain,
    create_semantic_retrieval_chain,
    create_retrieval_qa_source_chain,
    create_Runnable_Parallel_chain,
    create_combine_parallel_outputs_chain,
    create_complete_chain,
    function_create_history_aware_retriever,
    function_create_stuff_documents_chain,
    function_create_retrieval_chain,
    create_runnablewithmessagehistory,
    create_conversational_rag_chain,
)


from .src.maintenance import (
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

from .kb.controls import visualiza_context_faiss
from .kb.utils import sumup_history, update_list_answers_queries
