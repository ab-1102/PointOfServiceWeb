import streamlit as st
from pathlib import Path
import json

js_path = Path(__file__).parent / "connection.js"

with open(js_path, "r", encoding="utf-8") as file:
    JS = file.read()

link = st.components.v2.component(
    name="connection",
    js=JS
)


def send_to_local(bill_data):
    bill_json = json.dumps(bill_data, default=str)

    link(
        data={"bill_json": bill_json},
        key="connection"
    )