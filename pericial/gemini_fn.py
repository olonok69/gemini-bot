import google.generativeai as genai
import os


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
