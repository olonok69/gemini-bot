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

name, authentication_status, username = authenticator.login(
    key="Login", location="sidebar"
)

print(name, authentication_status, username)
