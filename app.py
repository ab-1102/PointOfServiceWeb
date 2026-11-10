import streamlit as st

billing = st.Page("pages/billing.py", title="Billing")
inventory = st.Page("pages/inventory.py", title="Inventory")
settings = st.Page("pages/settings.py", title="Settings")
bridge_test = st.Page("pages/bridge_test.py", title="Bridge Test")

pg = st.navigation([
    billing,
    inventory,
    settings,
    bridge_test,
])

pg.run()