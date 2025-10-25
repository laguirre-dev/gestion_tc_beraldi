# modulo de conexion a la base de datos

import streamlit as st
from sqlalchemy import create_engine, Connection


def connect_bd() -> tuple[Connection, Connection.cursor]:
    try:
        server = st.secrets["BERALDI_API_DB_HOST"]
        database = st.secrets["BERALDI_API_DB_NAME"]
        user = st.secrets["BERALDI_API_DB_USER"]
        password = st.secrets["BERALDI_API_DB_PASSWORD"]
        port = st.secrets["BERALDI_API_DB_PORT"]
        conn = create_engine(
            f"postgresql://{user}:{password}@{server}:{port}/{database}"
        )
        return conn, conn.cursor()
    except Exception as e:
        st.toast(f"Error al conectar a la base de datos: {e}", icon="🚨")
        return None
