# modulo de conexion a la base de datos

import streamlit as st
import pandas as pd
import pg8000


@st.cache_resource
def init_connections():
    return pg8000.connect(**st.secrets["connections"]["postgresql"])


conn = init_connections()


@st.cache_data(ttl=600)
def run_query(sql_query, params=None):
    try:
        with conn.cursor() as cur:
            if params:
                cur.execute(sql_query, params)
            else:
                cur.execute(sql_query)

            # Si es un SELECT, obtiene datos.
            data = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            return pd.DataFrame(data, columns=column_names)
    except Exception as e:
        # Maneja cualquier otro error SQL
        st.error(f"Error al ejecutar la consulta: {e}")
        conn.rollback()
        st.stop()
