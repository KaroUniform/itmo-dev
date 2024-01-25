from datetime import datetime
import streamlit as st
import requests
from streamlit_cookies_manager import EncryptedCookieManager
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

cookies = EncryptedCookieManager(
    password="My secret password",
)
if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()


st.title("elderly people safety App")
st.header("Predictions history")

with st.spinner("Please wait, the logs are loading"):
    res = requests.get(
        url="https://api:8080/api/v1/users/history",
        cookies={"people_safety": cookies.get("people_safety")},
        verify=False,
    )
if res.status_code == 200:
    st.table(res.json())
    st.text("Here are your expenses for the last day")
    data = res.json()

    # Преобразование timestamp в формат даты и время
    for item in data:
        item["timestamp"] = datetime.strptime(
            item["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z"
        )

    # Создание датафрейма
    df = pd.DataFrame(data)

    # Определение временных границ
    min_timestamp = df["timestamp"].min()
    max_timestamp = df["timestamp"].max()

    # Определение частоты
    num_intervals = 10
    freq = (max_timestamp - min_timestamp) / num_intervals

    # Группировка и агрегация по динамической частоте
    df_grouped = (
        df.groupby(pd.Grouper(key="timestamp", freq=freq))
        .agg({"amount": lambda x: x[x > 0].sum()})
        .rename(columns={"amount": "supplement"})
        .join(
            df.groupby(pd.Grouper(key="timestamp", freq=freq))
            .agg({"amount": lambda x: x[x < 0].sum()})
            .rename(columns={"amount": "spent"})
        )
        .fillna(0)
    )

    # Превращение индекса в колонку
    df_grouped = df_grouped.reset_index()
    df_grouped["timestamp"] = df_grouped["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    st.bar_chart(
        df_grouped,
        x="timestamp",
        y=["supplement", "spent"],
        color=[
            "#DC143C",
            "#50C878",
        ],
    )
else:
    st.error("You are unauthorized")
