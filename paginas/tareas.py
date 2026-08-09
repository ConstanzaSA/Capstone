import datetime
import streamlit as st

from componentes.interfaz import encabezado
from servicios.gestor_tareas import (
    actualizar_tarea,
    crear_tarea,
    eliminar_tarea,
    obtener_integrantes,
    obtener_tareas,
)


# ==========================================================
# ENCABEZADO
# ==========================================================

encabezado(
    "Tareas actuales",
    "Crea, asigna y actualiza actividades del proyecto",
)


# ==========================================================
# DATOS
# ==========================================================

integrantes = obtener_integrantes()
tareas = obtener_tareas()

nombres = {
    integrante["id"]: integrante["nombre"]
    for integrante in integrantes
}

ids_integrantes = list(nombres.keys())


def nombres_responsables(ids):
    """Convierte una lista de IDs en nombres."""

    if not ids:
        return "Sin asignar"

    return ", ".join(
        nombres.get(
            integrante_id,
            "Sin asignar",
        )
        for integrante_id in ids
    )


# ==========================================================
# CREAR TAREA
# ==========================================================

with st.expander(
    "➕ Añadir una tarea",
    expanded=True,
):

    with st.form(
        "formulario_nueva_tarea",
        clear_on_submit=True,
    ):

        # --------------------------------------------------
        # TÍTULO
        # --------------------------------------------------

        titulo = st.text_input(
            "Título de la tarea",
            placeholder="Ej.: Actualizar página web",
        )

        # --------------------------------------------------
        # RESPONSABLES / FECHA
        # --------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            responsables = st.multiselect(
                "Responsables",
                options=ids_integrantes,
                format_func=lambda x: nombres[x],
                help=(
                    "Selecciona las personas responsables "
                    "de esta tarea."
                ),
            )

        with col2:

            fecha_entrega = st.date_input(
                "Fecha de entrega",
                value=None,
                format="DD/MM/YYYY",
            )

        # --------------------------------------------------
        # PRIORIDAD
        # --------------------------------------------------

        prioridad = st.selectbox(
            "Prioridad",
            [
                "Baja",
                "Media",
                "Alta",
            ],
        )

        # --------------------------------------------------
        # ACTIVIDADES
        # --------------------------------------------------

        st.markdown(
            "### ☑️ Actividades"
        )

        st.caption(
            "Añade las actividades que componen esta tarea "
            "y asigna cada una a un integrante."
        )

        cantidad_actividades = st.number_input(
            "Cantidad de actividades",
            min_value=0,
            max_value=20,
            value=0,
            step=1,
            key="cantidad_actividades_nueva",
        )

        subtareas_nuevas = []

        for i in range(
            int(cantidad_actividades)
        ):

            st.markdown(
                f"**Actividad {i + 1}**"
            )

            col1, col2 = st.columns(
                [4, 2]
            )

            with col1:

                texto_actividad = st.text_input(
                    "Actividad",
                    placeholder=(
                        "Ej.: Revisar funcionamiento"
                    ),
                    key=f"nueva_actividad_{i}",
                    label_visibility="collapsed",
                )

            with col2:

                if responsables:

                    responsable_actividad = st.selectbox(
                        "Responsable",
                        options=responsables,
                        format_func=lambda x: (
                            nombres[x]
                        ),
                        key=(
                            f"nuevo_responsable_"
                            f"{i}"
                        ),
                        label_visibility="collapsed",
                    )

                else:

                    responsable_actividad = None

                    st.caption(
                        "Selecciona primero "
                        "un responsable"
                    )

            if texto_actividad.strip():

                subtareas_nuevas.append(
                    {
                        "texto": (
                            texto_actividad.strip()
                        ),
                        "integrante_id": (
                            responsable_actividad
                        ),
                        "completada": False,
                    }
                )

        # --------------------------------------------------
        # CREAR
        # --------------------------------------------------

        crear = st.form_submit_button(
            "Crear tarea",
            type="primary",
            use_container_width=True,
        )

        if crear:

            if not titulo.strip():

                st.error(
                    "El título de la tarea es obligatorio."
                )

            else:

                crear_tarea(
                    titulo=titulo,
                    descripcion="",
                    responsables_ids=responsables,
                    fecha_entrega=(
                        fecha_entrega.isoformat()
                        if fecha_entrega
                        else None
                    ),
                    prioridad=prioridad,
                    subtareas=subtareas_nuevas,
                )

                st.success(
                    "Tarea creada correctamente."
                )

                st.rerun()


# ==========================================================
# LISTA DE TAREAS
# ==========================================================

st.subheader("Lista de tareas")

tareas = obtener_tareas()


if not tareas:

    st.info(
        "Todavía no hay tareas registradas."
    )

else:

    # ======================================================
    # MOSTRAR TAREAS
    # ======================================================

    for tarea in sorted(
        tareas,
        key=lambda item: (
            item.get(
                "fecha_entrega"
            ) or "9999-12-31",
            item["titulo"].casefold(),
        ),
    ):

        with st.container(
            border=True
        ):

            # --------------------------------------------------
            # TÍTULO
            # --------------------------------------------------

            st.markdown(
                f"### {tarea['titulo']}"
            )

            # --------------------------------------------------
            # RESPONSABLES
            # --------------------------------------------------

            st.markdown(
                "**Responsables:** "
                + nombres_responsables(
                    tarea.get(
                        "responsables_ids",
                        [],
                    )
                )
            )

            # --------------------------------------------------
            # FECHA / PRIORIDAD
            # --------------------------------------------------

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

            # --------------------------------------------------
            # ACTIVIDADES
            # --------------------------------------------------

            subtareas = tarea.get(
                "subtareas",
                [],
            )

            with st.expander(
                f"☑️ Actividades ({len(subtareas)})",
                expanded=False,
            ):

                if not subtareas:

                    st.info(
                        "Esta tarea todavía "
                        "no tiene actividades."
                    )

                else:

                    for sub in subtareas:

                        texto = sub.get(
                            "texto",
                            "",
                        )

                        responsable_id = sub.get(
                            "integrante_id"
                        )

                        responsable = nombres.get(
                            responsable_id,
                            "Sin asignar",
                        )

                        if sub.get(
                            "completada",
                            False,
                        ):

                            icono = "☑️"

                        else:

                            icono = "⬜"

                        st.write(
                            f"{icono} {texto}"
                            f" — {responsable}"
                        )


# ==========================================================
# EDITAR TAREA
# ==========================================================

if tareas:

    st.divider()

    with st.expander(
        "✏️ Editar una tarea",
        expanded=False,
    ):

        # --------------------------------------------------
        # SELECCIONAR TAREA
        # --------------------------------------------------

        opciones_tareas = {
            tarea["id"]: tarea["titulo"]
            for tarea in tareas
        }

        tarea_seleccionada_id = st.selectbox(
            "Selecciona la tarea que quieres editar",
            options=list(
                opciones_tareas.keys()
            ),
            format_func=lambda x: (
                opciones_tareas[x]
            ),
        )

        tarea = next(
            (
                t
                for t in tareas
                if t["id"]
                == tarea_seleccionada_id
            ),
            None,
        )

        if tarea is not None:

            # ==================================================
            # DATOS GENERALES
            # ==================================================

            titulo_editado = st.text_input(
                "Título",
                value=tarea["titulo"],
                key=(
                    f"titulo_editar_"
                    f"{tarea['id']}"
                ),
            )

            responsables_editados = st.multiselect(
                "Responsables",
                options=ids_integrantes,
                default=[
                    x
                    for x in tarea.get(
                        "responsables_ids",
                        [],
                    )
                    if x in ids_integrantes
                ],
                format_func=lambda x: nombres[x],
                key=(
                    f"responsables_editar_"
                    f"{tarea['id']}"
                ),
            )

            # ==================================================
            # FECHA
            # ==================================================

            fecha_actual = None

            if tarea.get(
                "fecha_entrega"
            ):

                try:

                    fecha_actual = (
                        datetime.datetime.strptime(
                            tarea[
                                "fecha_entrega"
                            ],
                            "%Y-%m-%d",
                        ).date()
                    )

                except (
                    ValueError,
                    TypeError,
                ):

                    fecha_actual = None

            fecha_editada = st.date_input(
                "Fecha de entrega",
                value=fecha_actual,
                format="DD/MM/YYYY",
                key=(
                    f"fecha_editar_"
                    f"{tarea['id']}"
                ),
            )

            # ==================================================
            # PRIORIDAD
            # ==================================================

            prioridades = [
                "Baja",
                "Media",
                "Alta",
            ]

            prioridad_actual = tarea.get(
                "prioridad",
                "Baja",
            )

            prioridad_editada = st.selectbox(
                "Prioridad",
                prioridades,
                index=(
                    prioridades.index(
                        prioridad_actual
                    )
                    if prioridad_actual
                    in prioridades
                    else 0
                ),
                key=(
                    f"prioridad_editar_"
                    f"{tarea['id']}"
                ),
            )

            st.divider()

            # ==================================================
            # EDITAR CHECKLIST
            # ==================================================

            st.markdown(
                "### ☑️ Añadir o Eliminar Actividades"
            )

            st.caption(
                "Procura asignar la actividad a un "
                "miembro del equipo para que aparezca "
                "en su feed!"
            )

            actuales = tarea.get(
                "subtareas",
                [],
            )

            # --------------------------------------------------
            # CHECKLIST EXISTENTES
            # --------------------------------------------------

            checklist_editado = {}

            for i, sub in enumerate(
                actuales
            ):

                sub_id = sub["id"]

                texto_key = (
                    f"subtexto_"
                    f"{tarea['id']}_"
                    f"{sub_id}"
                )

                responsable_key = (
                    f"subresponsable_"
                    f"{tarea['id']}_"
                    f"{sub_id}"
                )

                eliminar_key = (
                    f"subeliminar_"
                    f"{tarea['id']}_"
                    f"{sub_id}"
                )

                col1, col2, col3 = st.columns(
                    [4, 2, 1]
                )

                # ------------------------------------------
                # TEXTO
                # ------------------------------------------

                texto = col1.text_input(
                    "Elemento",
                    value=sub.get(
                        "texto",
                        "",
                    ),
                    key=texto_key,
                    label_visibility="collapsed",
                )

                # ------------------------------------------
                # RESPONSABLE
                # ------------------------------------------

                responsables_disponibles = (
                    responsables_editados
                    if responsables_editados
                    else ids_integrantes
                )

                responsable_actual = sub.get(
                    "integrante_id"
                )

                if (
                    responsable_actual
                    not in responsables_disponibles
                ):

                    responsable_actual = (
                        responsables_disponibles[0]
                        if responsables_disponibles
                        else None
                    )

                if responsables_disponibles:

                    responsable = col2.selectbox(
                        "Responsable",
                        options=(
                            responsables_disponibles
                        ),
                        index=(
                            responsables_disponibles.index(
                                responsable_actual
                            )
                            if responsable_actual
                            in responsables_disponibles
                            else 0
                        ),
                        format_func=lambda x: (
                            nombres[x]
                        ),
                        key=responsable_key,
                        label_visibility="collapsed",
                    )

                else:

                    responsable = None

                    col2.caption(
                        "Sin responsable"
                    )

                # ------------------------------------------
                # ELIMINAR
                # ------------------------------------------

                eliminar_check = col3.checkbox(
                    "🗑",
                    key=eliminar_key,
                    help="Eliminar esta actividad",
                )

                # ------------------------------------------
                # GUARDAR EN MEMORIA
                # ------------------------------------------

                if not eliminar_check:

                    if responsable is not None:

                        checklist_editado.setdefault(
                            responsable,
                            [],
                        ).append(
                            {
                                "id": sub_id,
                                "texto": texto,
                                "completada": bool(
                                    sub.get(
                                        "completada",
                                        False,
                                    )
                                ),
                            }
                        )

            # ==================================================
            # NUEVAS ACTIVIDADES
            # ==================================================

            nuevos_key = (
                f"nuevos_checklist_"
                f"{tarea['id']}"
            )

            if nuevos_key not in st.session_state:

                st.session_state[
                    nuevos_key
                ] = []

            st.markdown(
                "#### Nuevas actividades"
            )

            # --------------------------------------------------
            # MOSTRAR NUEVOS ELEMENTOS
            # --------------------------------------------------

            for i, nuevo in enumerate(
                st.session_state[nuevos_key]
            ):

                col1, col2, col3 = st.columns(
                    [4, 2, 1]
                )

                texto_key = (
                    f"nuevo_texto_"
                    f"{tarea['id']}_"
                    f"{i}"
                )

                responsable_key = (
                    f"nuevo_responsable_"
                    f"{tarea['id']}_"
                    f"{i}"
                )

                eliminar_key = (
                    f"nuevo_eliminar_"
                    f"{tarea['id']}_"
                    f"{i}"
                )

                # ------------------------------------------
                # TEXTO NUEVO
                # ------------------------------------------

                texto_nuevo = col1.text_input(
                    "Nueva actividad",
                    value=nuevo.get(
                        "texto",
                        "",
                    ),
                    key=texto_key,
                    placeholder=(
                        "Ej.: Probar funcionamiento"
                    ),
                    label_visibility="collapsed",
                )

                # ------------------------------------------
                # RESPONSABLE NUEVO
                # ------------------------------------------

                if responsables_editados:

                    responsable_nuevo = col2.selectbox(
                        "Responsable",
                        options=(
                            responsables_editados
                        ),
                        index=(
                            responsables_editados.index(
                                nuevo.get(
                                    "integrante_id"
                                )
                            )
                            if nuevo.get(
                                "integrante_id"
                            )
                            in responsables_editados
                            else 0
                        ),
                        format_func=lambda x: (
                            nombres[x]
                        ),
                        key=responsable_key,
                        label_visibility="collapsed",
                    )

                else:

                    responsable_nuevo = None

                    col2.caption(
                        "Asigna primero un responsable"
                    )

                # ------------------------------------------
                # ELIMINAR NUEVO
                # ------------------------------------------

                eliminar_nuevo = col3.button(
                    "🗑",
                    key=eliminar_key,
                    help="Quitar esta nueva actividad",
                )

                if eliminar_nuevo:

                    st.session_state[
                        nuevos_key
                    ].pop(i)

                    st.rerun()

            # ==================================================
            # BOTÓN AÑADIR ACTIVIDAD
            # ==================================================

            if st.button(
                "➕ Añadir actividad",
                key=f"add_check_{tarea['id']}",
                use_container_width=True,
            ):

                responsable_inicial = (
                    responsables_editados[0]
                    if responsables_editados
                    else None
                )

                st.session_state[
                    nuevos_key
                ].append(
                    {
                        "texto": "",
                        "integrante_id": (
                            responsable_inicial
                        ),
                    }
                )

                st.rerun()

            # ==================================================
            # BOTONES PRINCIPALES
            # ==================================================

            st.divider()

            guardar, eliminar = st.columns(
                [4, 1]
            )

            # ==================================================
            # GUARDAR CAMBIOS
            # ==================================================

            if guardar.button(
                "Guardar cambios",
                key=(
                    f"guardar_editar_"
                    f"{tarea['id']}"
                ),
                type="primary",
                use_container_width=True,
            ):

                # --------------------------------------------------
                # AGREGAR NUEVAS ACTIVIDADES
                # --------------------------------------------------

                for i, nuevo in enumerate(
                    st.session_state[nuevos_key]
                ):

                    texto_key = (
                        f"nuevo_texto_"
                        f"{tarea['id']}_"
                        f"{i}"
                    )

                    responsable_key = (
                        f"nuevo_responsable_"
                        f"{tarea['id']}_"
                        f"{i}"
                    )

                    texto_nuevo = (
                        st.session_state.get(
                            texto_key,
                            "",
                        )
                    )

                    responsable_nuevo = (
                        st.session_state.get(
                            responsable_key,
                            nuevo.get(
                                "integrante_id"
                            ),
                        )
                    )

                    if (
                        texto_nuevo
                        and responsable_nuevo
                        is not None
                    ):

                        checklist_editado.setdefault(
                            responsable_nuevo,
                            [],
                        ).append(
                            {
                                "id": None,
                                "texto": (
                                    texto_nuevo.strip()
                                ),
                                "completada": False,
                            }
                        )

                # --------------------------------------------------
                # ACTUALIZAR TAREA
                # --------------------------------------------------

                actualizar_tarea(
                    tarea_id=tarea["id"],
                    titulo=titulo_editado,
                    descripcion="",
                    responsables_ids=(
                        responsables_editados
                    ),
                    fecha_entrega=(
                        fecha_editada.isoformat()
                        if fecha_editada
                        else None
                    ),
                    prioridad=prioridad_editada,
                    subtareas_por_integrante=(
                        checklist_editado
                    ),
                )

                # --------------------------------------------------
                # LIMPIAR NUEVAS ACTIVIDADES
                # --------------------------------------------------

                st.session_state[
                    nuevos_key
                ] = []

                st.success(
                    "Tarea actualizada correctamente."
                )

                st.rerun()

            # ==================================================
            # ELIMINAR TAREA
            # ==================================================

            if eliminar.button(
                "Eliminar tarea",
                key=(
                    f"eliminar_tarea_"
                    f"{tarea['id']}"
                ),
                use_container_width=True,
            ):

                eliminar_tarea(
                    tarea["id"]
                )

                st.session_state.pop(
                    nuevos_key,
                    None,
                )

                st.rerun()
