# modulo principal de la aplicacion
import streamlit as st
from conexiones import run_query
from querys import get_all_tc
import pandas as pd
import datetime

# creamos 2 variables fecha, hoy y hace un mes
hoy = datetime.date.today()
hace_un_mes = hoy - datetime.timedelta(days=30)

# Configuracion de la web
st.set_page_config(
    page_title="Gestion de TC - Beraldi",
    page_icon=":warning:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def crea_tendencias(dataframe):
    t = pd.DataFrame(
        {
            "pregunta": [
                "Contador Total",
                'Contador "Cumple"',
                'Contador "No Cumple"',
                'Contador "No Aplica"',
                "% No Cumple",
            ]
        }
    )
    for col in dataframe.columns:
        cumple = (dataframe[col] == "Cumple").sum()
        no_cumple = (dataframe[col] == "No Cumple").sum()
        no_aplica = (dataframe[col] == "No Aplica").sum()
        total = cumple + no_cumple + no_aplica
        por_no_cumple = (no_cumple / total) * 100 if total > 0 else 0
        if total > 0:
            t[col] = [total, cumple, no_cumple, no_aplica, por_no_cumple]
    return t


def crea_resumen_tendencias(dataframe):
    return dataframe.melt(
        id_vars=["pregunta"], var_name="id_pregunta", value_name="valor"
    )


def filtra_tendencia(dataframe):
    return dataframe[
        (dataframe["pregunta"] == "% No Cumple") & (dataframe["valor"] > 0)
    ]


# si no hay un df en session_state, les asignamos valores vacios a los de la sesion
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
if "df_filtered" not in st.session_state:
    st.session_state.df_filtered = pd.DataFrame()

# traemos el df de session_state
df = st.session_state.df
df_filtered = st.session_state.df_filtered

# creamos una barra lateral con filtros de fecha
with st.sidebar:
    st.image(st.secrets["URL_LOGO"], width="content")
    st.subheader("Filtros", divider="orange")
    fechas = st.date_input(
        "Rango de fechas:",
        value=(hace_un_mes, hoy),
    )
    if st.button("Actualizar", key="a|ctualizar", type="primary"):
        df = run_query(get_all_tc(), fechas)
        st.session_state.df = df
    if not df.empty:
        if st.toggle("Filtrar por columna"):
            col = st.selectbox(
                "Columna a filtrar",
                df.columns,
                key="col",
                help="Elija la columna que desea filtrar por algun valor existente",
            )
            df_filter = df[col].unique()
            # valor de la columna
            val = st.selectbox("Valor a filtrar", df_filter)
            # mostramos el df filtrado
            df_prefiltrado = df[df[col] == val]
            # filtro multiselect de tipo
            tipo = st.multiselect("Tipo", df["tipo"].unique(), key="tipo")
            if tipo:
                df_prefiltrado = df_prefiltrado[df_prefiltrado["tipo"].isin(tipo)]
            # filtro multiselect por instructor
            instructor = st.multiselect(
                "Instructor", df["Instructor"].unique(), key="instructor"
            )
            if instructor:
                df_prefiltrado = df_prefiltrado[
                    df_prefiltrado["Instructor"].isin(instructor)
                ]
            # aplica el filtro al df principal
            df_filtered = df_prefiltrado


if not df.empty:
    st.title("Reporte de :primary[Gestion para Test de Competencia]")
    # columna a filtrar
    if not df_filtered.empty:
        df_actual = df_filtered
    else:
        df_actual = df
    # transformamos columna
    df_actual["puntaje"] = df_actual["puntaje"].astype(float)

    # Seccion principal
    st.subheader("Resultados 🎯", divider="orange")
    # aprobadas
    aprobadas = df_actual[df_actual["puntaje"] > 80]
    # desaprobadas
    desaprobadas = df_actual[df_actual["puntaje"] < 80]
    _col2, _col1 = st.columns([1, 5])
    _col1.write(df_actual)
    _col2.metric(":orange[Total TC]", len(df_actual), border=True)
    _col2.metric(":green[Aprobadas]", len(aprobadas), border=True)
    _col2.metric(":red[Desaprobadas]", len(desaprobadas), border=True)

    # Seccion de graficos
    st.subheader("Graficos 📊", divider="orange")
    # grafico de lineas en donde se fija fecha_realizacion vs puntaje por chofer
    col1, col2 = st.columns([3, 1])
    # hacemos 4 graficos, uno para cada tipo de tc
    df_filtrado_carga = df_actual[df_actual["tipo"] == "CARGA"]
    df_filtrado_descarga = df_actual[df_actual["tipo"] == "DESCARGA"]
    df_filtrado_ipv = df_actual[df_actual["tipo"] == "IPV"]
    df_filtrado_manejo = df_actual[df_actual["tipo"] == "MANEJO"]
    # grafico 1: carga
    _col1, _col2 = col1.columns(2)
    _col1.badge("CARGA")
    _col1.scatter_chart(
        df_filtrado_carga,
        x="fecha_realizacion",
        y="puntaje",
        color="chofer",
        height=280,
    )
    # grafico 2: descarga
    _col1.badge("DESCARGA", color="orange")
    _col1.scatter_chart(
        df_filtrado_descarga,
        x="fecha_realizacion",
        y="puntaje",
        color="chofer",
        height=280,
    )
    # grafico 3: ipv
    _col2.badge("IPV", color="violet")
    _col2.scatter_chart(
        df_filtrado_ipv, x="fecha_realizacion", y="puntaje", color="chofer", height=280
    )
    # grafico 4: manejo
    _col2.badge("MANEJO", color="green")
    _col2.scatter_chart(
        df_filtrado_manejo,
        x="fecha_realizacion",
        y="puntaje",
        color="chofer",
        height=280,
    )
    # grafico 5: cantidad de tc por tipo (totalizado)
    count_tipo = df_actual["tipo"].value_counts()
    tot_carga = count_tipo["CARGA"] if "CARGA" in count_tipo else 0
    tot_descarga = count_tipo["DESCARGA"] if "DESCARGA" in count_tipo else 0
    tot_ipv = count_tipo["IPV"] if "IPV" in count_tipo else 0
    tot_manejo = count_tipo["MANEJO"] if "MANEJO" in count_tipo else 0
    # podemos metricas debajo del grafico de barras
    _scol1, _scol2 = col2.columns(2)
    _scol1.metric(":blue[CARGA]", tot_carga, border=True)
    _scol1.metric(":orange[DESCARGA]", tot_descarga, border=True)
    _scol2.metric(":violet[IPV]", tot_ipv, border=True)
    _scol2.metric(":green[MANEJO]", tot_manejo, border=True)
    col2.bar_chart(count_tipo, color="#ff5500")

    # porcentaje de tendencias segun tipo de tc
    ## creamos el Dataframe modelo
    tendencias = pd.DataFrame(
        {
            "pregunta": [
                "Contador Total",
                'Contador "Cumple"',
                'Contador "No Cumple"',
                'Contador "No Aplica"',
                "% No Cumple",
            ]
        }
    )

    ## Separamos los DataFrames
    df_carga = df_actual[df_actual["tipo"] == "CARGA"]
    df_descarga = df_actual[df_actual["tipo"] == "DESCARGA"]
    df_ipv = df_actual[df_actual["tipo"] == "IPV"]
    df_manejo = df_actual[df_actual["tipo"] == "MANEJO"]

    ## Separamos y mostramos las tendencias
    tf_carga = crea_tendencias(df_carga)
    tf_descarga = crea_tendencias(df_descarga)
    tf_ipv = crea_tendencias(df_ipv)
    tf_manejo = crea_tendencias(df_manejo)
    ##  hacemos dinamica de todas
    tf_carga_melteado = crea_resumen_tendencias(tf_carga)
    tf_descarga_melteado = crea_resumen_tendencias(tf_descarga)
    tf_ipv_melteado = crea_resumen_tendencias(tf_ipv)
    tf_manejo_melteado = crea_resumen_tendencias(tf_manejo)
    ## Mostramos la info
    st.subheader("Tendencias 🔥", divider="orange")
    st.title("__CARGA__")
    col1, col2 = st.columns(2)
    col1.bar_chart(
        filtra_tendencia(tf_carga_melteado),
        x="id_pregunta",
        y="valor",
        color="id_pregunta",
    )
    col2.dataframe(tf_carga.set_index("pregunta"))
    st.title("__DESCARGA__")
    col1, col2 = st.columns(2)
    col1.bar_chart(
        filtra_tendencia(tf_descarga_melteado),
        x="id_pregunta",
        y="valor",
        color="id_pregunta",
    )
    col2.dataframe(tf_descarga.set_index("pregunta"))
    st.title("__IPV__")
    col1, col2 = st.columns(2)
    col1.bar_chart(
        filtra_tendencia(tf_ipv_melteado),
        x="id_pregunta",
        y="valor",
        color="id_pregunta",
    )
    col2.dataframe(tf_ipv.set_index("pregunta"))
    st.title("__MANEJO__")
    col1, col2 = st.columns(2)
    col1.bar_chart(
        filtra_tendencia(tf_manejo_melteado),
        x="id_pregunta",
        y="valor",
        color="id_pregunta",
    )
    col2.dataframe(tf_manejo.set_index("pregunta"))


else:
    no_df_con = st.container(horizontal_alignment="center")
    no_df_con.info(
        "Por favor, seleccione un rango de fechas y actualice", icon="🔎", width=400
    )
