import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader

with open("keys/config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)


authenticator = Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)
st.write("Forensic Reports Tools. Powered by Gemini, Langchain and Pinecone")
(
    st.session_state["name"],
    st.session_state["authentication_status"],
    st.session_state["username"],
) = authenticator.login(key="Login", location="main")


if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "main")
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title("Some content")
elif st.session_state["authentication_status"] == False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] == None:
    st.warning("Please enter your username and password")
