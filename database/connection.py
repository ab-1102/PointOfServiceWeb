import streamlit as st
from psycopg_pool import ConnectionPool
url = st.secrets["DATABASE_URL"]
@st.cache_resource
def get_connection_pool():
    return ConnectionPool(
        conninfo=url,
        min_size=1,
        max_size=5,
        timeout=10,
        open=True
    )


def get_db_connection():
    return get_connection_pool().connection()