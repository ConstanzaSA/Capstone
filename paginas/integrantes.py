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


# ==========================================================
# AÑADIR NUEVO INTEGRANTE
# ==========================================================

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
            placeholder="Ej.: Alberto",
        )

        rol_nuevo = col2.text_input(
            "Rol",
            placeholder="Ej.: Robotics",
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


# ==========================================================
# MOSTRAR INTEGRANTES
# ==========================================================

if not integrantes:

    st.info(
        "Todavía no hay integrantes configurados."
    )

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

            #st.markdown(
            #    f"### {integrante['nombre']}"
            #)

            # ==================================================
            # DATOS DEL INTEGRANTE
            # ==================================================

            #col1, col2 = st.columns(2)

            #nuevo_nombre = col1.text_input(
            #    "Nombre",
            #    integrante["nombre"],
            #    key=f"nombre_{integrante['id']}",
            #)

            #nuevo_rol = col2.text_input(
            #    "Rol",
            #    integrante.get("rol", ""),
            #    key=f"rol_{integrante['id']}",
            #)

            #if st.button(
            #    "Guardar datos del integrante",
            #    key=f"guardar_integrante_{integrante['id']}",
            #    type="primary",
            #):

            #    actualizar_integrante(
            #        integrante["id"],
            #        nuevo_nombre,
            #        nuevo_rol,
            #    )

            #    st.success(
            #        "Integrante actualizado."
            #    )

            #    st.rerun()

            #st.divider()

            # ==================================================
            # TAREAS DEL INTEGRANTE
            # ==================================================

            tareas_integrante = [
                tarea
                for tarea in tareas
                if integrante["id"]
                in tarea.get(
                    "responsables_ids",
                    [],
                )
            ]

            st.subheader("Mis tareas")

            if not tareas_integrante:

                st.info(
                    "No tienes tareas asignadas."
                )

                continue

            # ==================================================
            # MOSTRAR TODAS LAS TAREAS
            # ==================================================

            for tarea in tareas_integrante:

                # ----------------------------------------------
                # Checklist que pertenece a este integrante
                # ----------------------------------------------

                propias = [
                    sub
                    for sub in tarea.get(
                        "subtareas",
                        [],
                    )
                    if sub.get(
                        "integrante_id"
                    ) == integrante["id"]
                ]

                with st.container(
                    border=True
                ):

                    # ------------------------------------------
                    # TÍTULO
                    # ------------------------------------------

                    st.markdown(
                        f"### {tarea['titulo']}"
                    )

                    # ------------------------------------------
                    # FECHA Y PRIORIDAD
                    # ------------------------------------------

                    col1, col2 = st.columns(2)

                    with col1:
                        st.caption(
                            "📅 Entrega: "
                            + str(
                                tarea.get(
                                    "fecha_entrega"
                                )
                                or "Sin fecha"
                            )
                        )

                    with col2:
                        st.caption(
                            "🚩 Prioridad: "
                            + tarea.get(
                                "prioridad",
                                "Baja",
                            )
                        )

                    # ------------------------------------------
                    # SI NO TIENE CHECKLIST
                    # ------------------------------------------

                    if not propias:

                        st.info(
                            "Esta tarea no tiene "
                            "checklist asignado."
                        )

                        continue

                    # ------------------------------------------
                    # CHECKLIST PERSONAL
                    # ------------------------------------------

                    st.markdown(
                        "**Checklist**"
                    )

                    cambios = {}

                    for sub in propias:

                        cambios[sub["id"]] = st.checkbox(
                            sub["texto"],
                            value=bool(
                                sub.get(
                                    "completada",
                                    False,
                                )
                            ),
                            key=(
                                f"check_"
                                f"{integrante['id']}_"
                                f"{sub['id']}"
                            ),
                        )

                    # ------------------------------------------
                    # CALCULAR AVANCE INDIVIDUAL
                    # ------------------------------------------

                    total = len(cambios)

                    completadas = sum(
                        cambios.values()
                    )

                    avance = int(
                        completadas
                        / total
                        * 100
                    )

                    # ------------------------------------------
                    # MOSTRAR AVANCE
                    # ------------------------------------------

                    st.progress(
                        avance / 100,
                        text=(
                            f"Avance individual: "
                            f"{avance}%"
                        ),
                    )

                    # ------------------------------------------
                    # GUARDAR
                    # ------------------------------------------

                    if st.button(
                        "Guardar avance",
                        key=(
                            f"avance_"
                            f"{integrante['id']}_"
                            f"{tarea['id']}"
                        ),
                        type="primary",
                    ):

                        for (
                            sub_id,
                            completada,
                        ) in cambios.items():

                            actualizar_subtarea(
                                sub_id,
                                completada,
                            )

                        st.success(
                            "Avance guardado."
                        )

                        st.rerun()
