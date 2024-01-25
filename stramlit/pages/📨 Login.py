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


st.title("elderly_people_safety App")
st.header("Login")

st.write(
    "Please login to have an access to a all functions. If you don't have an account, go to register page and create one."
)

email = st.text_input("Email")
password = st.text_input("Password")

inputs = {
    "username": email,
    "password": password,
}

if st.button("Submit"):
    res = requests.post(
        url="https://api:8080/api/v1/auth/login", data=inputs, verify=False
    )
    if res.status_code == 204:
        cookies["people_safety"] = res.cookies.get("people_safety")
        cookies.save()
        st.success("Login successful")
    else:
        st.error("Login failed")
