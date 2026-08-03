from pathlib import Path
import streamlit as st

from componentes.estilos import aplicar_estilos
from servicios.almacenamiento import inicializar_datos

st.set_page_config(
    page_title="Seguimiento de Robótica",
    page_icon="🤖",
    layout="wide",
)

aplicar_estilos()
inicializar_datos()

PAGINAS = [
    st.Page("paginas/inicio.py", title="Inicio", icon="🏠", default=True),
    st.Page("paginas/tareas.py", title="Tareas actuales", icon="🧩"),
    st.Page("paginas/integrantes.py", title="Integrantes", icon="👥"),
    st.Page("paginas/historial.py", title="Historial", icon="📚"),
]

navegacion = st.navigation(PAGINAS)
navegacion.run()
