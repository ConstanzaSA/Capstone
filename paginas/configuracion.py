from datetime import date, datetime

import streamlit as st

from componentes.interfaz import encabezado
from servicios.gestor_tareas import guardar_configuracion, obtener_configuracion

encabezado("Configuración", "Edita la información general mostrada en la página principal")

configuracion = obtener_configuracion()
fecha_guardada = configuracion.get("proxima_entrega", "")
try:
    fecha_inicial = datetime.strptime(fecha_guardada, "%Y-%m-%d").date()
except (TypeError, ValueError):
    fecha_inicial = date.today()

with st.form("configuracion_proyecto"):
    nombre_proyecto = st.text_input(
        "Nombre del proyecto",
        value=configuracion.get("nombre_proyecto", "Capstone Robótica"),
    )
    proxima_entrega = st.date_input(
        "Próxima entrega",
        value=fecha_inicial,
        format="DD/MM/YYYY",
        help="Esta fecha aparece en la cuarta tarjeta de la página principal.",
    )
    guardar = st.form_submit_button(
        "Guardar configuración",
        type="primary",
        use_container_width=True,
    )

if guardar:
    configuracion["nombre_proyecto"] = nombre_proyecto.strip() or "Capstone Robótica"
    configuracion["proxima_entrega"] = proxima_entrega.isoformat()
    guardar_configuracion(configuracion)
    st.success("Configuración actualizada.")
    st.rerun()
