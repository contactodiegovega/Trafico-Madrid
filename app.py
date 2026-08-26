import streamlit as st
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import plotly.express as px
from pyproj import Transformer
import sqlite3
# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------

st.set_page_config(
    page_title="Madrid Traffic Explorer",
    page_icon="🚦",
    layout="wide"
)

# --------------------------------------------------
# ESTILOS
# --------------------------------------------------

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.hero {
    padding: 1.8rem 2rem;
    border-radius: 20px;
    background: linear-gradient(
        120deg,
        rgba(30, 41, 59, 0.95),
        rgba(15, 23, 42, 0.95)
    );
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 1.4rem;
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
}

.hero-subtitle {
    color: #a8b2c1;
    font-size: 1rem;
}

.update-pill {
    display: inline-block;
    padding: 0.45rem 0.8rem;
    border-radius: 999px;
    background: rgba(34,197,94,0.15);
    color: #4ade80;
    font-size: 0.9rem;
    margin-top: 1rem;
}

.kpi-card {
    padding: 1.2rem 1.3rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    min-height: 120px;
}

.kpi-label {
    color: #9ca3af;
    font-size: 0.85rem;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    margin-top: 0.35rem;
}

.section-title {
    font-size: 1.45rem;
    font-weight: 700;
    margin-top: 1rem;
    margin-bottom: 0.8rem;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# CARGA Y LIMPIEZA DE DATOS
# --------------------------------------------------

@st.cache_data(ttl=300)
def cargar_trafico_actual():

    url = (
        "https://datos.madrid.es/dataset/"
        "202087-0-trafico-intensidad/resource/"
        "202087-0-trafico-intensidad/download/"
        "202087-0-trafico-intensidad.xml"
    )

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    fecha_hora = root.find("fecha_hora").text

    registros = []

    for pm in root.findall("pm"):

        fila = {
            "fecha_hora": fecha_hora
        }

        for campo in pm:
            fila[campo.tag] = campo.text

        registros.append(fila)

    df = pd.DataFrame(registros)

    # Fecha
    df["fecha_hora"] = pd.to_datetime(
        df["fecha_hora"],
        format="%d/%m/%Y %H:%M:%S"
    )

    # Variables numéricas
    columnas_numericas = [
        "intensidad",
        "ocupacion",
        "carga",
        "nivelServicio",
        "intensidadSat"
    ]

    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

    # Coordenadas
    df["st_x"] = pd.to_numeric(
        df["st_x"].str.replace(",", ".", regex=False),
        errors="coerce"
    )

    df["st_y"] = pd.to_numeric(
        df["st_y"].str.replace(",", ".", regex=False),
        errors="coerce"
    )

     # Transformar coordenadas UTM a latitud y longitud

    transformer = Transformer.from_crs(
    "EPSG:25830",
    "EPSG:4326",
    always_xy=True
    )

    longitudes, latitudes = transformer.transform(
    df["st_x"].values,
    df["st_y"].values
    )

    df["longitud"] = longitudes
    df["latitud"] = latitudes


    # Eliminar velocidad
    if "velocidad" in df.columns:
        df = df.drop(columns=["velocidad"])

    # Solo registros válidos
    df = df[df["error"] == "N"].copy()

    # -1 = ausencia de dato
    columnas_menos_uno = [
        "intensidad",
        "ocupacion",
        "carga",
        "nivelServicio"
    ]

    df[columnas_menos_uno] = (
        df[columnas_menos_uno]
        .replace(-1, pd.NA)
    )

    # Estado de tráfico
    mapa_nivel = {
        0: "Fluido",
        1: "Lento",
        2: "Retenciones",
        3: "Congestión"
    }

    df["estado_trafico"] = (
        df["nivelServicio"]
        .map(mapa_nivel)
    )

    return df, fecha_hora
# --------------------------------------------------
# GUARDAR CAPTURAS EN SQLITE
# --------------------------------------------------

def guardar_captura_sqlite(df):

    conexion = sqlite3.connect("trafico_madrid.db")

    # Crear tabla si todavía no existe
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS trafico (
            idelem TEXT,
            fecha_hora TEXT,
            descripcion TEXT,
            accesoAsociado TEXT,
            intensidad REAL,
            ocupacion REAL,
            carga REAL,
            nivelServicio REAL,
            intensidadSat REAL,
            error TEXT,
            subarea TEXT,
            st_x REAL,
            st_y REAL,
            estado_trafico TEXT,
            PRIMARY KEY (idelem, fecha_hora)
        )
    """)

    columnas_db = [
        "idelem",
        "fecha_hora",
        "descripcion",
        "accesoAsociado",
        "intensidad",
        "ocupacion",
        "carga",
        "nivelServicio",
        "intensidadSat",
        "error",
        "subarea",
        "st_x",
        "st_y",
        "estado_trafico"
    ]

    datos = df[columnas_db].copy()

    # Convertir fecha a texto para SQLite
    datos["fecha_hora"] = datos["fecha_hora"].astype(str)

    # Convertir NaN / pd.NA a None
    datos = datos.astype(object).where(
        pd.notnull(datos),
        None
    )

    sql = """
        INSERT OR IGNORE INTO trafico (
            idelem,
            fecha_hora,
            descripcion,
            accesoAsociado,
            intensidad,
            ocupacion,
            carga,
            nivelServicio,
            intensidadSat,
            error,
            subarea,
            st_x,
            st_y,
            estado_trafico
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cambios_antes = conexion.total_changes

    conexion.executemany(
        sql,
        datos.itertuples(index=False, name=None)
    )

    conexion.commit()

    nuevos_registros = (
        conexion.total_changes - cambios_antes
    )

    conexion.close()

    return nuevos_registros

# --------------------------------------------------
# CARGAR DATOS
# --------------------------------------------------

try:
    df_actual, ultima_actualizacion = cargar_trafico_actual()

    nuevos_registros = guardar_captura_sqlite(df_actual)

except Exception as e:
    st.error(
        "No se han podido cargar los datos del Ayuntamiento de Madrid."
    )
    st.exception(e)
    st.stop()


# --------------------------------------------------
# CABECERA
# --------------------------------------------------

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">🚦 Madrid Traffic Explorer</div>
        <div class="hero-subtitle">
            Descubre cómo se mueve Madrid ahora mismo.
            Tráfico actualizado a partir de los datos oficiales del Ayuntamiento.
        </div>
        <div class="update-pill">
            ● Actualizado {ultima_actualizacion}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if nuevos_registros > 0:
    st.toast(
        f"📥 Nueva captura guardada: {nuevos_registros:,} mediciones"
    )
# --------------------------------------------------
# KPIs
# --------------------------------------------------

total = len(df_actual)

fluido = (
    df_actual["estado_trafico"] == "Fluido"
).sum()

lento = (
    df_actual["estado_trafico"] == "Lento"
).sum()

retenciones = (
    df_actual["estado_trafico"] == "Retenciones"
).sum()

congestion = (
    df_actual["estado_trafico"] == "Congestión"
).sum()


cols = st.columns(5)

datos_kpi = [
    ("📍 Puntos analizados", total),
    ("🟢 Fluido", fluido),
    ("🟡 Lento", lento),
    ("🟠 Retenciones", retenciones),
    ("🔴 Congestión", congestion)
]

for col, (titulo, valor) in zip(cols, datos_kpi):

    with col:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{titulo}</div>
                <div class="kpi-value">{valor:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# --------------------------------------------------
# PESTAÑAS
# --------------------------------------------------

tab_ahora, tab_mapa, tab_historico, tab_chat = st.tabs(
    [
        "🚦 Ahora",
        "🗺️ Mapa",
        "📈 Histórico",
        "💬 Chat IA"
    ]
)


# --------------------------------------------------
# TAB AHORA
# --------------------------------------------------

with tab_ahora:

    st.markdown(
        '<div class="section-title">Estado actual de Madrid</div>',
        unsafe_allow_html=True
    )

    distribucion = (
        df_actual["estado_trafico"]
        .value_counts()
        .reindex(
            ["Fluido", "Lento", "Retenciones", "Congestión"]
        )
        .fillna(0)
        .reset_index()
    )

    distribucion.columns = [
        "Estado",
        "Puntos"
    ]

    fig = px.bar(
        distribucion,
        x="Estado",
        y="Puntos",
        text="Puntos",
        color="Estado",
        color_discrete_map={
            "Fluido": "#34d399",
            "Lento": "#facc15",
            "Retenciones": "#fb923c",
            "Congestión": "#f43f5e"
        }
    )

    fig.update_layout(
        showlegend=False,
        height=420,
        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10
        ),
        xaxis_title="",
        yaxis_title="Puntos de medición",
        hovermode="x"
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # ----------------------------------------------
    # TOP PUNTOS CON MÁS PROBLEMAS
    # ----------------------------------------------

    st.markdown(
        '<div class="section-title">⚠️ Puntos con mayor carga ahora</div>',
        unsafe_allow_html=True
    )

    top_problemas = (
        df_actual[
            df_actual["estado_trafico"].isin(
                ["Retenciones", "Congestión"]
            )
        ]
        .sort_values(
            "carga",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_problemas[
            [
                "descripcion",
                "estado_trafico",
                "intensidad",
                "ocupacion",
                "carga"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# TAB MAPA
# --------------------------------------------------

with tab_mapa:

    st.markdown(
        '<div class="section-title">🗺️ Mapa del tráfico en tiempo real</div>',
        unsafe_allow_html=True
    )

    # Estados que puede seleccionar el usuario
    estados_disponibles = [
        "Fluido",
        "Lento",
        "Retenciones",
        "Congestión"
    ]

    estados_seleccionados = st.multiselect(
        "Estado del tráfico",
        options=estados_disponibles,
        default=estados_disponibles
    )

    # Filtrar según la selección
    df_mapa = df_actual[
        df_actual["estado_trafico"].isin(estados_seleccionados)
    ].copy()

    # Eliminar registros sin coordenadas
    df_mapa = df_mapa.dropna(
        subset=["latitud", "longitud"]
    )

    # Crear mapa interactivo
    fig_mapa = px.scatter_map(
        df_mapa,
        lat="latitud",
        lon="longitud",
        color="estado_trafico",
        hover_name="descripcion",
        hover_data={
            "intensidad": True,
            "ocupacion": True,
            "carga": True,
            "latitud": False,
            "longitud": False
        },
        color_discrete_map={
            "Fluido": "#34d399",
            "Lento": "#facc15",
            "Retenciones": "#fb923c",
            "Congestión": "#f43f5e"
        },
        zoom=10.5,
        height=650
    )

    # Personalizar información al pasar el ratón
    fig_mapa.update_traces(
        hovertemplate=
            "<b>%{hovertext}</b><br><br>"
            "🚗 Flujo de vehículos: %{customdata[0]:.0f} veh/h<br>"
            "📊 Ocupación de la vía: %{customdata[1]:.0f}%<br>"
            "🚦 Saturación de la vía: %{customdata[2]:.0f}%"
            "<extra></extra>"
    )

    # Configurar aspecto y posición del mapa
    fig_mapa.update_layout(
        map_style="open-street-map",
        map_center={
            "lat": 40.4168,
            "lon": -3.7038
        },
        map_zoom=10,
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        )
    )

    # Mostrar mapa
    st.plotly_chart(
        fig_mapa,
        use_container_width=True
    )

    st.caption(
        f"Mostrando {len(df_mapa):,} puntos de medición."
    )



# --------------------------------------------------
# TAB HISTÓRICO
# --------------------------------------------------

with tab_historico:

    st.markdown(
        '<div class="section-title">📈 Evolución histórica del tráfico</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Consulta cómo ha evolucionado el tráfico en cada punto "
        "a partir de las mediciones almacenadas en SQLite."
    )

    # Conectar con SQLite
    conexion_db = sqlite3.connect("trafico_madrid.db")

    # Leer datos históricos
    df_historico = pd.read_sql_query(
        """
        SELECT *
        FROM trafico
        ORDER BY fecha_hora
        """,
        conexion_db
    )

    conexion_db.close()

    # Convertir fecha a datetime
    df_historico["fecha_hora"] = pd.to_datetime(
        df_historico["fecha_hora"]
    )

    # --------------------------------------------------
    # INFORMACIÓN GENERAL DEL HISTÓRICO
    # --------------------------------------------------

    numero_registros = len(df_historico)

    numero_capturas = df_historico["fecha_hora"].nunique()

    numero_puntos = df_historico["idelem"].nunique()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📊 Mediciones almacenadas",
        f"{numero_registros:,}"
    )

    col2.metric(
        "🕒 Capturas históricas",
        numero_capturas
    )

    col3.metric(
        "📍 Puntos registrados",
        f"{numero_puntos:,}"
    )

    st.divider()

    # --------------------------------------------------
    # SELECTOR DE PUNTO
    # --------------------------------------------------

    puntos = (
        df_historico[
            ["idelem", "descripcion"]
        ]
        .drop_duplicates()
        .dropna(subset=["descripcion"])
        .sort_values("descripcion")
    )

    opciones_puntos = {
        f"{fila.descripcion} · ID {fila.idelem}": fila.idelem
        for fila in puntos.itertuples()
    }

    punto_seleccionado = st.selectbox(
        "📍 Selecciona un punto de medición",
        options=list(opciones_puntos.keys())
    )

    id_seleccionado = opciones_puntos[punto_seleccionado]

    # Filtrar histórico del punto
    df_punto = df_historico[
        df_historico["idelem"] == id_seleccionado
    ].copy()

    # --------------------------------------------------
    # GRÁFICO DE EVOLUCIÓN
    # --------------------------------------------------

    st.subheader("Evolución del tráfico")

    indicador = st.selectbox(
        "¿Qué quieres analizar?",
        [
            "Flujo de vehículos",
            "Ocupación de la vía",
            "Saturación de la vía"
        ]
    )

    mapa_indicadores = {
        "Flujo de vehículos": {
            "columna": "intensidad",
            "unidad": "veh/h"
        },
        "Ocupación de la vía": {
            "columna": "ocupacion",
            "unidad": "%"
        },
        "Saturación de la vía": {
            "columna": "carga",
            "unidad": "%"
        }
    }

    columna = mapa_indicadores[indicador]["columna"]
    unidad = mapa_indicadores[indicador]["unidad"]

    fig_historico = px.line(
        df_punto,
        x="fecha_hora",
        y=columna,
        markers=True,
        labels={
            "fecha_hora": "Fecha y hora",
            columna: f"{indicador} ({unidad})"
        }
    )

    fig_historico.update_layout(
        height=480,
        xaxis_title="",
        yaxis_title=f"{indicador} ({unidad})",
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )

    st.plotly_chart(
        fig_historico,
        use_container_width=True
    )

# --------------------------------------------------
# TAB CHAT
# --------------------------------------------------

with tab_chat:

    st.info(
        "💬 Aquí integraremos el chat con IA sobre los datos de tráfico."
    )