import pandas as pd
import streamlit as st

from componentes.interfaz import encabezado
from servicios.gestor_tareas import obtener_historial

encabezado("Historial", "Registro de creaciones, cambios, reasignaciones y eliminaciones")

historial = obtener_historial()
if not historial:
    st.info("Todavía no hay movimientos registrados.")
else:
    st.dataframe(
        pd.DataFrame(historial).rename(columns={
            "fecha": "Fecha",
            "accion": "Acción",
            "tarea": "Tarea",
            "detalle": "Detalle",
        })[["Fecha", "Acción", "Tarea", "Detalle"]],
        use_container_width=True,
        hide_index=True,
    )
