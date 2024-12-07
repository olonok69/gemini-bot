from IPython import embed
import logging
# Session configuration
config ={
    "20": { 
"config_20_del" : ["vcol1doc_20",  "vcol2doc_20", "init_run_20", "pdf_ref_20", "file_name_20", "file_history_20", "upload_state_20", "value_20", "buttom_send_not_clicked_20","select_box_20",  
"file_prompt_selected_20", "prompt_introduced_20", "chat_true_20","expander_20", "initialized_20", "buttom_send_20", "buttom_has_send_20", "llm_20", "prompt_20", "chat_answers_history_20", 
"user_prompt_history_20","chat_history_20", "buttom_send_clicked_20", "buttom_resfresh_clicked_20", "salir_20"],

"config_20" : ["user_prompt_history_20",  "chat_answers_history_20", "chat_history_20", "initialized_20", "list_images_20", "file_name_20", "file_history_20", "prompt_introduced_20", "prompt_20","chat_true_20",  
"buttom_popup_20", "buttom_has_send_20", "pdf_ref_20","value_20", "buttom_send_not_clicked_20", "vcol1doc_20", "vcol2doc_20", "expander_20", "file_prompt_selected_20","buttom_send_clicked_20",
"buttom_resfresh_clicked_20"]},
    "21": {
"config_21_del" : ["vcol1doc_21",  "vcol2doc_21", "init_run_21", "pdf_ref_21", "multi_file_name_21", "multi_file_pages_21", "upload_state_21", "value_21", "buttom_send_not_clicked_21","case_query_21",  
"file_prompt_selected_21", "prompt_introduced_21", "chat_true_21","expander_21", "initialized_21", "buttom_send_21", "buttom_has_send_21", "llm_21", "prompt_21", "chat_answers_history_21", 
"user_prompt_history_21","chat_history_21", "buttom_send_clicked_21", "buttom_resfresh_clicked_21", "salir_21"],

"config_21" : ["user_prompt_history_21",  "chat_answers_history_21", "chat_history_21", "initialized_21", "list_images_21", "multi_file_name_21", "multi_file_pages_21", "prompt_introduced_21", "prompt_21","chat_true_21",  
"buttom_popup_21", "buttom_has_send_21", "pdf_ref_21","value_21", "buttom_send_not_clicked_21", "vcol1doc_21", "vcol2doc_21", "expander_21", "file_prompt_selected_21","buttom_send_clicked_21",
"buttom_resfresh_clicked_21"]},

 "22": { 
"config_22_del" : ["vcol1doc_22",  "vcol2doc_22", "init_run_22", "file_and_answer_select_22", "multi_file_name_21", "file_prompt_selected_visualiza_22", "file_and_answer_select_has_changed_22", "chat_true_22", "search_pericial_22",
"buttom_send_visualiza_22",  "section_prompt_selected_22", "prompt_introduced_22", "select_box_221","select_box_22""pericial_prompt_selected_22", "b_accept_inside_pericial_22", "prompt_combined_filename_22", "seccion_introduced_22", "answer_introduced_22",
"expander_22", "instruction_to_be_send_22","prompt_1_sample_22", "chat_answers_history_22", "initialized_22", "llm_22", "user_prompt_history_22","chat_history_22", "salir_22", "embeddings_22", "index_22", "vectorstore_22"],

"config_22" : ["file_prompt_selected_visualiza_22",  "file_and_answer_select_has_changed_22", "chat_true_22", "buttom_send_visualiza_22", "section_prompt_selected_22", "pericial_prompt_selected_22",  "prompt_introduced_22", 
"b_accept_inside_pericial_22","answer_introduced_22", "prompt_combined_filename_22", "seccion_introduced_22", "expander_22","instruction_to_be_send_22", "buttom_send_not_clicked_21", "vcol1doc_22", "vcol2doc_22", 
"chat_answers_history_22", "initialized_22","user_prompt_history_22", "chat_history_22"]},

 "23": { 
"config_23_del" : ["vcol1doc_23",  "vcol2doc_23", "init_run_23", "file_and_answer_select_23", "multi_file_name_21", "file_prompt_selected_visualiza_23", "file_and_answer_select_has_changed_23", "chat_true_23", "search_pericial_23",
"buttom_send_visualiza_23",  "section_prompt_selected_23", "prompt_introduced_23", "select_box_231","select_box_23""pericial_prompt_selected_23", "b_accept_inside_pericial_23", "prompt_combined_filename_23", "seccion_introduced_23", "answer_introduced_23",
"expander_23", "instruction_to_be_send_23","prompt_1_sample_23", "chat_answers_history_23", "initialized_23", "llm_23", "user_prompt_history_23","chat_history_23", "salir_23", "embeddings_23", "index_23", "vectorstore_23"],

"config_23" : ["file_prompt_selected_visualiza_23",  "file_and_answer_select_has_changed_23", "chat_true_23", "buttom_send_visualiza_23", "section_prompt_selected_23", "pericial_prompt_selected_23",  "prompt_introduced_23", 
"b_accept_inside_pericial_23","answer_introduced_23", "prompt_combined_filename_23", "seccion_introduced_23", "expander_23","instruction_to_be_send_23", "buttom_send_not_clicked_21", "vcol1doc_23", "vcol2doc_23", 
"chat_answers_history_23", "initialized_23","user_prompt_history_23", "chat_history_23"]},

 "30": { 
"config_30_del" : ["salir_30",  "llm_30", "embeddings_30", "vectorstore_30", "init_run_30", "select_file_faiss_30", "checkbox_faiss_30", "file_kb_faiss_selected_30", "checkbox_30", "user_prompt_history_faiss_30",
"retriever_30",  "name_file_kb_faiss_selected_30", "conversational_rag_chain_30", "store_30","current_prompt_30", "buttom_visualiza_faiss_clicked_30", "docs_context_names_30", "docs_context_30", "expander_30",
"answer_prompt_30", "chat_history_30","history_conversation_with_model_30", "text_30", "buttom_visualiza_faiss_30", "file_faiss_selected_30", "select_context_faiss_30","kb_text2_faiss_30", "chat_answers_history_faiss_30"],
"config_30" : ["file_kb_faiss_selected_30", "checkbox_30", "retriever_30", "name_file_kb_faiss_selected_30", "conversational_rag_chain_30", "store_30",  "current_prompt_30", "user_prompt_history_faiss_30",
"buttom_visualiza_faiss_clicked_30","docs_context_names_30", "docs_context_30",  "expander_30","answer_prompt_30", "chat_history_30", "history_conversation_with_model_30", "file_faiss_selected_30", "chat_answers_history_faiss_30"]},

 "31": { 
"config_31_del" : ["salir_31",  "llm_31", "embeddings_31", "vectorstore_31", "init_run_31", "api_wrapper_31", "web_research_retriever_31", "checkbox_31", "retrieval_chain_31", "qa_chain_31",
"map_chain_31",  "combine_parallel_chain_31", "complete_chain_31", "kb_text_31"],
"config_31" : []},
 "32": { 
"config_32_del" : ["salir_32",  "llm_32", "embeddings_32", "vectorstore_32", "init_run_32", "value_32", "file_name_32", "file_history_32", "upload_state_32", "pdf_ref_32",
"selectbox_category_32",  "add_file_kb_selected_32", "documents_32", "ids_32", "metadatas_32","pages_32"],
"config_32" : ["value_32","file_name_32", "file_history_32", "upload_state_32","add_file_kb_selected_32","documents_32", "ids_32", "metadatas_32", "pdf_ref_32", "pages_32"]},

 
 "10": { 
"config_10_del" : ["salir_10",  "index_10", "embeddings_10", "vectorstore_10", "init_run_10", "selector_selected_add_10", "select_box_add_10"],
"config_10" : ["selector_selected_add_10"]},

}

def reset_session_num(session, num:int="10"):
    """
    Delete session state for multiple files option
    param: st  session
    param: ss  session state
    param: model  chat (gemini model)
    """

    for x in list(session.session_state.keys()):
        if num in x and x in config[num][f"config_{num}_del"]:
            try:
                del session.session_state[x]
                logging.info(f"deleted {x}")
            except:
                logging.info(f"error deleting {x}")

    # placeholder for multiple files


    return

def init_session_num(sess, ss, num, col1, col2, config, model: None):
    """
    initialize session state 
    Args:
    param: st  session
    param: ss  session state
    param: num  number of session
    param: col1  column 1
    param: col2  column 2
    param: config  configuration
    param: model  chat (gemini model)
    """
    if f"user_prompt_history_{num}" not in sess.session_state and f"user_prompt_history_{num}" in config:
        sess.session_state[f"user_prompt_history_{num}"] = []

    if f"user_prompt_history_faiss_{num}" not in sess.session_state and f"user_prompt_history_faiss_{num}" in config:
        sess.session_state[f"user_prompt_history_faiss_{num}"] = []

    if f"chat_answers_history_faiss_{num}" not in sess.session_state and f"chat_answers_history_faiss_{num}" in config:
        sess.session_state[f"chat_answers_history_faiss_{num}"] = []

    if f"chat_answers_history_{num}" not in sess.session_state and f"chat_answers_history_{num}" in config:
        sess.session_state[f"chat_answers_history_{num}"] = []
        
    if f"multi_file_name_{num}" not in sess.session_state and f"multi_file_name_{num}" in config:
        sess.session_state[f"multi_file_name_{num}"] = []

    if f"multi_file_pages_{num}" not in sess.session_state and f"multi_file_pages_{num}" in config:
        sess.session_state[f"multi_file_pages_{num}"] = []

    if f"pages_{num}" not in sess.session_state and f"pages_{num}" in config:
        sess.session_state[f"pages_{num}"] = []
    
    if f"metadatas_{num}" not in sess.session_state and f"metadatas_{num}" in config:
        sess.session_state[f"metadatas_{num}"] = []
    
    if f"ids_{num}" not in sess.session_state and f"ids_{num}" in config:
        sess.session_state[f"ids_{num}"] = []

    if f"chat_history_{num}" not in sess.session_state and f"chat_history_{num}" in config:
        sess.session_state[f"chat_history_{num}"] = []
    
    if f"docs_context_names_{num}" not in sess.session_state and f"docs_context_names_{num}" in config:
        sess.session_state[f"docs_context_names_{num}"] = []
    
    if f"documents_{num}" not in sess.session_state and f"documents_{num}" in config:
        sess.session_state[f"documents_{num}"] = []

    if f"docs_context_{num}" not in sess.session_state and f"docs_context_{num}" in config:
        sess.session_state[f"docs_context_{num}"] = []

    if f"initialized_{num}" not in sess.session_state and f"initialized_{num}" in config:
        sess.session_state[f"initialized_{num}"] = "False"

    if f"chat_{num}" not in sess.session_state and f"chat_{num}" in config:
        sess.session_state[f"chat_{num}"] = None
    
    if f"conversational_rag_chain_{num}" not in sess.session_state and f"conversational_rag_chain_{num}" in config:
        sess.session_state[f"conversational_rag_chain_{num}"] = None

    if f"retriever_{num}" not in sess.session_state and f"retriever_{num}" in config:
        sess.session_state[f"retriever_{num}"] = None

    if f"embeddings_{num}" not in sess.session_state and f"embeddings_{num}" in config:
        sess.session_state[f"embeddings_{num}"] = None

    if f"vectorstore_{num}" not in sess.session_state and f"vectorstore_{num}" in config:
        sess.session_state[f"vectorstore_{num}"] = None

    if f"index_{num}" not in sess.session_state and f"index_{num}" in config:
        sess.session_state[f"index_{num}"] = None

    if f"list_images_{num}" not in sess.session_state and f"list_images_{num}" in config:
        sess.session_state[f"list_images_{num}"] = []

    if f"user_prompt_history_{num}" not in sess.session_state and f"user_prompt_history_{num}" in config:
        sess.session_state[f"user_prompt_history_{num}"] = []

    if f"chat_answers_history_{num}" not in sess.session_state and f"chat_answers_history_{num}" in config:
        sess.session_state[f"chat_answers_history_{num}"] = []

    # placeholder for multiple files
    if f"file_name_{num}" not in sess.session_state and f"file_name_{num}" in config:
        sess.session_state[f"file_name_{num}"] = "no file"

    if f"file_history_{num}" not in sess.session_state and f"file_history_{num}" in config:
        sess.session_state[f"file_history_{num}"] = "no file"

    if f"prompt_introduced_{num}" not in sess.session_state and f"prompt_introduced_{num}" in config:
        sess.session_state[f"prompt_introduced_{num}"] = ""
    
    if f"name_file_kb_faiss_selected_{num}" not in sess.session_state and f"name_file_kb_faiss_selected_{num}" in config:
        sess.session_state[f"name_file_kb_faiss_selected_{num}"] = ""
    
    if f"history_conversation_with_model_{num}" not in sess.session_state and f"history_conversation_with_model_{num}" in config:
        sess.session_state[f"history_conversation_with_model_{num}"] = ""
    
    if f"current_prompt_{num}" not in sess.session_state and f"current_prompt_{num}" in config:
        sess.session_state[f"current_prompt_{num}"] = ""
    
    if f"answer_prompt_{num}" not in sess.session_state and f"answer_prompt_{num}" in config:
        sess.session_state[f"answer_prompt_{num}"] = ""

    if f"seccion_introduced_{num}" not in sess.session_state and f"seccion_introduced_{num}" in config:
        sess.session_state[f"seccion_introduced_{num}"] = ""

    if f"upload_state_{num}" not in sess.session_state and f"upload_state_{num}" in config:
        sess.session_state[f"upload_state_{num}"] = ""

    if f"answer_introduced_{num}" not in sess.session_state and f"answer_introduced_{num}" in config:
        sess.session_state[f"answer_introduced_{num}"] = ""
    
    if f"answer_{num}" not in sess.session_state and f"answer_{num}" in config:
        sess.session_state[f"answer_{num}"] = ""

    if f"prompt_combined_filename_{num}" not in sess.session_state and f"prompt_combined_filename_{num}" in config:
        sess.session_state[f"prompt_combined_filename_{num}"] = ""

    if f"instruction_to_be_send_{num}" not in sess.session_state and f"instruction_to_be_send_{num}" in config:
        sess.session_state[f"instruction_to_be_send_{num}"] = ""

    if f"prompt_{num}" not in sess.session_state and f"prompt_{num}" in config:
        sess.session_state[f"prompt_{num}"] = ""

    if f"chat_true_{num}" not in sess.session_state and f"chat_true_{num}" in config:
        sess.session_state[f"chat_true_{num}"] = "no_chat"

    if f"buttom_popup_{num}" not in sess.session_state and f"buttom_popup_{num}" in config:
        sess.session_state[f"buttom_popup_{num}"] = "no_buttom"

    if f"buttom_has_send_{num}" not in sess.session_state and f"buttom_has_send_{num}" in config:
        sess.session_state[f"buttom_has_send_{num}"] = "no_buttom"

    if f"buttom_send_clicked_{num}" not in sess.session_state and f"buttom_send_clicked_{num}" in config:
        sess.session_state[f"buttom_send_clicked_{num}"] = False

    if f"selector_selected_add_{num}" not in sess.session_state and f"selector_selected_add_{num}" in config:
        sess.session_state[f"selector_selected_add_{num}"] = False
    
    if f"add_file_kb_selected_{num}" not in sess.session_state and f"add_file_kb_selected_{num}" in config:
        sess.session_state[f"add_file_kb_selected_{num}"] = False
    
    if f"file_faiss_selected_{num}" not in sess.session_state and f"file_faiss_selected_{num}" in config:
        sess.session_state[f"file_faiss_selected_{num}"] = False
    
    if f"buttom_visualiza_faiss_clicked_{num}" not in sess.session_state and f"buttom_visualiza_faiss_clicked_{num}" in config:
        sess.session_state[f"buttom_visualiza_faiss_clicked_{num}"] = False

    if f"checkbox_{num}" not in sess.session_state and f"checkbox_{num}" in config:
        sess.session_state[f"checkbox_{num}"] = False

    if f"file_kb_faiss_selected_{num}" not in sess.session_state and f"file_kb_faiss_selected_{num}" in config:
        sess.session_state[f"file_kb_faiss_selected_{num}"] = False

    if f"buttom_send_visualiza_{num}" not in sess.session_state and f"buttom_send_visualiza_{num}" in config:
        sess.session_state[f"buttom_send_visualiza_{num}"] = False

    if f"file_prompt_selected_visualiza_{num}" not in sess.session_state and f"file_prompt_selected_visualiza_{num}" in config:
        sess.session_state[f"file_prompt_selected_visualiza_{num}"] = False

    if f"file_and_answer_select_has_changed_{num}" not in sess.session_state and f"file_and_answer_select_has_changed_{num}" in config:
        sess.session_state[f"file_and_answer_select_has_changed_{num}"] = False

    if f"section_prompt_selected_{num}" not in sess.session_state and f"section_prompt_selected_{num}" in config:
        sess.session_state[f"section_prompt_selected_{num}"] = False

    if f"pericial_prompt_selected_{num}" not in sess.session_state and f"pericial_prompt_selected_{num}" in config:
        sess.session_state[f"pericial_prompt_selected_{num}"] = False
        
    if f"buttom_resfresh_clicked_{num}" not in sess.session_state    and f"buttom_resfresh_clicked_{num}" in config:
        sess.session_state[f"buttom_resfresh_clicked_{num}"] = False

    if f"b_accept_inside_pericial_{num}" not in sess.session_state and f"b_accept_inside_pericial_{num}" in config:
        sess.session_state[f"b_accept_inside_pericial_{num}"] = False
    
    if f"store_{num}" not in sess.session_state and f"store_{num}" in config:
        sess.session_state[f"store_{num}"] = {}
    if f"pdf_ref_{num}" not in ss and f"pdf_ref_{num}" in config:
        ss[f"pdf_ref_{num}"] = None

    if f"value_{num}" not in sess.session_state and f"value_{num}" in config:
        sess.session_state[f"value_{num}"] = 0

    # buttom send to gemini
    if f"buttom_send_not_clicked_{num}" not in sess.session_state  and f"buttom_send_not_clicked_{num}" in config:
        sess.session_state[f"buttom_send_not_clicked_{num}"] = False

    if f"file_prompt_selected_{num}" not in sess.session_state and f"file_prompt_selected_{num}" in config:
        sess.session_state[f"file_prompt_selected_{num}"] = False

    if f"vcol1doc_{num}" not in sess.session_state and f"vcol1doc_{num}" in config:
        sess.session_state[f"vcol1doc_{num}"] = col1

    if f"vcol2doc_{num}" not in sess.session_state and f"vcol2doc_{num}" in config:
        sess.session_state[f"vcol2doc_{num}"] = col2

    if f"expander_{num}" not in sess.session_state and f"expander_{num}" in config:
        sess.session_state[f"expander_{num}"] = True
    sess.session_state[f"init_run_{num}"] = True
    return