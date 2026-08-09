import streamlit as st

from componentes.interfaz import encabezado
from servicios.gestor_tareas import (
    actualizar_integrante,
    actualizar_subtarea,
    crear_integrante,
    obtener_integrantes,
    obtener_tareas,
)

encabezado(
    "Integrantes",
    "Cada integrante gestiona aquí su avance individual",
)

integrantes = obtener_integrantes()
tareas = obtener_tareas()


with st.expander(
    "➕ Añadir nuevo integrante",
    expanded=False,
):
    with st.form(
        "formulario_nuevo_integrante",
        clear_on_submit=True,
    ):
        col1, col2 = st.columns(2)

        nombre_nuevo = col1.text_input(
            "Nombre",
            placeholder="Ej.: Javier Aguilera",
        )

        rol_nuevo = col2.text_input(
            "Rol",
            placeholder="Ej.: Mecánica",
        )

        crear = st.form_submit_button(
            "Añadir integrante",
            type="primary",
            use_container_width=True,
        )

        if crear:
            if not nombre_nuevo.strip():
                st.error("El nombre es obligatorio.")
            else:
                crear_integrante(
                    nombre_nuevo,
                    rol_nuevo,
                )
                st.success(
                    "Integrante añadido correctamente."
                )
                st.rerun()


if not integrantes:
    st.info("Todavía no hay integrantes configurados.")
else:
    pestanas = st.tabs(
        [
            integrante["nombre"]
            for integrante in integrantes
        ]
    )

    for pestana, integrante in zip(
        pestanas,
        integrantes,
    ):
        with pestana:
            st.markdown(
                f"### {integrante['nombre']}"
            )

            col1, col2 = st.columns(2)

            nuevo_nombre = col1.text_input(
                "Nombre",
                integrante["nombre"],
                key=f"nombre_{integrante['id']}",
            )

            nuevo_rol = col2.text_input(
                "Rol",
                integrante.get("rol", ""),
                key=f"rol_{integrante['id']}",
            )

            if st.button(
                "Guardar datos del integrante",
                key=f"guardar_integrante_{integrante['id']}",
                type="primary",
            ):
                actualizar_integrante(
                    integrante["id"],
                    nuevo_nombre,
                    nuevo_rol,
                )
                st.success("Integrante actualizado.")
                st.rerun()

            asignadas = [
                tarea
                for tarea in tareas
                if integrante["id"]
                in tarea.get("responsables_ids", [])
            ]

            pendientes = [
                tarea
                for tarea in asignadas
                if tarea["avance"] < 100
            ]

            completadas = [
                tarea
                for tarea in asignadas
                if tarea["avance"] == 100
            ]

            izquierda, derecha = st.columns(2)

            with izquierda:
                st.subheader("Tareas pendientes")

                if not pendientes:
                    st.info(
                        "No hay tareas pendientes."
                    )

                for tarea in pendientes:
                    with st.container(border=True):
                        avance = tarea[
                            "progreso_individual"
                        ].get(
                            integrante["id"],
                            0,
                        )

                        st.markdown(
                            f"**{tarea['titulo']}**"
                        )

                        st.caption(
                            "Entrega: "
                            + str(
                                tarea.get(
                                    "fecha_entrega"
                                )
                                or "Sin fecha"
                            )
                        )

                        st.progress(
                            avance / 100,
                            text=f"Tu avance: {avance}%",
                        )

                        propias = [
                            sub
                            for sub in tarea.get(
                                "subtareas",
                                [],
                            )
                            if sub.get(
                                "integrante_id"
                            )
                            == integrante["id"]
                        ]

                        if propias:
                            st.markdown(
                                "**Checklist**"
                            )

                            cambios = {}

                            for sub in propias:
                                cambios[sub["id"]] = st.checkbox(
                                    sub["texto"],
                                    value=bool(
                                        sub.get(
                                            "completada"
                                        )
                                    ),
                                    key=(
                                        f"check_"
                                        f"{integrante['id']}_"
                                        f"{sub['id']}"
                                    ),
                                )

                            if st.button(
                                "Guardar avance",
                                key=(
                                    f"avance_"
                                    f"{integrante['id']}_"
                                    f"{tarea['id']}"
                                ),
                                type="primary",
                            ):
                                for sub_id, completada in cambios.items():
                                    actualizar_subtarea(
                                        sub_id,
                                        completada,
                                    )

                                st.success(
                                    "Avance guardado."
                                )
                                st.rerun()
                        else:
                            st.info(
                                "Esta tarea todavía no tiene "
                                "casillas de avance."
                            )

            with derecha:
                st.subheader("Tareas completadas")

                if not completadas:
                    st.info(
                        "No hay tareas completadas."
                    )

                for tarea in completadas:
                    with st.container(border=True):
                        st.markdown(
                            f"**{tarea['titulo']}**"
                        )

                        st.caption(
                            "Avance individual: 100% · "
                            "Completada"
                        )
