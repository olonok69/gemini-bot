from langchain_community.vectorstores import FAISS

from src.pdf_utils import create_documents_metadatas

from langchain_chroma import Chroma
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain_core.documents import Document
import uuid


def create_multi_vectorstore(
    collection_name: str, embeddings_model: str, credentials: str
):
    """
    Create a multi vector store.
    Args:
        collection_name (str): The name of the collection.
        embeddings_model (str): The name of the embeddings model.
        credentials (str): The credentials for the embeddings model.
    Returns:
        _type_: Chroma   The created Chroma object.
    """
    return Chroma(
        collection_name=collection_name,
        embedding_function=VertexAIEmbeddings(
            model_name=embeddings_model, credentials=credentials
        ),
    )


def create_multivector_retriever(key: str, vectorstore):
    """
    Create multi-vector retriever.
    Args:
        key (str): The key for the multi-vector retriever.
        vectorstore (object): The vector store to be used.
    """
    # Initialize the storage layer
    store = InMemoryStore()
    id_key = key

    # Create the multi-vector retriever
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key,
    )
    return retriever


def add_docs_multi_vector_retriever(
    retriever,
    text_summaries,
    texts,
    table_summaries,
    tables,
    image_summaries,
    images,
    id_key,
):
    """
    Add Documents to retriever that indexes summaries, but returns raw images or texts
    Args:
        retriever (object): The retriever object to which documents will be added.
        text_summaries (list of str): A list of text summaries.
        texts (list of str): A list of text documents.
        table_summaries (list of str): A list of table summaries.
        tables (list of str): A list of table documents.
        image_summaries (list of str): A list of image summaries.
        images (list of str): A list of image documents.
        id_key (str): The key for the document ID.
    """

    # Helper function to add documents to the vectorstore and docstore
    def add_documents(retriever, doc_summaries, doc_contents):
        doc_ids = [str(uuid.uuid4()) for _ in doc_contents]
        summary_docs = [
            Document(page_content=s, metadata={id_key: doc_ids[i]})
            for i, s in enumerate(doc_summaries)
        ]
        retriever.vectorstore.add_documents(summary_docs)
        retriever.docstore.mset(list(zip(doc_ids, doc_contents)))

    # Add texts, tables, and images
    # Check that text_summaries is not empty before adding
    if text_summaries:
        add_documents(retriever, text_summaries, texts)
    # Check that table_summaries is not empty before adding
    if table_summaries:
        add_documents(retriever, table_summaries, tables)
    # Check that image_summaries is not empty before adding
    if image_summaries:
        add_documents(retriever, image_summaries, images)

    return retriever


def create_db_store_from_file(embeddings, index_name, folder_path: str = "./faiss/"):
    """
    Load a Faiss index from a file.

    Args:
        embeddings (Any): The embeddings object used for the Faiss index.
        index_name (str): The name of the index to load.
        folder_path (str, optional): The path to the folder containing the Faiss index file. Defaults to "./faiss/".

    Returns:
        _type_: Faiss   The loaded Faiss index.
    """
    return FAISS.load_local(
        folder_path=folder_path,
        embeddings=embeddings,
        index_name=index_name,
        allow_dangerous_deserialization=True,
    )


def create_db_from_documents(texts, embedding, metadatas, ids):
    """
    Create a FAISS database from documents.
    Params:
        texts (list of str): A list of document texts.
        embedding (Embedding): The embedding model to use for vectorizing the texts.
        metadatas (list of dict): A list of metadata dictionaries corresponding to each document.
        ids (list of str): A list of unique identifiers for each document.
    return:
        FAISS: A FAISS index created from the provided documents.
    """
    return FAISS.from_texts(
        texts=texts, embedding=embedding, metadatas=metadatas, ids=ids
    )


def add_documents_vector_store(
    config,
    session,
    embeddings,
    num: int = 0,
):
    """
    Adds documents to a vector store based on the specified type (Faiss or Elastic).
    Parameters:
    - config (dict): Configuration dictionary containing settings for the vector store.
    - session (Streamlit): Streamlit session state object.
    - embeddings (object): Embeddings retriever object used for creating document embeddings.
    - db_local_folder (str): Path to the local folder where the database will be saved.
    - df_pdfs (DataFrame): DataFrame containing PDF information.
    - pname (str): Name of the dataframe file.
    - db_load (object): Vector Database object to which documents will be added.
    - file_path (str): Path to the file to be added to the vector store.
    Returns:
    - db_load (object): Updated database object after adding documents.

    """

    # Add documents to Faiss and save database to local
    documents_all, metadatas_all, ids_all = create_documents_metadatas(
        files=[session.session_state[f"file_name_{num}"]],
        category=config.get("INDEX_NAME"),
    )

    db_load = create_db_from_documents(
        texts=documents_all,
        embedding=embeddings,
        metadatas=metadatas_all,
        ids=ids_all,
    )

    return db_load
