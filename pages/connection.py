import streamlit as st
from pathlib import Path

js_path = Path(__file__).parent / "connection.js"

with open(js_path, "r", encoding="utf-8") as file:
    JS = file.read()

link = st.components.v2.component(
    name="connection",
    js=JS
)


def send_to_local(bill_data):
    link(
        data={"bill_data": bill_data},
        key="connection"
    )
