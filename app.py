import streamlit as st

billing = st.Page("pages/billing.py", title="Billing")
inventory = st.Page("pages/inventory.py", title="Inventory")
settings = st.Page("pages/settings.py", title="Settings")

pg = st.navigation([
    billing,
    inventory,
    settings
])

pg.run()