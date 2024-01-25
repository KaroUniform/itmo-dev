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
st.header("About me")

with st.spinner("Please wait, the data are loading"):
    res = requests.get(
        url="https://api:8080/api/v1/users/me",
        cookies={"people_safety": cookies.get("people_safety")},
        verify=False,
    )
if res.status_code == 200:
    st.table(res.json())
else:
    st.error("You are unauthorized")
