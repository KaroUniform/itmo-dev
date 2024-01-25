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
st.header("Predict values")

st.write("Please enter your data:")

res = requests.get(
    url="https://api:8080/api/v1/models",
    cookies={"people_safety": cookies.get("people_safety")},
    verify=False,
)
if res.status_code == 200:
    res = res.json()
    model_names = [item["model_name"] for item in res]
else:
    st.error("You are unauthorized")
    st.stop()

model_name = st.selectbox("Choose a model for forecasting", model_names)

temperature = st.text_input("Enter temperature")
humidity = st.text_input("Enter humidity")
CO2CosIRValue = st.text_input("Enter CO2 concentration using CosIR technology")
CO2MG811Value = st.text_input("Enter CO2 concentration using MG811 sensor")
Mox1 = st.text_input("Enter value for MOx1 measurement")
Mox2 = st.text_input("Enter value for MOx2 measurement")
COValue = st.text_input("Enter CO concentration")
hour = st.text_input("Enter hour value")

inputs = {
    "temperature": temperature,
    "humidity": humidity,
    "CO2CosIRValue": CO2CosIRValue,
    "CO2MG811Value": CO2MG811Value,
    "MOX1": Mox1,
    "MOX2": Mox2,
    "COValue": COValue,
    "hour": hour,
}


if st.button("Predict", use_container_width=True):
    with st.spinner("Please wait, the calculation is underway"):
        res = requests.post(
            url="https://api:8080/api/v1/models/" + model_name,
            json=inputs,
            cookies={"people_safety": cookies.get("people_safety")},
            verify=False,
        )
        task_created_json = res.json()

        if "detail" in task_created_json:
            st.error("Недостаточно средств")
            st.stop()
        job_id = task_created_json["job_id"]

        res = requests.get(
            url="https://api:8080/api/v1/models/" + job_id,
            cookies={"people_safety": cookies.get("people_safety")},
            verify=False,
        )
        if res.status_code == 200:
            if res.text == "0":
                st.success(
                    "😌 Everything is fine, the sensor readings are 0. Your relatives don't need help"
                )
                st.balloons()
            elif res.text == "1":
                st.error(
                    "😨 The system has detected an anomaly, urgently check your relatives!"
                )
            else:
                st.info("🫠Something went wrong.")

            st.info(
                f"💸 The cost of the predict: {task_created_json['amount_spent']}; You have {task_created_json['remaining_balance']} money left"
            )
