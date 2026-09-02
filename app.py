import streamlit as st
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import plotly.express as px
from pyproj import Transformer
import sqlite3
import ollama
import textwrap
from rapidfuzz import process, fuzz
# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------

st.set_page_config(
    page_title="Madrid Traffic Explorer",
    page_icon="🚦",
    layout="wide"
)

# --------------------------------------------------
# --------------------------------------------------
# ESTILOS
# --------------------------------------------------

st.markdown("""
<style>

/* ================================
   FONDO GENERAL
================================ */

.stApp {
    background:
        radial-gradient(
            circle at 15% 0%,
            rgba(59, 130, 246, 0.12),
            transparent 28%
        ),
        radial-gradient(
            circle at 85% 5%,
            rgba(52, 211, 153, 0.08),
            transparent 25%
        ),
        #070b14;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

[data-testid="stHeader"] {
    background: rgba(7, 11, 20, 0.80);
}


/* ================================
   HERO
================================ */

.hero {
    position: relative;
    overflow: hidden;

    padding: 2.4rem 2.5rem;

    border-radius: 28px;

    background:
        linear-gradient(
            135deg,
            rgba(17, 24, 39, 0.98),
            rgba(8, 15, 29, 0.98)
        );

    border: 1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 20px 60px rgba(0,0,0,0.30);

    margin-bottom: 1.2rem;
}


.hero::after {

    content: "";

    position: absolute;

    width: 380px;
    height: 380px;

    right: -150px;
    top: -220px;

    border-radius: 50%;

    background:
        rgba(52, 211, 153, 0.12);

    filter: blur(10px);
}


.eyebrow {

    color: #60a5fa;

    font-size: 0.75rem;

    letter-spacing: 0.17em;

    font-weight: 800;

    text-transform: uppercase;

    margin-bottom: 0.9rem;
}


.hero-title {

    font-size: clamp(2.5rem, 5vw, 4.5rem);

    line-height: 0.95;

    font-weight: 900;

    letter-spacing: -0.055em;

    margin-bottom: 1rem;
}


.hero-title span {
    color: #34d399;
}


.hero-subtitle {

    color: #9ba8bb;

    font-size: 1.05rem;

    max-width: 780px;

    line-height: 1.65;
}


/* ================================
   LIVE BADGE
================================ */

.update-pill {

    display: inline-flex;

    align-items: center;

    gap: 0.6rem;

    padding: 0.5rem 0.85rem;

    border-radius: 999px;

    background:
        rgba(52, 211, 153, 0.10);

    border:
        1px solid rgba(52, 211, 153, 0.25);

    color: #6ee7b7;

    font-size: 0.85rem;

    font-weight: 700;

    margin-top: 1.3rem;
}


.live-dot {

    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #34d399;

    animation: pulse 1.8s infinite;
}


@keyframes pulse {

    0% {
        box-shadow:
            0 0 0 0
            rgba(52,211,153,0.45);
    }

    70% {
        box-shadow:
            0 0 0 10px
            rgba(52,211,153,0);
    }

    100% {
        box-shadow:
            0 0 0 0
            rgba(52,211,153,0);
    }
}


/* ================================
   ESTADO GENERAL
================================ */

.status-panel {

    padding: 1.1rem 1.3rem;

    border-radius: 18px;

    background:
        rgba(255,255,255,0.035);

    border:
        1px solid rgba(255,255,255,0.07);

    margin:
        0.3rem 0 1.1rem 0;
}


.status-title {

    font-size: 1rem;

    font-weight: 800;

    margin-bottom: 0.3rem;
}


.status-text {

    color: #94a3b8;

    font-size: 0.9rem;
}


/* ================================
   KPI CARDS
================================ */

.kpi-card {

    padding: 1.25rem;

    border-radius: 20px;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.055),
            rgba(255,255,255,0.025)
        );

    border:
        1px solid rgba(255,255,255,0.075);

    min-height: 125px;

    transition:
        transform 0.2s ease,
        border-color 0.2s ease;
}


.kpi-card:hover {

    transform:
        translateY(-4px);

    border-color:
        rgba(255,255,255,0.17);
}


.kpi-label {

    color: #91a0b5;

    font-size: 0.78rem;

    font-weight: 700;

    letter-spacing: 0.03em;
}


.kpi-value {

    font-size: 2.2rem;

    font-weight: 850;

    letter-spacing: -0.04em;

    margin-top: 0.4rem;
}


.kpi-note {

    color: #64748b;

    font-size: 0.73rem;

    margin-top: 0.25rem;
}


/* ================================
   TÍTULOS
================================ */

.section-kicker {

    color: #60a5fa;

    font-size: 0.72rem;

    letter-spacing: 0.15em;

    font-weight: 800;

    text-transform: uppercase;

    margin-top: 1.3rem;
}


.section-title {

    font-size: 1.7rem;

    font-weight: 850;

    letter-spacing: -0.03em;

    margin-top: 0.15rem;

    margin-bottom: 1rem;
}


/* ================================
   TABS
================================ */

div[data-baseweb="tab-list"] {

    gap: 0.35rem;

    padding: 0.35rem;

    border-radius: 16px;

    background:
        rgba(255,255,255,0.025);
}


button[data-baseweb="tab"] {

    border-radius: 12px;

    padding-left: 1.1rem !important;

    padding-right: 1.1rem !important;
}


div[data-baseweb="tab-highlight"] {

    background-color:
        #34d399;
}


/* ================================
   METRICS
================================ */

[data-testid="stMetric"] {

    padding: 1rem;

    border-radius: 16px;

    background:
        rgba(255,255,255,0.03);

    border:
        1px solid rgba(255,255,255,0.06);
}


/* ================================
   DATAFRAME
================================ */

[data-testid="stDataFrame"] {

    border-radius: 16px;

    overflow: hidden;

    border:
        1px solid rgba(255,255,255,0.07);
}


/* ================================
   CHAT
================================ */

[data-testid="stChatInput"] {

    border:
        1px solid rgba(52,211,153,0.25);
}


/* ================================
   DIVIDERS
================================ */

hr {

    border-color:
        rgba(255,255,255,0.07);
}
/* ================================
   KPI NATIVOS
================================ */

[data-testid="stMetric"] {

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.045),
            rgba(255,255,255,0.015)
        );

    border-radius: 16px;

    padding: 0.5rem 0.3rem;

}


[data-testid="stMetricLabel"] {

    font-size: 0.78rem;

    font-weight: 700;

    letter-spacing: 0.03em;

    color: #94a3b8;

}


[data-testid="stMetricValue"] {

    font-size: 2rem;

    font-weight: 800;

}


[data-testid="stVerticalBlockBorderWrapper"] {

    border-color:
        rgba(255,255,255,0.08) !important;

    border-radius: 20px !important;

    background:
        rgba(255,255,255,0.02);

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
# CARGA DATOS ACCIDENTES
# --------------------------------------------------
@st.cache_data(ttl=21600)
def cargar_accidentes():

    urls = {
        2019: "https://datos.madrid.es/dataset/300228-0-accidentes-trafico-detalle/resource/300228-11-accidentes-trafico-detalle-csv/download/300228-11-accidentes-trafico-detalle-csv.csv",
        2020: "https://datos.madrid.es/dataset/300228-0-accidentes-trafico-detalle/resource/300228-8-accidentes-trafico-detalle-csv/download/300228-8-accidentes-trafico-detalle-csv.csv",
        2021: "https://datos.madrid.es/dataset/300228-0-accidentes-trafico-detalle/resource/300228-33-accidentes-trafico-detalle-csv/download/300228-33-accidentes-trafico-detalle-csv.csv",
        2022: "https://datos.madrid.es/dataset/300228-0-accidentes-trafico-detalle/resource/300228-5-accidentes-trafico-detalle-csv/download/300228-5-accidentes-trafico-detalle-csv.csv",
        2023: "https://datos.madrid.es/dataset/300228-0-accidentes-trafico-detalle/resource/300228-3-accidentes-trafico-detalle-csv/download/300228-3-accidentes-trafico-detalle-csv.csv",
        2024: "https://datos.madrid.es/dataset/300228-0-accidentes-trafico-detalle/resource/300228-2-accidentes-trafico-detalle-csv/download/300228-2-accidentes-trafico-detalle-csv.csv",
        2025: "https://datos.madrid.es/dataset/300228-0-accidentes-trafico-detalle/resource/300228-1-accidentes-trafico-detalle-csv/download/300228-1-accidentes-trafico-detalle-csv.csv",
        2026: "https://datos.madrid.es/dataset/300228-0-accidentes-trafico-detalle/resource/300228-34-accidentes-trafico-detalle/download/300228-34-accidentes-trafico-detalle.csv",
    }

    dataframes = []

    # ----------------------------------------------
    # DESCARGAR CADA AÑO
    # ----------------------------------------------

    for anio, url in urls.items():

        try:

            df_anio = pd.read_csv(
                url,
                sep=";",
                encoding="utf-8"
            )

            df_anio["anio"] = anio

            dataframes.append(df_anio)

        except Exception as error:

            print(
                f"Error cargando accidentes {anio}: {error}"
            )

    # Si no se ha podido cargar ningún año
    if not dataframes:
        return pd.DataFrame()

    # ----------------------------------------------
    # UNIR TODOS LOS AÑOS
    # ----------------------------------------------

    df_accidentes = pd.concat(
        dataframes,
        ignore_index=True
    )

    # ----------------------------------------------
    # FECHA
    # ----------------------------------------------

    df_accidentes["fecha"] = pd.to_datetime(
        df_accidentes["fecha"],
        dayfirst=True,
        errors="coerce"
    )

    # ----------------------------------------------
    # HORA
    # ----------------------------------------------

    df_accidentes["hora_dt"] = pd.to_datetime(
        df_accidentes["hora"],
        format="%H:%M:%S",
        errors="coerce"
    )

    df_accidentes["hora_num"] = (
        df_accidentes["hora_dt"].dt.hour
    )

    # ----------------------------------------------
    # MES
    # ----------------------------------------------

    df_accidentes["mes"] = (
        df_accidentes["fecha"].dt.month
    )

    # ----------------------------------------------
    # LIMPIAR COLUMNAS DE TEXTO
    # ----------------------------------------------

    columnas_texto = [
        "distrito",
        "tipo_accidente",
        "estado_meteorológico",
        "tipo_vehiculo",
        "tipo_persona",
        "rango_edad",
        "sexo",
        "lesividad"
    ]

    for columna in columnas_texto:

        if columna in df_accidentes.columns:

            df_accidentes[columna] = (
                df_accidentes[columna]
                .astype("string")
                .str.strip()
            )

    # ----------------------------------------------
    # COORDENADAS
    # ----------------------------------------------

    df_accidentes["coordenada_x_utm"] = pd.to_numeric(
        df_accidentes["coordenada_x_utm"],
        errors="coerce"
    )

    df_accidentes["coordenada_y_utm"] = pd.to_numeric(
        df_accidentes["coordenada_y_utm"],
        errors="coerce"
    )

    # ----------------------------------------------
    # CONVERTIR COORDENADAS UTM A LATITUD / LONGITUD
    # ----------------------------------------------

    transformer_acc = Transformer.from_crs(
        "EPSG:25830",
        "EPSG:4326",
        always_xy=True
    )

    coords_validas = (
        df_accidentes["coordenada_x_utm"].notna()
        & df_accidentes["coordenada_y_utm"].notna()
    )

    df_accidentes["longitud"] = pd.NA
    df_accidentes["latitud"] = pd.NA

    if coords_validas.any():
        lon, lat = transformer_acc.transform(
            df_accidentes.loc[coords_validas, "coordenada_x_utm"].to_numpy(),
            df_accidentes.loc[coords_validas, "coordenada_y_utm"].to_numpy()
        )
        df_accidentes.loc[coords_validas, "longitud"] = lon
        df_accidentes.loc[coords_validas, "latitud"] = lat

    df_accidentes["longitud"] = pd.to_numeric(df_accidentes["longitud"], errors="coerce")
    df_accidentes["latitud"] = pd.to_numeric(df_accidentes["latitud"], errors="coerce")

    # ----------------------------------------------
    # DEVOLVER DATAFRAME LIMPIO
    # ----------------------------------------------

    return df_accidentes

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

st.html(
    f"""
    <div class="hero">
        <div class="eyebrow">MADRID · LIVE MOBILITY</div>
        <div class="hero-title">Madrid <span>Traffic</span> Explorer</div>
        <div class="hero-subtitle">
            Una mirada en tiempo real al pulso de movilidad de Madrid.
            Explora sensores, detecta puntos críticos y consulta los datos con Inteligencia Artificial.
        </div>
        <div class="update-pill">
            <span class="live-dot"></span>
            LIVE · actualizado {ultima_actualizacion}
        </div>
    </div>
    """
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


# --------------------------------------------------
# RESUMEN AUTOMÁTICO DEL ESTADO DE MADRID
# --------------------------------------------------

porcentaje_fluido = (
    fluido / total * 100
    if total > 0
    else 0
)

if porcentaje_fluido >= 90:
    lectura_estado = "🟢 Madrid circula con normalidad"
elif porcentaje_fluido >= 75:
    lectura_estado = "🟡 Madrid presenta algunas incidencias"
else:
    lectura_estado = "🔴 Madrid presenta tráfico complicado"


st.html(
    f"""
    <div class="status-panel">
        <div class="status-title">{lectura_estado}</div>
        <div class="status-text">
            El <b>{porcentaje_fluido:.1f}%</b> de los puntos presentan tráfico fluido.
            Actualmente hay <b>{retenciones}</b> puntos con retenciones
            y <b>{congestion}</b> con congestión.
        </div>
    </div>
    """
)


# --------------------------------------------------
# TARJETAS KPI
# --------------------------------------------------

cols = st.columns(5)

datos_kpi = [
    ("📍 PUNTOS ACTIVOS", total, "sensores analizados"),
    ("🟢 FLUIDO", fluido, f"{porcentaje_fluido:.1f}% del total"),
    ("🟡 LENTO", lento, "circulación moderada"),
    ("🟠 RETENCIONES", retenciones, "requieren atención"),
    ("🔴 CONGESTIÓN", congestion, "situación crítica")
]

for col, (titulo, valor, nota) in zip(cols, datos_kpi):
    with col:
        st.html(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{titulo}</div>
                <div class="kpi-value">{valor:,}</div>
                <div class="kpi-note">{nota}</div>
            </div>
            """
        )



# --------------------------------------------------
# PESTAÑAS
# --------------------------------------------------

tab_ahora, tab_mapa, tab_accidentes, tab_chat = st.tabs(
    [
        "🚦 Tráfico actual",
        "🗺️ Live Map",
        "🚨 Accidentes",
        "✦ Ask Madrid Traffic Explorer"
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
# BUSCAR PUNTOS RELEVANTES
# --------------------------------------------------

def buscar_puntos_relevantes(pregunta, df, limite=8):
    """
    Busca puntos de tráfico cuya descripción se parezca
    a lo escrito por el usuario.
    """

    descripciones = (
        df["descripcion"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    resultados = process.extract(
        pregunta,
        descripciones,
        scorer=fuzz.WRatio,
        limit=limite
    )

    coincidencias = [
        descripcion
        for descripcion, puntuacion, _ in resultados
        if puntuacion >= 55
    ]

    if not coincidencias:
        return pd.DataFrame()

    return df[
        df["descripcion"].isin(coincidencias)
    ].copy()

# --------------------------------------------------
# TAB ACCIDENTES
# --------------------------------------------------

with tab_accidentes:
    st.markdown('<div class="section-title">🚨 Siniestralidad vial en Madrid</div>', unsafe_allow_html=True)
    st.caption("Datos oficiales de Policía Municipal · 2019–2026 · Actualización mensual")

    with st.spinner("Cargando datos de accidentes..."):
        df_accidentes = cargar_accidentes()

    if df_accidentes.empty:
        st.error("No se han podido cargar los datos de accidentes.")
    else:
        # Una fila por accidente real
        df_siniestros = (
            df_accidentes.sort_values("fecha")
            .drop_duplicates(subset=["num_expediente"])
            .copy()
        )

        # FILTROS
        f1, f2, f3 = st.columns(3)
        anios = sorted(df_siniestros["anio"].dropna().astype(int).unique().tolist(), reverse=True)
        with f1:
            anio = st.selectbox("📅 Año", anios, index=0, key="acc_anio")

        base_anio = df_siniestros[df_siniestros["anio"] == anio].copy()
        distritos = ["Todos"] + sorted(base_anio["distrito"].dropna().astype(str).unique().tolist())
        with f2:
            distrito = st.selectbox("📍 Distrito", distritos, index=0, key="acc_distrito")

        base_distrito = base_anio.copy()
        if distrito != "Todos":
            base_distrito = base_distrito[base_distrito["distrito"] == distrito].copy()

        tipos = ["Todos"] + sorted(base_distrito["tipo_accidente"].dropna().astype(str).unique().tolist())
        with f3:
            tipo = st.selectbox("🚗 Tipo de accidente", tipos, index=0, key="acc_tipo")

        df_filtrado = base_distrito.copy()
        if tipo != "Todos":
            df_filtrado = df_filtrado[df_filtrado["tipo_accidente"] == tipo].copy()

        expedientes = set(df_filtrado["num_expediente"].dropna().astype(str))
        df_personas_filtrado = df_accidentes[df_accidentes["num_expediente"].astype(str).isin(expedientes)].copy()

        st.divider()

        # KPIs
        total_accidentes = df_filtrado["num_expediente"].nunique()
        conteo_distritos = df_filtrado["distrito"].value_counts()
        distrito_top = conteo_distritos.index[0] if not conteo_distritos.empty else "—"
        conteo_tipos = df_filtrado["tipo_accidente"].value_counts()
        tipo_top = conteo_tipos.index[0] if not conteo_tipos.empty else "—"
        conteo_horas = df_filtrado["hora_num"].dropna().astype(int).value_counts()
        if not conteo_horas.empty:
            h = int(conteo_horas.index[0])
            hora_punta = f"{h:02d}:00–{(h + 1) % 24:02d}:00"
        else:
            hora_punta = "—"

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🚨 Accidentes", f"{total_accidentes:,}")
        k2.metric("👥 Personas implicadas", f"{len(df_personas_filtrado):,}")
        k3.metric("📍 Distrito destacado", distrito_top)
        k4.metric("🕐 Hora con más accidentes", hora_punta)
        st.caption(f"Tipo de accidente más frecuente en la selección: **{tipo_top}**")

        st.divider()
        st.markdown('<div class="section-title">🗺️ Dónde ocurren los accidentes</div>', unsafe_allow_html=True)
        col_mapa, col_insights = st.columns([3.2, 1])
        df_mapa_acc = df_filtrado.dropna(subset=["latitud", "longitud"]).copy()
        df_mapa_acc = df_mapa_acc[
            df_mapa_acc["latitud"].between(40.2, 40.65)
            & df_mapa_acc["longitud"].between(-4.05, -3.45)
        ].copy()

        with col_mapa:
            if df_mapa_acc.empty:
                st.info("No hay coordenadas disponibles para esta selección.")
            else:
                fig_acc_mapa = px.scatter_map(
                    df_mapa_acc, lat="latitud", lon="longitud", hover_name="localizacion",
                    hover_data={"fecha": True, "hora": True, "distrito": True, "tipo_accidente": True, "latitud": False, "longitud": False},
                    zoom=10, height=560
                )
                fig_acc_mapa.update_traces(marker={"size": 7, "opacity": 0.65})
                fig_acc_mapa.update_layout(
                    map_style="open-street-map", map_center={"lat": 40.4168, "lon": -3.7038},
                    margin=dict(l=0, r=0, t=0, b=0), showlegend=False
                )
                st.plotly_chart(fig_acc_mapa, use_container_width=True)

        with col_insights:
            st.markdown("#### ⚠️ Insights")
            if total_accidentes == 0:
                st.info("No hay accidentes para los filtros seleccionados.")
            else:
                dias = df_filtrado["fecha"].dt.day_name().value_counts()
                dia_top = dias.index[0] if not dias.empty else "—"
                traduccion = {"Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles","Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"}
                dia_top = traduccion.get(dia_top, dia_top)
                st.metric("📍 Distrito", distrito_top)
                st.metric("🕐 Franja punta", hora_punta)
                st.metric("📅 Día más frecuente", dia_top)
                st.metric("🚗 Tipología", tipo_top)

        st.divider()
        st.markdown('<div class="section-title">🕐 Cuándo ocurren</div>', unsafe_allow_html=True)
        accidentes_hora = (
            df_filtrado.dropna(subset=["hora_num"])
            .groupby("hora_num")["num_expediente"].nunique()
            .reindex(range(24), fill_value=0).reset_index()
        )
        accidentes_hora.columns = ["Hora", "Accidentes"]
        fig_horas = px.bar(accidentes_hora, x="Hora", y="Accidentes", text="Accidentes")
        fig_horas.update_layout(height=380, xaxis=dict(tickmode="linear", dtick=1, title="Hora del día"), yaxis_title="Accidentes", showlegend=False, margin=dict(l=10,r=10,t=20,b=10))
        fig_horas.update_traces(textposition="outside")
        st.plotly_chart(fig_horas, use_container_width=True)

        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="section-title">📈 Evolución mensual</div>', unsafe_allow_html=True)
            meses = (
                df_filtrado.dropna(subset=["mes"])
                .groupby("mes")["num_expediente"].nunique()
                .reindex(range(1,13), fill_value=0).reset_index()
            )
            meses.columns = ["Mes", "Accidentes"]
            nombres = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
            meses["Mes_nombre"] = meses["Mes"].map(nombres)
            fig_meses = px.line(meses, x="Mes_nombre", y="Accidentes", markers=True)
            fig_meses.update_layout(height=390, xaxis_title="", yaxis_title="Accidentes", margin=dict(l=10,r=10,t=20,b=10))
            st.plotly_chart(fig_meses, use_container_width=True)

        with g2:
            st.markdown('<div class="section-title">🚗 Tipos de accidente</div>', unsafe_allow_html=True)
            tipos_acc = df_filtrado["tipo_accidente"].value_counts().head(8).sort_values().reset_index()
            tipos_acc.columns = ["Tipo", "Accidentes"]
            fig_tipos = px.bar(tipos_acc, x="Accidentes", y="Tipo", orientation="h", text="Accidentes")
            fig_tipos.update_layout(height=390, xaxis_title="Accidentes", yaxis_title="", showlegend=False, margin=dict(l=10,r=10,t=20,b=10))
            fig_tipos.update_traces(textposition="outside")
            st.plotly_chart(fig_tipos, use_container_width=True)

        st.caption(
            "Cada accidente se cuenta una sola vez mediante num_expediente. "
            "El indicador de personas implicadas utiliza el dataset detallado."
        )


# --------------------------------------------------
# TAB CHAT
# --------------------------------------------------

# --------------------------------------------------
# TAB CHAT
# --------------------------------------------------

with tab_chat:

    st.markdown(
        '<div class="section-title">✦ Ask Madrid Traffic Explorer</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Pregunta sobre el tráfico actual o la siniestralidad vial de Madrid."
    )

    # --------------------------------------------------
    # CARGAR ACCIDENTES PARA EL CHAT
    # --------------------------------------------------

    if "df_accidentes" not in locals():
        df_accidentes = cargar_accidentes()

    # --------------------------------------------------
    # HISTORIAL DE CONVERSACIÓN
    # --------------------------------------------------

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    for mensaje in st.session_state.mensajes:

        with st.chat_message(
            mensaje["rol"]
        ):
            st.markdown(
                mensaje["contenido"]
            )

    # --------------------------------------------------
    # INPUT
    # --------------------------------------------------

    pregunta = st.chat_input(
        "Ejemplo: ¿Qué distrito tuvo más accidentes en 2025?"
    )

    if pregunta:

        st.session_state.mensajes.append(
            {
                "rol": "user",
                "contenido": pregunta
            }
        )

        with st.chat_message("user"):
            st.markdown(pregunta)

        # --------------------------------------------------
        # DETECTAR TIPO DE PREGUNTA
        # --------------------------------------------------

        pregunta_lower = pregunta.lower()

        palabras_accidentes = [
            "accidente",
            "accidentes",
            "siniestro",
            "siniestros",
            "atropello",
            "atropellos",
            "colisión",
            "colisiones",
            "choque",
            "choques",
            "lesividad",
            "herido",
            "heridos",
            "víctima",
            "víctimas",
            "alcohol",
            "droga",
            "drogas",
            "peatón",
            "peatones"
        ]

        palabras_trafico = [
            "tráfico",
            "trafico",
            "congestión",
            "congestion",
            "retención",
            "retenciones",
            "fluido",
            "lento",
            "saturación",
            "saturacion",
            "ocupación",
            "ocupacion",
            "intensidad",
            "vehículos por hora"
        ]

        pregunta_accidentes = any(
            palabra in pregunta_lower
            for palabra in palabras_accidentes
        )

        pregunta_trafico = any(
            palabra in pregunta_lower
            for palabra in palabras_trafico
        )

        # --------------------------------------------------
        # CONTEXTO DE TRÁFICO
        # --------------------------------------------------

        contexto_trafico = ""

        if pregunta_trafico or not pregunta_accidentes:

            total_puntos = len(
                df_actual
            )

            conteo_estados = (
                df_actual[
                    "estado_trafico"
                ]
                .value_counts()
                .to_dict()
            )

            top_congestion = (
                df_actual[
                    df_actual[
                        "estado_trafico"
                    ].isin(
                        [
                            "Retenciones",
                            "Congestión"
                        ]
                    )
                ]
                .sort_values(
                    "carga",
                    ascending=False
                )
                .head(10)[
                    [
                        "descripcion",
                        "estado_trafico",
                        "intensidad",
                        "ocupacion",
                        "carga"
                    ]
                ]
            )

            puntos_relevantes = (
                buscar_puntos_relevantes(
                    pregunta,
                    df_actual
                )
            )

            if not puntos_relevantes.empty:

                contexto_puntos = (
                    puntos_relevantes[
                        [
                            "descripcion",
                            "estado_trafico",
                            "intensidad",
                            "ocupacion",
                            "carga"
                        ]
                    ]
                    .to_string(
                        index=False
                    )
                )

            else:

                contexto_puntos = (
                    "No se encontraron "
                    "puntos claramente relacionados."
                )

            contexto_trafico = f"""
DATOS DE TRÁFICO EN TIEMPO REAL

Última actualización:
{ultima_actualizacion}

Puntos analizados:
{total_puntos}

Distribución del tráfico:
{conteo_estados}

PUNTOS RELACIONADOS CON LA PREGUNTA:
{contexto_puntos}

PUNTOS CON MAYOR SATURACIÓN:
{top_congestion.to_string(index=False)}
"""

        # --------------------------------------------------
        # CONTEXTO DE ACCIDENTES
        # --------------------------------------------------

        contexto_accidentes = ""

        if pregunta_accidentes:

            # ----------------------------------------------
            # DETECTAR AÑO
            # ----------------------------------------------

            anios_disponibles = sorted(
                df_accidentes[
                    "anio"
                ]
                .dropna()
                .astype(int)
                .unique()
                .tolist()
            )

            anio_pregunta = None

            for anio_posible in anios_disponibles:

                if str(
                    anio_posible
                ) in pregunta_lower:

                    anio_pregunta = (
                        anio_posible
                    )

                    break

            # Si no especifica año,
            # usamos el más reciente
            if anio_pregunta is None:

                anio_pregunta = max(
                    anios_disponibles
                )

            df_acc_chat = (
                df_accidentes[
                    df_accidentes[
                        "anio"
                    ] == anio_pregunta
                ]
                .copy()
            )

            # ----------------------------------------------
            # UNA FILA POR ACCIDENTE
            # ----------------------------------------------

            df_siniestros_chat = (
                df_acc_chat
                .sort_values("fecha")
                .drop_duplicates(
                    subset=[
                        "num_expediente"
                    ]
                )
                .copy()
            )

            total_accidentes_chat = (
                df_siniestros_chat[
                    "num_expediente"
                ]
                .nunique()
            )

            # ----------------------------------------------
            # DISTRITOS
            # ----------------------------------------------

            accidentes_distrito = (
                df_siniestros_chat[
                    "distrito"
                ]
                .value_counts()
                .head(10)
            )

            # ----------------------------------------------
            # TIPOS
            # ----------------------------------------------

            accidentes_tipo = (
                df_siniestros_chat[
                    "tipo_accidente"
                ]
                .value_counts()
                .head(10)
            )

            # ----------------------------------------------
            # HORAS
            # ----------------------------------------------

            accidentes_hora = (
                df_siniestros_chat[
                    "hora_num"
                ]
                .dropna()
                .astype(int)
                .value_counts()
                .sort_values(
                    ascending=False
                )
                .head(10)
            )

            # ----------------------------------------------
            # PERSONAS IMPLICADAS
            # ----------------------------------------------

            personas_implicadas = len(
                df_acc_chat
            )

            # ----------------------------------------------
            # ALCOHOL
            # ----------------------------------------------

            alcohol = (
                df_acc_chat[
                    "positiva_alcohol"
                ]
                .value_counts(
                    dropna=False
                )
                .head(10)
                .to_dict()
            )

            # ----------------------------------------------
            # DROGAS
            # ----------------------------------------------

            drogas = (
                df_acc_chat[
                    "positiva_droga"
                ]
                .value_counts(
                    dropna=False
                )
                .head(10)
                .to_dict()
            )

            contexto_accidentes = f"""
DATOS DE SINIESTRALIDAD VIAL DE MADRID

Año analizado:
{anio_pregunta}

Número de accidentes únicos:
{total_accidentes_chat}

Número de registros de personas implicadas:
{personas_implicadas}

ACCIDENTES POR DISTRITO:
{accidentes_distrito.to_string()}

TIPOS DE ACCIDENTE MÁS FRECUENTES:
{accidentes_tipo.to_string()}

HORAS CON MÁS ACCIDENTES:
{accidentes_hora.to_string()}

RESULTADOS DE ALCOHOL:
{alcohol}

RESULTADOS DE DROGAS:
{drogas}

IMPORTANTE:
Cada accidente puede aparecer varias veces
en el dataset porque existe una fila por persona
implicada.

Para contar accidentes se utiliza siempre
num_expediente como identificador único.
"""

        # --------------------------------------------------
        # CONTEXTO FINAL
        # --------------------------------------------------

        contexto_final = f"""
{contexto_trafico}

{contexto_accidentes}
"""

        # --------------------------------------------------
        # CONSULTAR OLLAMA
        # --------------------------------------------------

        try:

            with st.spinner(
                "Analizando los datos de Madrid..."
            ):

                respuesta_ollama = (
                    ollama.chat(
                        model="llama3.2:3b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Eres Ask Madrid Traffic Explorer, "
                                    "un asistente especializado en movilidad "
                                    "y siniestralidad vial de Madrid. "

                                    "Puedes responder preguntas sobre dos "
                                    "fuentes de datos: tráfico en tiempo real "
                                    "y accidentes de tráfico registrados por "
                                    "la Policía Municipal. "

                                    "Utiliza EXCLUSIVAMENTE los datos "
                                    "proporcionados en el contexto. "

                                    "No inventes cifras, calles, accidentes, "
                                    "causas o explicaciones que no estén "
                                    "respaldadas por los datos. "

                                    "Si la información disponible no permite "
                                    "responder, indícalo claramente. "

                                    "Para los datos de accidentes, recuerda "
                                    "que num_expediente identifica un accidente "
                                    "único y que pueden existir varias filas "
                                    "para un mismo accidente porque cada fila "
                                    "puede representar una persona implicada. "

                                    "No confundas número de registros con "
                                    "número de accidentes. "

                                    "Cuando hables de tráfico, intensidad "
                                    "representa vehículos por hora, ocupación "
                                    "el porcentaje de ocupación de la vía y "
                                    "carga el nivel de saturación. "

                                    "Responde siempre en español, de forma "
                                    "clara, breve y útil para un usuario "
                                    "no técnico."
                                )
                            },
                            {
                                "role": "user",
                                "content": f"""
CONTEXTO REAL DE MADRID:

{contexto_final}

PREGUNTA:

{pregunta}
"""
                            }
                        ]
                    )
                )

            respuesta = (
                respuesta_ollama[
                    "message"
                ][
                    "content"
                ]
            )

        except Exception as e:

            respuesta = (
                "⚠️ No he podido conectar "
                "con el modelo de IA. "
                f"Error: {e}"
            )

        # --------------------------------------------------
        # MOSTRAR RESPUESTA
        # --------------------------------------------------

        st.session_state.mensajes.append(
            {
                "rol": "assistant",
                "contenido": respuesta
            }
        )

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                respuesta
            )