from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from componentes.interfaz import encabezado
from servicios.gestor_tareas import (
    actualizar_tarea,
    crear_tarea,
    eliminar_tarea,
    obtener_integrantes,
    obtener_tareas,
)

encabezado("Tareas actuales", "Crea, asigna, actualiza o reasigna actividades")

integrantes = obtener_integrantes()
nombres = {integrante["id"]: integrante["nombre"] for integrante in integrantes}
opciones_ids = [integrante["id"] for integrante in integrantes]


def nombres_responsables(ids: list[str]) -> str:
    nombres_seleccionados = [nombres.get(i, "Integrante") for i in ids]
    return ", ".join(nombres_seleccionados) if nombres_seleccionados else "Sin asignar"


def convertir_fecha(valor: str) -> date:
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


with st.expander("➕ Añadir una tarea", expanded=True):
    with st.form("formulario_nueva_tarea", clear_on_submit=True):
        titulo = st.text_input("Título de la tarea")
        descripcion = st.text_area("Descripción")

        col1, col2, col3 = st.columns(3)

        responsables = col1.multiselect(
            "Responsable(s)",
            options=opciones_ids,
            format_func=lambda integrante_id: nombres.get(integrante_id, "Integrante"),
            help="Puedes seleccionar una, varias personas o dejar la tarea sin responsable.",
        )

        fecha_entrega = col2.date_input(
            "Fecha de entrega",
            value=date.today(),
            format="DD/MM/YYYY",
            help="Día en que la tarea debe estar lista.",
        )

        prioridad = col3.selectbox("Prioridad", ["Baja", "Media", "Alta"])

        enviar = st.form_submit_button(
            "Crear tarea",
            type="primary",
            use_container_width=True,
        )

        if enviar:
            if not titulo.strip():
                st.error("El título de la tarea es obligatorio.")
            else:
                crear_tarea(
                    titulo,
                    descripcion,
                    responsables,
                    fecha_entrega.isoformat(),
                    prioridad,
                )
                st.success("Tarea creada correctamente.")
                st.rerun()


st.subheader("Lista de tareas")
tareas = obtener_tareas()

if not tareas:
    st.info("Todavía no hay tareas registradas.")

for tarea in sorted(
    tareas,
    key=lambda item: (
        item["estado"] == "Completada",
        item.get("fecha_entrega") or "9999-12-31",
        item["titulo"].casefold(),
    ),
):
    with st.container(border=True):
        st.markdown(f"### {tarea['titulo']}")
        fecha_texto = tarea.get("fecha_entrega") or "Sin fecha"
        st.caption(
            f"Responsable(s): {nombres_responsables(tarea.get('responsable_ids', []))} · "
            f"Entrega: {fecha_texto} · Prioridad: {tarea['prioridad']}"
        )

        if tarea.get("descripcion"):
            st.write(tarea["descripcion"])

        col1, col2, col3, col4 = st.columns([1.5, 1.1, 1.05, 1])

        responsables_actuales = tarea.get("responsable_ids", [])
        responsables = col1.multiselect(
            "Responsable(s)",
            options=opciones_ids,
            default=[i for i in responsables_actuales if i in opciones_ids],
            format_func=lambda integrante_id: nombres.get(integrante_id, "Integrante"),
            key=f"responsables_{tarea['id']}",
        )

        fecha = col2.date_input(
            "Fecha de entrega",
            value=convertir_fecha(tarea.get("fecha_entrega", "")),
            format="DD/MM/YYYY",
            key=f"fecha_{tarea['id']}",
        )

        estados = ["Pendiente", "En progreso", "Completada"]
        estado = col3.selectbox(
            "Estado",
            estados,
            index=estados.index(tarea["estado"]),
            key=f"estado_{tarea['id']}",
        )

        avance = col4.slider(
            "Avance",
            0,
            100,
            int(tarea["avance"]),
            5,
            key=f"avance_{tarea['id']}",
        )

        boton1, boton2 = st.columns([4, 1])

        if boton1.button(
            "Guardar cambios",
            key=f"guardar_{tarea['id']}",
            type="primary",
            use_container_width=True,
        ):
            actualizar_tarea(
                tarea["id"],
                estado,
                avance,
                responsables,
                fecha.isoformat(),
            )
            st.success("Cambios guardados.")
            st.rerun()

        if boton2.button(
            "Eliminar",
            key=f"eliminar_{tarea['id']}",
            use_container_width=True,
        ):
            eliminar_tarea(tarea["id"])
            st.rerun()
