from pathlib import Path
import sys

import streamlit as st

CARPETA_PROYECTO = Path(__file__).resolve().parent
if str(CARPETA_PROYECTO) not in sys.path:
    sys.path.insert(0, str(CARPETA_PROYECTO))

from componentes.estilos import aplicar_estilos
from servicios.almacenamiento import inicializar_datos

st.set_page_config(
    page_title="Seguimiento de Capstone",
    page_icon="🤖",
    layout="wide",
)

aplicar_estilos()
inicializar_datos()

PAGINAS = [
    st.Page(str(CARPETA_PROYECTO / "paginas" / "inicio.py"), title="Inicio", default=True),
    st.Page(str(CARPETA_PROYECTO / "paginas" / "tareas.py"), title="Tareas Añadidas"),
    st.Page(str(CARPETA_PROYECTO / "paginas" / "integrantes.py"), title="Integrantes"),
    st.Page(str(CARPETA_PROYECTO/ "paginas"/ "compras.py"),title="Compras"),
    st.Page(str(CARPETA_PROYECTO / "paginas" / "inventario.py"), title="Inventario"),
    st.Page(str(CARPETA_PROYECTO / "paginas" / "configuracion.py"), title="Configuración"),
    st.Page(str(CARPETA_PROYECTO / "paginas" / "historial.py"), title="Historial")
]

st.navigation(PAGINAS).run()
