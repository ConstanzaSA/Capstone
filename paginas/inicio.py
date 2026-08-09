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
    configuracion.get(
        "nombre_proyecto",
        "Capstone Robótica",
    ),
    "Visualización del avance del equipo",
)

tareas = obtener_tareas()
integrantes = obtener_integrantes()
resumen = avance_por_integrante()

completadas = sum(
    tarea["avance"] == 100
    for tarea in tareas
)

avance_global = (
    round(
        sum(
            tarea["avance"]
            for tarea in tareas
        )
        / len(tareas),
        1,
    )
    if tareas
    else 0
)

proxima_entrega = (
    configuracion.get("proxima_entrega")
    or "Sin definir"
)

columnas = st.columns(4)

with columnas[0]:
    tarjeta_indicador(
        "Tareas totales",
        str(len(tareas)),
        "Todas las actividades",
    )

with columnas[1]:
    tarjeta_indicador(
        "Completadas",
        str(completadas),
        "Actividades terminadas",
    )

with columnas[2]:
    tarjeta_indicador(
        "Avance global",
        f"{avance_global}%",
        "Promedio de las tareas",
    )

with columnas[3]:
    tarjeta_indicador(
        "Próxima Presentación",
        proxima_entrega or "Sin definir",
        "Fecha de presentación",
    )

st.subheader("Progreso del Proyecto")

df = pd.DataFrame(resumen)

if df.empty:
    st.info("Todavía no hay integrantes configurados.")
else:
    figura = px.bar(
        df,
        x="Integrante",
        y="Avance (%)",
        text="Avance (%)",
        hover_data=[
            "Rol",
            "Tareas",
            "Completadas",
        ],
        range_y=[0, 100],
    )

    figura.update_traces(
        texttemplate="%{text}%",
        textposition="outside",
    )

    figura.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="#0d0c12",
        plot_bgcolor="#17131d",
        font=dict(color="#ffffff"),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.08)"
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.12)"
        ),
    )

    st.plotly_chart(
        figura,
        use_container_width=True,
    )

st.subheader("Resumen Tareas")

if not tareas:
    st.info(
        "No hay tareas. Agrégalas desde Tareas actuales."
    )
else:
    nombres = {
        integrante["id"]: integrante["nombre"]
        for integrante in integrantes
    }

    filas = []

    for tarea in tareas:
        responsables = tarea.get(
            "responsables_ids",
            [],
        )

        texto_responsables = (
            ", ".join(
                nombres.get(
                    integrante_id,
                    "Sin asignar",
                )
                for integrante_id in responsables
            )
            if responsables
            else "Sin asignar"
        )

        filas.append(
            {
                "Tarea": tarea["titulo"],
                "Responsable(s)": texto_responsables,
                "Fecha de entrega": (
                    tarea.get("fecha_entrega")
                    or "Sin fecha"
                ),
                "Estado": tarea["estado"],
                "Avance (%)": tarea["avance"],
                "Prioridad": tarea["prioridad"],
            }
        )

    st.dataframe(
        pd.DataFrame(filas),
        use_container_width=True,
        hide_index=True,
    )
