import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.title("Análisis migratorio")
st.text("La información fue tomada de: https://www.kaggle.com/datasets/saikrishna20/bird-tracking/data")
st.text("""La información tiene el recorrido migratorio de 3 aves a las cuales se les instaló un dispositivo GPS, de la información suministrada 
 por los equipos se encuentra la siguiente información:""")

# Cargar los datos usando st.cache_data para la nueva forma de cacheo
@st.cache_data
def load_data():
    data = pd.read_csv("data/bird_tracking.csv", parse_dates=["date_time"])
    
    # Verificar que latitude y longitude estén en formato decimal
    data["latitude"] = pd.to_numeric(data["latitude"], errors="coerce")
    data["longitude"] = pd.to_numeric(data["longitude"], errors="coerce")
    
    # Filtrar filas con valores inválidos en latitude o longitude
    data = data.dropna(subset=["latitude", "longitude"])
    
    # Eliminar la zona horaria de 'date_time' para evitar errores de comparación
    data['date_time'] = data['date_time'].dt.tz_localize(None)
    
    return data

data = load_data()

# Filtros de fecha y ave
min_date = data["date_time"].min()
max_date = data["date_time"].max()
bird_names = data['bird_name'].unique()

selected_bird = st.selectbox("Selecciona el nombre del ave", bird_names)
start_date, end_date = st.date_input(
    "Selecciona el rango de fechas",
    [min_date.date(), max_date.date()],
    min_value=min_date.date(),
    max_value=max_date.date()
)

# Convertir fechas seleccionadas a formato datetime sin zona horaria
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filtrar datos por ave y rango de fechas seleccionado
filtered_data = data[
    (data['bird_name'] == selected_bird) & 
    (data['date_time'] >= start_date) & 
    (data['date_time'] <= end_date)
]

# Configurar los colores del mapa de calor en tonos de azul
color_range = [
    [65, 105, 225],  # Azul claro
    [30, 144, 255],  # Azul medio
    [0, 191, 255],   # Azul brillante
    [0, 255, 127],   # Verde
    [255, 215, 0],   # Amarillo
    [255, 69, 0],    # Naranja
    [255, 0, 0]      # Rojo intenso
]

# Mapa de calor para las zonas más frecuentes
heatmap_layer = pdk.Layer(
    "HeatmapLayer",
    data=filtered_data,
    get_position=["longitude", "latitude"],
    opacity=0.6,
    color_range=color_range,
    aggregation="mean",
    get_weight=1,
)

# Configuración de la vista inicial del mapa
initial_view_state = pdk.ViewState(
    latitude=filtered_data['latitude'].mean(),
    longitude=filtered_data['longitude'].mean(),
    zoom=4,
    pitch=0,
)

# Renderizar el mapa con el mapa de calor
st.pydeck_chart(pdk.Deck(
    layers=[heatmap_layer],
    initial_view_state=initial_view_state,
    map_style="mapbox://styles/mapbox/satellite-v9",
))

# Gráfico de barras de velocidad promedio por ave
avg_speed = data.groupby("bird_name")["speed_2d"].mean().reset_index()
fig_speed = px.bar(avg_speed, x="bird_name", y="speed_2d", title="Velocidad Promedio de Vuelo por Ave")
fig_speed.update_layout(xaxis_title="Ave", yaxis_title="Velocidad Promedio (m/s)")
st.plotly_chart(fig_speed)

# Gráfico de líneas del perfil de elevación por ave
fig_altitude = px.line(data, x="date_time", y="altitude", color="bird_name", title="Perfil de Elevación por Altura de Vuelo")
fig_altitude.update_layout(xaxis_title="Fecha y Hora", yaxis_title="Altitud (m)")
st.plotly_chart(fig_altitude)
