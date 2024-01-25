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


st.title("👴 elderly people safety App")
st.header(
    "👋 Hi! Get information about if something is wrong based on different sensors"
)

col1, col2, col3 = st.columns(3)

st.text(
    "There are many machine learning models available to you to choose from,\nchoose at your discretion!"
)

with col1:
    st.header("🌳Decision tree")
    st.image("stramlit/static/forest.png")
    st.text("💵 Cost: 5.\n➕ Good performance,\n➕ great accuracy")

with col2:
    st.header("🔍LightGBM")
    st.image("stramlit/static/lgmb.png")
    st.text("💵 Cost: 8.\n➕ Good performance,\n➕ highest accuracy,\n➖ high price")

with col3:
    st.header("📈Logistic regression")
    st.image("stramlit/static/logreg.png")
    st.text("💵 Cost: 3.\n➖ Good accuracy,\n➕ good performance,\n➕ price compromise")

st.header("Check the 🥠 Prediction 🥠 page to create a prediction!")
st.header("Also check out our docs API: karouniform.xyz:8080/docs")
