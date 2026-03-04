import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración de la página
st.set_page_config(
    page_title="🍕 Pizzerías en España",
    page_icon="🍕",
    layout="wide"
)

# Título
st.title("🍕 Análisis de Pizzerías en España")
st.markdown("---")

# Cargar datos
@st.cache_data
def cargar_datos():
    # Obtener la ruta base del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construir rutas absolutas
    csv_path = os.path.join(base_dir, "data/processed/analisis_pizzerias_municipios_final.csv")
    gpkg_path = os.path.join(base_dir, "data/processed/pizzerias_con_municipio.gpkg")
    
    # Cargar archivos
    analisis = pd.read_csv(csv_path)
    pizzerias = gpd.read_file(gpkg_path)
    
    return analisis, pizzerias

with st.spinner("Cargando datos... 🍕"):
    analisis, pizzerias = cargar_datos()

# Sidebar con filtros
st.sidebar.header("🎛️ Filtros")

# Selector de provincia
provincias = sorted([p for p in analisis['PROVINCIA'].dropna().unique() if pd.notna(p)])
provincia_sel = st.sidebar.selectbox(
    "Selecciona provincia:",
    ["Todas"] + provincias
)

# Filtro de población mínima
pob_min = st.sidebar.slider(
    "Población mínima:",
    min_value=0,
    max_value=int(analisis['POB25'].max()),
    value=0,
    step=1000
)

# Aplicar filtros
if provincia_sel != "Todas":
    analisis_filt = analisis[
        (analisis['PROVINCIA'] == provincia_sel) &
        (analisis['POB25'] >= pob_min)
    ]
else:
    analisis_filt = analisis[analisis['POB25'] >= pob_min]

# MÉTRICAS PRINCIPALES
st.header("📊 Métricas clave")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total pizzerías",
        f"{int(analisis_filt['num_pizzerias'].sum()):,}"
    )

with col2:
    st.metric(
        "Municipios con pizzerías",
        f"{len(analisis_filt):,}"
    )

with col3:
    media_pob = analisis_filt['POB25'].mean()
    st.metric(
        "Población media",
        f"{int(media_pob):,}"
    )

with col4:
    ratio_medio = analisis_filt['pizzerias_100k_hab'].mean()
    st.metric(
        "Ratio medio (piz/100k hab)",
        f"{ratio_medio:.1f}"
    )

st.markdown("---")

# MAPA Y TOP 10
col_mapa, col_top = st.columns([2, 1])

with col_mapa:
    st.subheader("🗺️ Mapa de pizzerías")
    
    # Filtrar pizzerías por provincia
    if provincia_sel != "Todas":
        pizzerias_filt = pizzerias[pizzerias['PROVINCIA'] == provincia_sel]
    else:
        pizzerias_filt = pizzerias
    
    # Crear mapa base
    m = folium.Map(location=[40.4165, -3.7026], zoom_start=6, tiles='CartoDB positron')
    
    # Añadir puntos (samplear si hay muchos)
    max_puntos = 1000
    if len(pizzerias_filt) > max_puntos:
        pizzerias_sample = pizzerias_filt.sample(max_puntos)
        st.caption(f"Mostrando {max_puntos} pizzerías (muestra aleatoria)")
    else:
        pizzerias_sample = pizzerias_filt
    
    for _, row in pizzerias_sample.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=2,
            color='red',
            fill=True,
            fillOpacity=0.6,
            popup=row['name'] if pd.notna(row['name']) else 'Sin nombre'
        ).add_to(m)
    
    # Mostrar mapa
    st_folium(m, width=700, height=500)

with col_top:
    st.subheader("🏆 Top 10 municipios")
    
    top10 = analisis_filt.nlargest(10, 'num_pizzerias')[
        ['NAMEUNIT', 'num_pizzerias', 'pizzerias_100k_hab', 'POB25']
    ].copy()
    
    top10.columns = ['Municipio', 'Pizzerías', 'Ratio/100k', 'Población']
    
    st.dataframe(
        top10,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Pizzerías": st.column_config.NumberColumn(format="%d"),
            "Población": st.column_config.NumberColumn(format="%d"),
            "Ratio/100k": st.column_config.NumberColumn(format="%.1f")
        }
    )

st.markdown("---")

# GRÁFICOS ADICIONALES
st.header("📈 Análisis detallado")

col_scatter, col_hist = st.columns(2)

with col_scatter:
    st.subheader("Población vs Pizzerías")
    
    # Scatter plot SIN línea de tendencia
    fig = px.scatter(
        analisis_filt,
        x='POB25',
        y='num_pizzerias',
        hover_data=['NAMEUNIT', 'PROVINCIA'],
        labels={'POB25': 'Población', 'num_pizzerias': 'Número de pizzerías'},
        opacity=0.6
        # 👈 Sin trendline
    )
    
    fig.update_layout(
        xaxis_type="log",
        yaxis_type="log",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col_hist:
    st.subheader("Distribución del ratio")
    
    fig = px.histogram(
        analisis_filt,
        x='pizzerias_100k_hab',
        nbins=50,
        labels={'pizzerias_100k_hab': 'Pizzerías por 100k habitantes'},
        marginal='box',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# TABLA COMPLETA
st.markdown("---")
st.header("📋 Datos completos")

st.dataframe(
    analisis_filt[['NAMEUNIT', 'PROVINCIA', 'num_pizzerias', 'POB25', 'pizzerias_100k_hab']],
    hide_index=True,
    use_container_width=True,
    column_config={
        "NAMEUNIT": "Municipio",
        "PROVINCIA": "Provincia",
        "num_pizzerias": "Pizzerías",
        "POB25": "Población 2025",
        "pizzerias_100k_hab": "Ratio/100k hab"
    }
)

# Footer
st.markdown("---")
st.caption("🍕 Fuentes: OpenStreetMap · INE · CNIG | Dashboard interactivo de pizzerías en España")