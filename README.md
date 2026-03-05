# 🍕 Análisis de Pizzerías en España

Dashboard interactivo para explorar la distribución de pizzerías en España, su relación con la población y análisis por municipios.

## 📊 Datos clave
- **33,046** pizzerías geolocalizadas
- **8,132** municipios con datos de población (2025)
- **Correlación población-pizzerías: 0.974**

## ✨ Características
- 🗺️ Mapa interactivo con MarkerCluster y HeatMap
- 🔍 Filtros por provincia y cadena (ej: Telepizza, Domino's)
- 📈 Top 10 municipios con más pizzerías
- 📊 Gráficos de análisis (población vs pizzerías)
- 📋 Tabla completa de datos

## 🛠️ Tecnologías utilizadas
- **Python**: Procesamiento de datos
- **Streamlit**: Dashboard interactivo
- **GeoPandas**: Análisis espacial
- **Folium**: Mapas interactivos
- **Plotly**: Gráficos dinámicos
- **OpenStreetMap**: Datos de pizzerías
- **INE**: Datos de población
- **CNIG**: Límites municipales

## 🚀 Demo en vivo
[https://pizzerias-spain.streamlit.app](https://pizzerias-spain.streamlit.app)

## 📁 Estructura del proyecto
pizzerias/
├── spain/
│ ├── dashboard.py # Aplicación Streamlit
│ ├── requirements.txt # Dependencias
│ ├── data/
│ │ ├── raw/ # Datos originales
│ │ └── processed/ # Datos limpios
│ ├── notebooks/ # Análisis exploratorio
│ └── outputs/ # Mapas y gráficos
└── README.md


## 📄 Licencia
MIT
