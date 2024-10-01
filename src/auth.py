import streamlit as st
import streamlit_authenticator as stauth
import yaml

from yaml.loader import SafeLoader


def authenticate_user(config_path: str) -> stauth.Authenticate | None:
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Pre-hashing all plain text passwords once
    try:
        stauth.Hasher.hash_passwords(config['credentials'])
    except TypeError:
        return None

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        auto_hash=False
    )
    return authenticator
