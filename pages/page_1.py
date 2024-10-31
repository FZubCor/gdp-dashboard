import streamlit as st
import pandas as pd
import pydeck as pdk

# Mostrar título y agregar la imagen al encabezado
st.title("Visualización general de recorrido migratorio de aves")

col1, col2, col3 = st.columns([1, 3, 1])  # Crear columnas para centrar la imagen
with col2:
    st.image("images/img_1.webp", caption="Recorrido Migratorio de Aves", width=600)


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
    
    return data

data = load_data()
st.dataframe(data.head(5).reset_index(drop=True))

# Obtener el rango de fechas del archivo
min_date = data["date_time"].min()
max_date = data["date_time"].max()

# Selección del nombre del ave
bird_names = data['bird_name'].unique()
selected_bird = st.selectbox("Selecciona el nombre del ave", bird_names)

# Filtro de fechas con el rango acotado y conversión a datetime con zona horaria UTC
start_date, end_date = st.date_input(
    "Selecciona el rango de fechas",
    [min_date.date(), max_date.date()],
    min_value=min_date.date(),
    max_value=max_date.date()
)
# Convertir las fechas seleccionadas a formato datetime con zona horaria UTC
start_date = pd.to_datetime(start_date).tz_localize("UTC")
end_date = pd.to_datetime(end_date).tz_localize("UTC")

# Filtrar los datos por ave y fechas seleccionadas, y ordenar por fecha
filtered_data = data[(data['bird_name'] == selected_bird) & 
                     (data['date_time'] >= start_date) & 
                     (data['date_time'] <= end_date)].sort_values(by="date_time")

# Crear una lista de coordenadas para trazar la línea
line_data = filtered_data[["longitude", "latitude"]].values.tolist()

# Selección de visualización: puntos o líneas
view_option = st.radio("Selecciona la visualización en el mapa:", ("Puntos", "Líneas"))

# Capa de la línea de recorrido con efecto neón
line_layer = pdk.Layer(
    "PathLayer",
    data=pd.DataFrame({"path": [line_data]}),  # Crear una sola línea con todos los puntos
    get_path="path",
    get_color=[57, 255, 20],  # Color verde neón
    width_scale=10,
    width_min_pixels=3,
)

# Capa para los puntos de ubicación
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_data,
    get_position=["longitude", "latitude"],
    get_color=[0, 255, 255],   # Color cian para puntos de ubicación
    get_radius=1500,
)

# Configurar la capa según la selección del usuario
if view_option == "Puntos":
    layers = [scatter_layer]
else:
    layers = [line_layer]

# Configuración de la vista inicial del mapa
initial_view_state = pdk.ViewState(
    latitude=filtered_data['latitude'].mean(),
    longitude=filtered_data['longitude'].mean(),
    zoom=4,
    pitch=30,
)

# Renderizar el mapa con el basemap de satélite y la capa seleccionada
r = pdk.Deck(
    layers=layers,
    initial_view_state=initial_view_state,
    map_style="mapbox://styles/mapbox/satellite-v9",  # Basemap de satélite
)

st.pydeck_chart(r)

# Calcular la velocidad promedio de vuelo y la altura promedio
average_speed = filtered_data['speed_2d'].mean()
average_altitude = filtered_data['altitude'].mean()

# Mostrar velocidad promedio y altura promedio como métricas
st.subheader("Estadísticas de Vuelo")
col1, col2 = st.columns(2)
col1.metric("Velocidad Promedio de Vuelo", f"{average_speed:.2f} m/s")
col2.metric("Altura Promedio", f"{average_altitude:.2f} m")
