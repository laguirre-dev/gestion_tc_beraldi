# modulo de conexion a la base de datos

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text


@st.cache_resource
def init_connection():
    connection_string = (
        f"postgresql+pg8000://{st.secrets['connections']['postgresql']['user']}:"
        f"{st.secrets['connections']['postgresql']['password']}@"
        f"{st.secrets['connections']['postgresql']['host']}:"
        f"{st.secrets['connections']['postgresql']['port']}/"
        f"{st.secrets['connections']['postgresql']['database']}"
    )
    return create_engine(connection_string)


@st.cache_data(ttl=600)
def run_query(sql_query, params=None):
    try:
        engine = init_connection()
        with engine.connect() as connection:
            result = connection.execute(text(sql_query), params or {})
            # Si la consulta devuelve datos (SELECT)
            if result.returns_rows:
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                return df
            else:
                connection.commit()
                return None
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")
        st.stop()
