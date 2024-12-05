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
"buttom_send_visualiza_22",  "section_prompt_selected_22", "prompt_introduced_22", "select_box_221","select_box_222""pericial_prompt_selected_22", "b_accept_inside_pericial_22", "prompt_combined_filename_22", "seccion_introduced_22", "answer_introduced_22",
"expander_22", "instruction_to_be_send_22","prompt_1_sample_22", "chat_answers_history_22", "initialized_22", "llm_22", "user_prompt_history_22","chat_history_22", "salir_22", "embeddings_22", "index_22", "vectorstore_22"],

"config_22" : ["file_prompt_selected_visualiza_22",  "file_and_answer_select_has_changed_22", "chat_true_22", "buttom_send_visualiza_22", "section_prompt_selected_22", "pericial_prompt_selected_22",  "prompt_introduced_22", 
"b_accept_inside_pericial_22","answer_introduced_22", "prompt_combined_filename_22", "seccion_introduced_22", "expander_22","instruction_to_be_send_22", "buttom_send_not_clicked_21", "vcol1doc_22", "vcol2doc_22", 
"chat_answers_history_22", "initialized_22","user_prompt_history_22", "chat_history_22"]},

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

    if f"chat_answers_history_{num}" not in sess.session_state and f"chat_answers_history_{num}" in config:
        sess.session_state[f"chat_answers_history_{num}"] = []
        
    if f"multi_file_name_{num}" not in sess.session_state and f"multi_file_name_{num}" in config:
        sess.session_state[f"multi_file_name_{num}"] = []

    if f"multi_file_pages_{num}" not in sess.session_state and f"multi_file_pages_{num}" in config:
        sess.session_state[f"multi_file_pages_{num}"] = []

    if f"chat_history_{num}" not in sess.session_state and f"chat_history_{num}" in config:
        sess.session_state[f"chat_history_{num}"] = []

    if f"initialized_{num}" not in sess.session_state and f"initialized_{num}" in config:
        sess.session_state[f"initialized_{num}"] = "False"

    if f"chat_{num}" not in sess.session_state and f"chat_{num}" in config:
        sess.session_state[f"chat_{num}"] = None

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

    if f"seccion_introduced_{num}" not in sess.session_state and f"seccion_introduced_{num}" in config:
        sess.session_state[f"seccion_introduced_{num}"] = ""

    if f"upload_state_{num}" not in sess.session_state and f"upload_state_{num}" in config:
        sess.session_state[f"upload_state_{num}"] = ""

    if f"answer_introduced_{num}" not in sess.session_state and f"answer_introduced_{num}" in config:
        sess.session_state[f"answer_introduced_{num}"] = ""

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