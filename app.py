import streamlit as st

print('Streamlit Main UI')
print()

billing = st.Page("pages/Billing.py", title="Billing")
inventory = st.Page("pages/Inventory.py", title="Inventory")
settings = st.Page("pages/Settings.py", title="Settings")

pg = st.navigation([
    billing,
    inventory,
    settings,
])

pg.run()

print('end')