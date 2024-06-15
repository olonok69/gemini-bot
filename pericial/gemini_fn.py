import google.generativeai as genai
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

secciones = [
    "antecedentes documentos",
    "antecedentes doctor",
    "estado actual",
    "consideraciones medico-legales",
    "conclusiones",
]


# Get the embeddings of each text and add to an embeddings column in the dataframe
def embed_fn(title, text, model):
    """
    Get the embeddings of each text and add to an embeddings column in the dataframe
    :param title: str
    :param text: str
    :param model: str
    :return: list
    """
    return genai.embed_content(
        model=model, content=text, task_type="retrieval_document", title=title
    )["embedding"]


def get_embeddings_model(model_name: str):
    return GoogleGenerativeAIEmbeddings(model=model_name)


def get_pinecone_objects(config, embeddings, index_name: str = "forensic"):

    pc = Pinecone(api_key=config.get("PINECONE_API_KEY"))
    index = pc.Index("forensic")

    vectorstore = PineconeVectorStore(embedding=embeddings, index_name=index_name)
    return index, vectorstore


def pericial_prompt_selected(st):
    st.session_state["pericial_prompt_selected"] = True
