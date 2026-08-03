from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from componentes.interfaz import encabezado, tarjeta_indicador
from servicios.gestor_tareas import (
    avance_por_integrante,
    obtener_configuracion,
    obtener_integrantes,
    obtener_tareas,
)

configuracion = obtener_configuracion()
encabezado(
    configuracion.get("nombre_proyecto", "Capstone Robótica"),
    "Visualización semanal del avance del equipo",
)

tareas = obtener_tareas()
integrantes = obtener_integrantes()
resumen = avance_por_integrante()
completadas = sum(t["estado"] == "Completada" for t in tareas)
avance_global = round(sum(t["avance"] for t in tareas) / len(tareas), 1) if tareas else 0
proxima_entrega = configuracion.get("proxima_entrega") or "Sin definir"
if proxima_entrega != "Sin definir":
    try:
        proxima_entrega = datetime.strptime(proxima_entrega, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        pass

columnas = st.columns(4)
with columnas[0]:
    tarjeta_indicador("Tareas totales", str(len(tareas)), "Todas las actividades")
with columnas[1]:
    tarjeta_indicador("Completadas", str(completadas), "Actividades terminadas")
with columnas[2]:
    tarjeta_indicador("Avance global", f"{avance_global}%", "Porcentaje del proyecto")
with columnas[3]:
    tarjeta_indicador("Próxima entrega", proxima_entrega, "Define en Configuración")

st.subheader("Progreso por integrante")
df = pd.DataFrame(resumen)
if df.empty:
    st.info("Todavía no hay integrantes configurados.")
else:
    figura = px.bar(
        df,
        x="Integrante",
        y="Avance (%)",
        text="Avance (%)",
        hover_data=["Rol", "Tareas", "Completadas"],
        range_y=[0, 100],
    )
    figura.update_traces(texttemplate="%{text}%", textposition="outside")
    figura.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="#0d0c12",
        plot_bgcolor="#17131d",
        font=dict(color="#ffffff"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.12)"),
    )
    st.plotly_chart(figura, use_container_width=True)

st.subheader("Tareas semanales")
if not tareas:
    st.info("No hay tareas. Agrégalas desde la pestaña Tareas actuales.")
else:
    nombres = {integrante["id"]: integrante["nombre"] for integrante in integrantes}
    filas = []
    for tarea in tareas:
        filas.append(
            {
                "Tarea": tarea["titulo"],
                "Responsable": nombres.get(tarea.get("responsable_id"), "Sin asignar"),
                "Fecha de entrega": tarea.get("fecha_entrega") or "Sin fecha",
                "Estado": tarea["estado"],
                "Avance (%)": tarea["avance"],
                "Prioridad": tarea["prioridad"],
            }
        )
    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
