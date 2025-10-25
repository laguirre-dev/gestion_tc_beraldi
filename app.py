# modulo principal de la aplicacion
import streamlit as st
from conexiones import connect_bd

st.title("Hola!")

conn, cursor = connect_bd()
st.write(conn)
st.write(cursor)