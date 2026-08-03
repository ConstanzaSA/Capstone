import pandas as pd
import plotly.express as px
import streamlit as st

from componentes.interfaz import encabezado, tarjeta_indicador
from servicios.almacenamiento import modo_almacenamiento
from servicios.gestor_tareas import avance_por_integrante, obtener_tareas

encabezado("Capstone Robótica", "Visualización semanal del avance del equipo")

tareas = obtener_tareas()
resumen = avance_por_integrante()
completadas = sum(t["estado"] == "Completada" for t in tareas)
avance_global = round(sum(t["avance"] for t in tareas) / len(tareas), 1) if tareas else 0

columnas = st.columns(4)
with columnas[0]: tarjeta_indicador("Tareas totales", str(len(tareas)), "Todas las semanas")
with columnas[1]: tarjeta_indicador("Completadas", str(completadas), "Actividades terminadas")
with columnas[2]: tarjeta_indicador("Avance global", f"{avance_global}%", "Promedio del proyecto")
with columnas[3]: tarjeta_indicador("Almacenamiento", modo_almacenamiento(), "GitHub o copia local")

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
    figura.update_layout(height=420, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(figura, use_container_width=True)

st.subheader("Tareas semanales")
if not tareas:
    st.info("No hay tareas. Agrégalas desde la pestaña Tareas actuales.")
else:
    nombres = {i["id"]: i["Integrante"] for i in []}
    integrantes_df = pd.DataFrame(resumen)
    st.dataframe(
        pd.DataFrame(tareas)[["titulo", "semana", "estado", "avance", "prioridad"]]
        .rename(columns={"titulo": "Tarea", "semana": "Semana", "estado": "Estado", "avance": "Avance (%)", "prioridad": "Prioridad"}),
        use_container_width=True,
        hide_index=True,
    )
