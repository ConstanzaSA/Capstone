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
# AÑADIR INTEGRANTE
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

        with col1:

            nombre_nuevo = st.text_input(
                "Nombre",
                placeholder="Ej.: Javier Aguilera",
            )

        with col2:

            rol_nuevo = st.text_input(
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

                st.error(
                    "El nombre es obligatorio."
                )

            else:

                crear_integrante(
                    nombre_nuevo.strip(),
                    rol_nuevo.strip(),
                )

                st.success(
                    "Integrante añadido correctamente."
                )

                st.rerun()


# ==========================================================
# SIN INTEGRANTES
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


    # ======================================================
    # CADA INTEGRANTE
    # ======================================================

    for pestana, integrante in zip(
        pestanas,
        integrantes,
    ):

        with pestana:

            st.markdown(
                f"### {integrante['nombre']}"
            )


            # ==================================================
            # DATOS DEL INTEGRANTE
            # ==================================================

            col1, col2 = st.columns(2)


            with col1:

                nuevo_nombre = st.text_input(
                    "Nombre",
                    integrante["nombre"],
                    key=f"nombre_{integrante['id']}",
                )


            with col2:

                nuevo_rol = st.text_input(
                    "Rol",
                    integrante.get(
                        "rol",
                        "",
                    ),
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

                st.success(
                    "Integrante actualizado."
                )

                st.rerun()


            # ==================================================
            # TAREAS DEL INTEGRANTE
            # ==================================================

            asignadas = [
                tarea
                for tarea in tareas
                if integrante["id"]
                in tarea.get(
                    "responsables_ids",
                    [],
                )
            ]


            pendientes = [
                tarea
                for tarea in asignadas
                if tarea.get(
                    "progreso_individual",
                    {},
                ).get(
                    integrante["id"],
                    0,
                ) < 100
            ]


            completadas = [
                tarea
                for tarea in asignadas
                if tarea.get(
                    "progreso_individual",
                    {},
                ).get(
                    integrante["id"],
                    0,
                ) == 100
            ]


            # ==================================================
            # TAREAS PENDIENTES
            # ==================================================

            st.subheader(
                "Tareas pendientes"
            )


            if not pendientes:

                st.info(
                    "No hay tareas pendientes."
                )


            for tarea in pendientes:

                with st.container(
                    border=True
                ):

                    # ------------------------------------------
                    # TÍTULO
                    # ------------------------------------------

                    st.markdown(
                        f"**{tarea['titulo']}**"
                    )


                    # ------------------------------------------
                    # ENTREGA
                    # ------------------------------------------

                    st.caption(
                        "Entrega: "
                        + str(
                            tarea.get(
                                "fecha_entrega"
                            )
                            or "Sin fecha"
                        )
                    )


                    # ------------------------------------------
                    # AVANCE INDIVIDUAL
                    # ------------------------------------------

                    avance = tarea.get(
                        "progreso_individual",
                        {},
                    ).get(
                        integrante["id"],
                        0,
                    )


                    st.progress(
                        avance / 100,
                        text=(
                            f"Tu avance: "
                            f"{avance}%"
                        ),
                    )


                    # ==================================================
                    # CHECKLIST DEL INTEGRANTE
                    # ==================================================

                    st.markdown(
                        "**Checklist**"
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


                    # ==================================================
                    # AÑADIR CHECKLIST PERSONAL
                    # ==================================================

                    clave_nueva = (
                        f"nueva_checklist_"
                        f"{integrante['id']}_"
                        f"{tarea['id']}"
                    )


                    if clave_nueva not in st.session_state:

                        st.session_state[
                            clave_nueva
                        ] = False


                    if st.button(
                        "＋ Añadir checklist",
                        key=(
                            f"boton_"
                            f"{clave_nueva}"
                        ),
                    ):

                        st.session_state[
                            clave_nueva
                        ] = True

                        st.rerun()


                    # --------------------------------------------------
                    # RECTÁNGULO PARA NUEVA CASILLA
                    # --------------------------------------------------

                    if st.session_state[
                        clave_nueva
                    ]:

                        with st.container(
                            border=True
                        ):

                            nuevo_checklist = st.text_input(
                                "Nueva casilla",
                                placeholder=(
                                    "Ej.: Probar funcionamiento"
                                ),
                                key=(
                                    f"input_"
                                    f"{clave_nueva}"
                                ),
                            )


                            col_guardar, col_cancelar = st.columns(
                                2
                            )


                            with col_guardar:

                                if st.button(
                                    "Añadir",
                                    key=(
                                        f"guardar_"
                                        f"{clave_nueva}"
                                    ),
                                    type="primary",
                                    use_container_width=True,
                                ):

                                    if nuevo_checklist.strip():

                                        # Esta función debe agregarse
                                        # al gestor_tareas.py
                                        from servicios.gestor_tareas import (
                                            crear_subtarea,
                                        )

                                        crear_subtarea(
                                            tarea_id=tarea["id"],
                                            integrante_id=integrante["id"],
                                            texto=nuevo_checklist.strip(),
                                        )

                                        st.session_state[
                                            clave_nueva
                                        ] = False

                                        st.success(
                                            "Checklist añadido."
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            "Escribe el contenido "
                                            "de la casilla."
                                        )


                            with col_cancelar:

                                if st.button(
                                    "Cancelar",
                                    key=(
                                        f"cancelar_"
                                        f"{clave_nueva}"
                                    ),
                                    use_container_width=True,
                                ):

                                    st.session_state[
                                        clave_nueva
                                    ] = False

                                    st.rerun()


                    # ==================================================
                    # GUARDAR AVANCE
                    # ==================================================

                    if cambios:

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


            # ==================================================
            # TAREAS COMPLETADAS
            # ==================================================

            st.subheader(
                "Tareas completadas"
            )


            if not completadas:

                st.info(
                    "No hay tareas completadas."
                )


            for tarea in completadas:

                with st.container(
                    border=True
                ):

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
                        1.0,
                        text="Tu avance: 100%",
                    )
