from vertexai.generative_models import GenerativeModel, Part, ChatSession
import base64


def get_chat_response(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)

    try:
        for chunk in responses:

            if chunk.text:
                text_response.append(chunk.text)
        return "".join(text_response)
    except:
        for chuck in responses:
            print(chuck)
        return "error"


def start_chat(model):
    chat = model.start_chat(response_validation=False)
    return chat


def prepare_prompt(list_images, question, page_select, st):
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
        print("here")
        st.session_state["prompt"] = prompt
        st.session_state.value = 5
        st.session_state["chat_true"] = "chat activo"
        st.session_state["buttom_send_not_clicked"] = True

    return
