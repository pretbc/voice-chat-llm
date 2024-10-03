import streamlit as st
import streamlit_authenticator as stauth
import yaml
import jwt

from yaml.loader import SafeLoader


def authenticate_user(config_path: str = "auth.yaml") -> stauth.Authenticate | None:
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


def auth_token(config_path: str = "auth.yaml"):
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
    if config.get('token') is None:
        return False
    query = st.query_params
    token = query.get('token')
    if token:
        if len(token.split('.')) != 3:
            st.error("Token format is invalid.")
            return False
        try:
            decoded_token = jwt.decode(token, config['token'], algorithms=['HS256'])
            if 'sub' in decoded_token and decoded_token['sub'] == next(iter(config['credentials']['usernames'])):
                return True
            st.error("Invalid token claims.")
            return False
        except jwt.ExpiredSignatureError:
            st.error("Token has expired.")
        except jwt.InvalidTokenError as e:
            st.error(f"Invalid token: {str(e)}")
        except Exception as e:
            st.error(f"An error occurred during token validation: {str(e)}")
    return False
