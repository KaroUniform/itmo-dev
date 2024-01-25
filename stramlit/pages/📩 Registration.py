import streamlit as st
import requests
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config()

cookies = EncryptedCookieManager(
    password="My secret password",
)
if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()


st.title("elderly people safety App")
st.header("Registration")

st.write("Please Registration to have an access to a all functions.")

email = st.text_input("Email")
password = st.text_input("Password")

inputs = {
    "email": email,
    "password": password,
    "is_active": True,
    "is_superuser": False,
    "is_verified": False,
}

if st.button("Submit"):
    res = requests.post(
        url="https://api:8080/api/v1/auth/register", json=inputs, verify=False
    )
    if res.status_code == 201:
        st.success("Registration successful. Please now log in")
    else:
        st.error(f"Registration failed: {res.text}")
