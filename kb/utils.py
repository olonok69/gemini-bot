from langchain_community.document_loaders import PyPDFLoader
import uuid
from IPython import embed


def load_file(path):
    # load pdf file and transform into Langchain Documents
    loader = PyPDFLoader(path)
    pages = loader.load_and_split()
    return pages


def get_docs_to_add_vectorstore(pages, file, google_ef):
    # get components to add to Chroma
    documents = []
    ids = []
    metadatas = []
    embeddings = []

    for page in pages:
        emb = google_ef([page.page_content])
        embeddings.append(emb[0])
        metadatas.append({"page": page.metadata.get("page"), "filename": file})
        ids.append(uuid.uuid1().hex)
        documents.append(page.page_content)
    return documents, ids, metadatas, embeddings


def sumup_history(st):
    """
    create a text value with the chat history
    Args:
        st (_type_): Streamlit session
    """
    textvalue = ""

    for promp, answer, i in zip(
        st.session_state["user_prompt_history_faiss"],
        st.session_state["chat_answers_history_faiss"],
        range(
            1,
            len(st.session_state["chat_answers_history_faiss"]) + 1,
        ),
    ):
        textvalue = (
            textvalue
            + "\n"
            + str(i)
            + "."
            + "Prompt:\n"
            + promp
            + "\n\nAnswer:\n"
            + answer
            + "\n"
            + "-" * 30
        )
    return textvalue


def update_list_answers_queries(st, result, query):
    """
    update list of answers and queries
    Args:
        result ([type]): result of model
        query ([type]): query of user
    """
    # add model answer and user query to history
    if (
        result["answer"] not in st.session_state["chat_answers_history_faiss"]
        and st.session_state["buttom_visualiza_faiss_clicked"] == False
    ):
        st.session_state["chat_answers_history_faiss"].append(
            result["answer"]
        )  # add model answer to history
    if (
        query not in st.session_state["user_prompt_history_faiss"]
        and st.session_state["buttom_visualiza_faiss_clicked"] == False
    ):
        st.session_state["user_prompt_history_faiss"].append(
            query
        )  # add user query to history
    return
