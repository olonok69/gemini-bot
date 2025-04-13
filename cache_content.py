import os.path
from pathlib import Path

from vertexai.generative_models import Part
from google.oauth2 import service_account
import vertexai
from dotenv import dotenv_values
import json
from src.model import init_model

from vertexai import caching
import datetime


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT_DIR)
PROJECT_DIR = path.parent.absolute().as_posix()
# # go to login page if not authenticated
# if (
#     st.session_state["authentication_status"] == None
#     or st.session_state["authentication_status"] == False
# ):
#     st.session_state.runpage = "main.py"
#     st.switch_page("main.py")


# Load the configuration and Initialize the Vertex AI client
config = dotenv_values(os.path.join(ROOT_DIR, "keys", ".env"))
credentials_path = os.path.join(
    ROOT_DIR, "keys", "complete-tube-421007-208a4862c992.json"
)
with open(credentials_path) as source:
    info = json.load(source)
# Create a service account credentials object
vertex_credentials = service_account.Credentials.from_service_account_info(info)
vertexai.init(
    project=config["PROJECT"],
    location=config["REGION"],
    credentials=vertex_credentials,
)

if "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = config.get("GEMINI-API-KEY")
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = config.get("GEMINI-API-KEY")
if "GOOGLE_CLOUD_PROJECT" not in os.environ:
    os.environ["GOOGLE_CLOUD_PROJECT"] = config.get("PROJECT")
if "GOOGLE_CLOUD_LOCATION" not in os.environ:
    os.environ["GOOGLE_CLOUD_LOCATION"] = config.get("REGION")
if "GOOGLE_GENAI_USE_VERTEXAI" not in os.environ:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
# create the model
model = init_model()
bucket_name = "gemini-bot-data"  # Replace with your bucket name
destination_blob_folder = (
    "input"  # Replace with the desired name in the bucket (can include folders)
)


system_instruction = """
Eres un experto en exytraer Informacion de documentos PDF

"""

contents = [
    Part.from_uri(
        uri="gs://gemini-bot-data/input/Ejemplo de Informe pericial Rosa Pinto Sánchez.pdf",
        mime_type="application/pdf",
    )
]

content_cache = caching.CachedContent.create(
    model_name="gemini-2.0-flash-001",
    system_instruction=system_instruction,
    contents=contents,
    ttl=datetime.timedelta(minutes=60),
)

print(content_cache.name)


cached_content = caching.CachedContent(cached_content_name=content_cache.name)
print(cached_content)
model = model.from_cached_content(cached_content=cached_content)


response = model.generate_content(
    "Extraer una lista con todos los antedecentes ordenada for fecha y resume las conclusiones del informe"
)
print(response.text)
print(response.usage_metadata)
