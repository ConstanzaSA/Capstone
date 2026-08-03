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
nombres = {i["id"]: i["nombre"] for i in integrantes}
ids = list(nombres)

with st.expander("➕ Añadir una tarea", expanded=True):
    with st.form("formulario_nueva_tarea", clear_on_submit=True):
        titulo = st.text_input("Título de la tarea")
        descripcion = st.text_area("Descripción")
        col1, col2, col3 = st.columns(3)
        responsable = col1.selectbox("Responsable", ids, format_func=lambda x: nombres[x])
        semana = col2.text_input("Semana", placeholder="Ejemplo: 2026-S32")
        prioridad = col3.selectbox("Prioridad", ["Baja", "Media", "Alta"])
        enviar = st.form_submit_button("Crear y asignar", type="primary", use_container_width=True)
        if enviar:
            if not titulo.strip() or not semana.strip():
                st.error("El título y la semana son obligatorios.")
            else:
                crear_tarea(titulo, descripcion, responsable, semana, prioridad)
                st.success("Tarea creada y asignada.")
                st.rerun()

st.subheader("Lista de tareas")
tareas = obtener_tareas()
if not tareas:
    st.info("Todavía no hay tareas registradas.")

for tarea in sorted(tareas, key=lambda t: (t["estado"] == "Completada", t["semana"], t["titulo"])):
    with st.container(border=True):
        st.markdown(f"### {tarea['titulo']}")
        st.caption(f"Semana {tarea['semana']} · Prioridad {tarea['prioridad']}")
        if tarea.get("descripcion"):
            st.write(tarea["descripcion"])

        col1, col2, col3 = st.columns([1.3, 1.2, 1])
        responsable = col1.selectbox(
            "Responsable",
            ids,
            index=ids.index(tarea["responsable_id"]),
            format_func=lambda x: nombres[x],
            key=f"responsable_{tarea['id']}",
        )
        estado = col2.selectbox(
            "Estado",
            ["Pendiente", "En progreso", "Completada"],
            index=["Pendiente", "En progreso", "Completada"].index(tarea["estado"]),
            key=f"estado_{tarea['id']}",
        )
        avance = col3.slider("Avance", 0, 100, int(tarea["avance"]), 5, key=f"avance_{tarea['id']}")

        boton1, boton2 = st.columns([4, 1])
        if boton1.button("Guardar cambios", key=f"guardar_{tarea['id']}", type="primary", use_container_width=True):
            actualizar_tarea(tarea["id"], estado, avance, responsable)
            st.success("Cambios guardados.")
            st.rerun()
        if boton2.button("Eliminar", key=f"eliminar_{tarea['id']}", use_container_width=True):
            eliminar_tarea(tarea["id"])
            st.rerun()
