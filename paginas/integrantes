import streamlit as st

from componentes.interfaz import encabezado
from servicios.gestor_tareas import guardar_integrantes, obtener_integrantes, obtener_tareas

encabezado("Integrantes", "Página individual de tareas pendientes y completadas")

integrantes = obtener_integrantes()
tareas = obtener_tareas()

pestanas = st.tabs([i["nombre"] for i in integrantes])
for pestana, integrante in zip(pestanas, integrantes):
    with pestana:
        col1, col2 = st.columns(2)
        nuevo_nombre = col1.text_input("Nombre", integrante["nombre"], key=f"nombre_{integrante['id']}")
        nuevo_rol = col2.text_input("Rol", integrante["rol"], key=f"rol_{integrante['id']}")
        if st.button("Guardar datos del integrante", key=f"guardar_integrante_{integrante['id']}"):
            integrante["nombre"] = nuevo_nombre.strip() or integrante["nombre"]
            integrante["rol"] = nuevo_rol.strip()
            guardar_integrantes(integrantes)
            st.success("Integrante actualizado.")
            st.rerun()

        asignadas = [t for t in tareas if t["responsable_id"] == integrante["id"]]
        pendientes = [t for t in asignadas if t["estado"] != "Completada"]
        completadas = [t for t in asignadas if t["estado"] == "Completada"]

        izquierda, derecha = st.columns(2)
        with izquierda:
            st.subheader("Tareas pendientes")
            if not pendientes:
                st.info("No hay tareas pendientes.")
            for tarea in pendientes:
                with st.container(border=True):
                    st.markdown(f"**{tarea['titulo']}**")
                    st.caption(f"{tarea['semana']} · {tarea['estado']} · {tarea['avance']}%")
                    st.progress(tarea["avance"] / 100)
        with derecha:
            st.subheader("Tareas completadas")
            if not completadas:
                st.info("No hay tareas completadas.")
            for tarea in completadas:
                with st.container(border=True):
                    st.markdown(f"**{tarea['titulo']}**")
                    st.caption(f"{tarea['semana']} · Completada")
