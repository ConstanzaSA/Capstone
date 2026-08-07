import pandas as pd
import streamlit as st
from componentes.interfaz import encabezado
from servicios.gestor_tareas import obtener_historial
encabezado("Historial","Registro permanente de los cambios realizados en el proyecto")
historial=obtener_historial()
if not historial:
    st.info("Todavía no hay movimientos registrados.")
else:
    st.dataframe(pd.DataFrame([{"Fecha":e.get("fecha",""),"Acción":e.get("accion",""),"Tarea":e.get("tarea",""),"Detalle":e.get("detalle","")} for e in historial]),use_container_width=True,hide_index=True)
