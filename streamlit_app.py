import streamlit as st
from st_pages import add_page_title, get_nav_from_toml

st.set_page_config(
    page_title="App_aves",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/library/api-reference/utilities/st.set_page_config',
        'Report a bug': "https://docs.streamlit.io/library/api-reference/utilities/st.set_page_config",
        'About': """
            # App de Seguimiento de Aves Migratorias
            ---
            
            **Realizado por:**  
            Álvaro Ronderos  
            Johan Matiz  
            Fernando Zubieta
            
            ---
            
            Esta aplicación permite visualizar y analizar los recorridos migratorios de aves mediante datos de GPS.  
            Puedes navegar entre distintas secciones para obtener una visión completa del análisis migratorio.
        """
    }
)
st.sidebar.markdown("## Menú de Navegación")

nav = get_nav_from_toml(".streamlit/pages_sections.toml")
pg = st.navigation(nav)

pg.run()