from vertexai.generative_models import GenerativeModel, Part, ChatSession
import vertexai.generative_models as generative_models
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import base64
import logging


def get_chat_response(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)

    try:
        for chunk in responses:

            if chunk.text:
                text_response.append(chunk.text)
        return "".join(text_response)
    except:

        return "error"


def start_chat(model):
    chat = model.start_chat(response_validation=False)
    return chat


def prepare_prompt(list_images, question, page_select, st, num):
    """
    Prepare the prompt for the chat session
    :param list_images: list of images
    :param question: question
    :param page_select: page selected
    :param st: st state
    :return: prompt
    """
    content = []
    if page_select == "all":
        mime_type = "application/pdf"
    else:
        mime_type = "image/jpeg"
    content = []
    for image in list_images:
        im_b64 = base64.b64encode(image).decode("utf8")
        image = Part.from_data(data=im_b64, mime_type=mime_type)
        content.append(image)
    prompt = [f"""{question} """] + content
    if len(content) > 0 and len(question) > 0:
        logging.info("Gemini app: prompt ready")
        st.session_state[f"prompt_{num}"] = prompt
        st.session_state[f"value_{num}"] = 5
        st.session_state[f"chat_true_{num}"] = "chat activo"
        st.session_state[f"buttom_send_not_clicked_{num}"] = True

    return


def init_model(config):
    return GenerativeModel(
        config["MODEL"],
        system_instruction=[
            """You a helpful agent who helps to extract relevant information from documents"""
        ],
        safety_settings={
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        },
        generation_config={
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        },
    )


def init_llm(model, credentials):
    """
    Initialize the chat model
    :param model: model
    :param credentials: credentials
    :return: ChatGoogleGenerativeAI
    """
    return ChatGoogleGenerativeAI(model=model, credentials=credentials)

def init_google_embeddings(config, credentials, google_api_key):
    """
    get embeddings model
    :param config: config
    :param credentials: credentials
    :param google_api_key: google api key
    :return: GoogleGenerativeAIEmbeddings
    """
    return GoogleGenerativeAIEmbeddings(
                    model=config.get("EMBEDDINGS2"),
                    credentials=credentials,
                    google_api_key=google_api_key,
                )