import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, HeatMap
import plotly.express as px
import os

# Configuración de la página
st.set_page_config(page_title="🍕 Pizzerías en España", page_icon="🍕", layout="wide")

st.title("🍕 Análisis de Pizzerías en España")
st.markdown("---")

# Cargar datos
@st.cache_data
def cargar_datos():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "data/processed/analisis_pizzerias_municipios_final.csv")
    gpkg_path = os.path.join(base_dir, "data/processed/pizzerias_con_municipio.gpkg")
    
    # Cargar archivos
    analisis = pd.read_csv(csv_path)
    pizzerias = gpd.read_file(gpkg_path)
    
    # 🔥 FIX: Añadir columna PROVINCIA a pizzerias usando NAMEUNIT
    provincia_por_municipio = analisis.set_index('NAMEUNIT')['PROVINCIA'].to_dict()
    pizzerias['PROVINCIA'] = pizzerias['NAMEUNIT'].map(provincia_por_municipio)
    
    # Mostrar columnas para debug (opcional, puedes comentarlo después)
    # st.write("Columnas en pizzerias:", pizzerias.columns.tolist())
    
    return analisis, pizzerias

with st.spinner("Cargando datos... 🍕"):
    analisis, pizzerias = cargar_datos()

# Sidebar con filtros
st.sidebar.header("🎛️ Filtros")
provincias = sorted([p for p in analisis['PROVINCIA'].dropna().unique() if pd.notna(p)])
provincia_sel = st.sidebar.selectbox("Selecciona provincia:", ["Todas"] + provincias)

pob_min = st.sidebar.slider(
    "Población mínima:",
    min_value=0,
    max_value=int(analisis['POB25'].max()),
    value=0,
    step=1000
)

st.sidebar.header("🔍 Filtro por cadena")
buscar_cadena = st.sidebar.text_input("Buscar cadena (ej: Telepizza):")

# --- Aplicar filtros ---
# Datos municipales
if provincia_sel != "Todas":
    analisis_filt = analisis[(analisis['PROVINCIA'] == provincia_sel) & (analisis['POB25'] >= pob_min)]
else:
    analisis_filt = analisis[analisis['POB25'] >= pob_min]

# Datos de pizzerías (AHORA SÍ FUNCIONA)
if provincia_sel != "Todas":
    pizzerias_filt = pizzerias[pizzerias['PROVINCIA'] == provincia_sel]
else:
    pizzerias_filt = pizzerias.copy()

# Filtro por cadena
if buscar_cadena:
    pizzerias_filt = pizzerias_filt[pizzerias_filt['name'].str.contains(buscar_cadena, case=False, na=False)]

# --- Métricas clave ---
st.header("📊 Métricas clave")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total pizzerías", f"{len(pizzerias_filt):,}")
with col2:
    st.metric("Municipios con pizzerías", f"{len(analisis_filt):,}")
with col3:
    media_pob = analisis_filt['POB25'].mean()
    st.metric("Población media", f"{int(media_pob):,}")
with col4:
    ratio_medio = analisis_filt['pizzerias_100k_hab'].mean()
    st.metric("Ratio medio (piz/100k hab)", f"{ratio_medio:.1f}")
st.markdown("---")

# --- Mapa y Top 10 ---
col_mapa, col_top = st.columns([2, 1])

with col_mapa:
    st.subheader("🗺️ Mapa de pizzerías")

    if pizzerias_filt.empty:
        st.warning("No hay pizzerías que cumplan los filtros seleccionados.")
    else:
        # Crear mapa base
        m = folium.Map(location=[40.4165, -3.7026], zoom_start=6, tiles='CartoDB positron')

        # Preparar datos para heatmap
        heat_data = [[row.geometry.y, row.geometry.x] for _, row in pizzerias_filt.iterrows() if pd.notna(row.geometry.y) and pd.notna(row.geometry.x)]
        
        # Siempre añadimos heatmap
        if heat_data:
            HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)

        # Decidir si añadir marcadores según cantidad
        num_puntos = len(pizzerias_filt)
        if num_puntos > 2000:
            st.caption(f"⚠️ Mostrando solo mapa de calor ({num_puntos} pizzerías). Demasiados puntos para marcadores individuales.")
        else:
            st.caption(f"📍 Mostrando {num_puntos} pizzerías (marcadores agrupados + mapa de calor)")
            marker_cluster = MarkerCluster().add_to(m)
            for _, row in pizzerias_filt.iterrows():
                if pd.notna(row.geometry.y) and pd.notna(row.geometry.x):
                    folium.Marker(
                        location=[row.geometry.y, row.geometry.x],
                        popup=row['name'] if pd.notna(row['name']) else 'Sin nombre',
                        tooltip=row['name'] if pd.notna(row['name']) else 'Sin nombre',
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(marker_cluster)

        # Mostrar mapa
        st_folium(m, width=700, height=500, key="mapa_principal")

with col_top:
    st.subheader("🏆 Top 10 municipios")
    if not analisis_filt.empty:
        top10 = analisis_filt.nlargest(10, 'num_pizzerias')[['NAMEUNIT', 'num_pizzerias', 'pizzerias_100k_hab', 'POB25']].copy()
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
    else:
        st.info("No hay datos para mostrar")

st.markdown("---")

# --- Gráficos adicionales ---
if not analisis_filt.empty:
    st.header("📈 Análisis detallado")
    col_scatter, col_hist = st.columns(2)

    with col_scatter:
        st.subheader("Población vs Pizzerías")
        fig = px.scatter(
            analisis_filt,
            x='POB25',
            y='num_pizzerias',
            hover_data=['NAMEUNIT', 'PROVINCIA'],
            labels={'POB25': 'Población', 'num_pizzerias': 'Número de pizzerías'},
            opacity=0.6
        )
        fig.update_layout(xaxis_type="log", yaxis_type="log", height=400)
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

st.markdown("---")
st.caption("🍕 Fuentes: OpenStreetMap · INE · CNIG | Dashboard interactivo de pizzerías en España")