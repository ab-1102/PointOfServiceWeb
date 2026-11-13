import streamlit as st
import hashlib
import hmac

st.set_page_config(
    page_title="SOL Bites POS",
    layout="wide"
)


# ---------------- AUTHENTICATION ----------------

def verify_pin(pin, stored_hash):
    salt, expected_hash = stored_hash.split(":")

    calculated_hash = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode(),
        bytes.fromhex(salt),
        600_000
    ).hex()

    return hmac.compare_digest(calculated_hash, expected_hash)


def login():

    st.title("SOL Bites POS")
    st.subheader("Enter your PIN to continue")

    with st.form("login_form"):
        pin = st.text_input(
            "PIN",
            type="password",
            max_chars=20
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True
        )

    if submitted:

        if verify_pin(
            pin,
            st.secrets["auth"]["manager_pin_hash"]
        ):
            st.session_state.role = "manager"
            st.rerun()

        elif verify_pin(
            pin,
            st.secrets["auth"]["counter_pin_hash"]
        ):
            st.session_state.role = "counter"
            st.rerun()

        else:
            st.error("Incorrect PIN")


# ---------------- SESSION CHECK ----------------

if "role" not in st.session_state:

    login()
    st.stop()


# ---------------- LOGOUT ----------------

role = st.session_state.role

if role == "manager":

    if st.sidebar.button("Logout", use_container_width=True):
        del st.session_state.role
        st.rerun()

elif role == "counter":

    if st.button("Logout"):
        del st.session_state.role
        st.rerun()


# ---------------- NAVIGATION ----------------

billing = st.Page(
    "pages/billing.py",
    title="Billing"
)

inventory = st.Page(
    "pages/inventory.py",
    title="Inventory"
)

settings = st.Page(
    "pages/settings.py",
    title="Settings"
)


if role == "manager":

    pg = st.navigation(
        [billing, inventory, settings],
        position="sidebar"
    )

elif role == "counter":

    pg = st.navigation(
        [billing],
        position="hidden"
    )


pg.run()