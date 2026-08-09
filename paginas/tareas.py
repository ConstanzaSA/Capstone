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


encabezado(
    "Tareas actuales",
    "Crea, asigna y actualiza actividades del proyecto",
)


# ==========================================================
# DATOS
# ==========================================================

integrantes = obtener_integrantes()

nombres = {
    integrante["id"]: integrante["nombre"]
    for integrante in integrantes
}

ids_integrantes = list(nombres.keys())


def nombres_responsables(ids):
    if not ids:
        return "Sin asignar"

    return ", ".join(
        nombres.get(integrante_id, "Sin asignar")
        for integrante_id in ids
    )


# ==========================================================
# ESTADO DEL CHECKLIST PARA CREAR TAREA
# ==========================================================

if "checklist_nueva_tarea" not in st.session_state:
    st.session_state.checklist_nueva_tarea = []


# ==========================================================
# AÑADIR TAREA
# ==========================================================

with st.expander(
    "➕ Añadir una tarea",
    expanded=True,
):

    # ------------------------------------------------------
    # INFORMACIÓN GENERAL
    # ------------------------------------------------------

    titulo = st.text_input(
        "Título de la tarea",
        placeholder="Ej.: Diseñar soporte del motor",
        key="nueva_tarea_titulo",
    )

    col1, col2 = st.columns(2)

    with col1:

        responsables = st.multiselect(
            "Responsables",
            options=ids_integrantes,
            format_func=lambda x: nombres[x],
            key="nueva_tarea_responsables",
            help=(
                "Puedes seleccionar uno, varios o ninguno. "
                "Los responsables se utilizan para asignar "
                "las casillas del checklist."
            ),
        )

    with col2:

        fecha_entrega = st.date_input(
            "Fecha de entrega",
            value=None,
            format="DD/MM/YYYY",
            key="nueva_tarea_fecha",
        )

    prioridad = st.selectbox(
        "Prioridad",
        ["Baja", "Media", "Alta"],
        key="nueva_tarea_prioridad",
    )


    # ======================================================
    # CHECKLIST
    # ======================================================

    st.markdown("### Checklist")

    st.caption(
        "Cada casilla debe asignarse a un integrante. "
        "El avance individual se calculará según las "
        "casillas completadas por cada integrante."
    )


    # ------------------------------------------------------
    # MOSTRAR CHECKLISTS EXISTENTES
    # ------------------------------------------------------

    checklist_actual = st.session_state.checklist_nueva_tarea.copy()

    for i, item in enumerate(checklist_actual):

        with st.container(border=True):

            col1, col2, col3 = st.columns([6, 3, 1])

            with col1:

                texto = st.text_input(
                    "Casilla",
                    value=item.get("texto", ""),
                    key=f"nueva_check_texto_{i}",
                    placeholder="Ej.: Comprar material",
                )

            with col2:

                responsable_check = st.selectbox(
                    "Responsable",
                    options=[""] + ids_integrantes,
                    index=(
                        (
                            [""] + ids_integrantes
                        ).index(
                            item.get(
                                "integrante_id",
                                "",
                            )
                        )
                        if item.get("integrante_id", "")
                        in ids_integrantes
                        else 0
                    ),
                    format_func=lambda x: (
                        "Sin asignar"
                        if x == ""
                        else nombres[x]
                    ),
                    key=f"nueva_check_responsable_{i}",
                )

            with col3:

                st.write("")

                if st.button(
                    "🗑",
                    key=f"eliminar_nueva_check_{i}",
                    help="Eliminar esta casilla",
                ):

                    st.session_state.checklist_nueva_tarea.pop(i)

                    st.rerun()


            # Guardamos cambios del elemento
            st.session_state.checklist_nueva_tarea[i] = {
                "texto": texto,
                "integrante_id": responsable_check,
            }


    # ------------------------------------------------------
    # AÑADIR NUEVA CASILLA
    # ------------------------------------------------------

    if st.button(
        "＋ Añadir checklist",
        key="boton_agregar_checklist",
        use_container_width=True,
    ):

        st.session_state.checklist_nueva_tarea.append(
            {
                "texto": "",
                "integrante_id": "",
            }
        )

        st.rerun()


    # ======================================================
    # CREAR
    # ======================================================

    st.markdown("")

    if st.button(
        "Crear tarea",
        type="primary",
        use_container_width=True,
        key="crear_tarea",
    ):

        if not titulo.strip():

            st.error(
                "El título de la tarea es obligatorio."
            )

        else:

            # ----------------------------------------------
            # Convertir checklist a formato por integrante
            # ----------------------------------------------

            subtareas_por_integrante = {}

            for item in st.session_state.checklist_nueva_tarea:

                texto = item.get(
                    "texto",
                    "",
                ).strip()

                integrante_id = item.get(
                    "integrante_id",
                    "",
                )

                if not texto:
                    continue

                if not integrante_id:
                    st.error(
                        "Todas las casillas deben tener "
                        "un responsable."
                    )
                    st.stop()

                subtareas_por_integrante.setdefault(
                    integrante_id,
                    [],
                ).append(
                    {
                        "texto": texto,
                        "completada": False,
                    }
                )


            # ----------------------------------------------
            # Crear tarea
            # ----------------------------------------------

            crear_tarea(
                titulo=titulo.strip(),
                descripcion="",
                responsables_ids=responsables,
                fecha_entrega=(
                    fecha_entrega.isoformat()
                    if fecha_entrega
                    else None
                ),
                prioridad=prioridad,
                subtareas_por_integrante=(
                    subtareas_por_integrante
                ),
            )


            # ----------------------------------------------
            # Limpiar formulario
            # ----------------------------------------------

            st.session_state.checklist_nueva_tarea = []

            st.session_state.pop(
                "nueva_tarea_titulo",
                None,
            )

            st.session_state.pop(
                "nueva_tarea_responsables",
                None,
            )

            st.session_state.pop(
                "nueva_tarea_fecha",
                None,
            )

            st.session_state.pop(
                "nueva_tarea_prioridad",
                None,
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

    for tarea in sorted(
        tareas,
        key=lambda item: (
            item["estado"] == "Completada",
            item.get("fecha_entrega")
            or "9999-12-31",
            item["titulo"].casefold(),
        ),
    ):

        with st.container(border=True):

            # ==================================================
            # INFORMACIÓN DE LA TAREA
            # ==================================================

            st.markdown(
                f"### {tarea['titulo']}"
            )

            st.caption(
                f"Entrega: "
                f"{tarea.get('fecha_entrega') or 'Sin fecha'}"
                f" · Prioridad: "
                f"{tarea['prioridad']}"
                f" · Avance global: "
                f"{tarea['avance']}%"
            )

            st.markdown(
                "**Responsables:** "
                + nombres_responsables(
                    tarea.get(
                        "responsables_ids",
                        [],
                    )
                )
            )

            st.markdown(
                f"**Avance global:** "
                f"{tarea['avance']}%"
            )


            # ==================================================
            # EDITAR TAREA
            # ==================================================

            with st.expander(
                "✏️ Editar tarea",
                expanded=False,
            ):

                titulo_editado = st.text_input(
                    "Título",
                    value=tarea["titulo"],
                    key=f"titulo_{tarea['id']}",
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
                    key=f"responsables_{tarea['id']}",
                )


                fecha_actual = None

                if tarea.get("fecha_entrega"):

                    try:

                        fecha_actual = (
                            datetime.datetime.strptime(
                                tarea["fecha_entrega"],
                                "%Y-%m-%d",
                            ).date()
                        )

                    except ValueError:

                        fecha_actual = None


                fecha_editada = st.date_input(
                    "Fecha de entrega",
                    value=fecha_actual,
                    format="DD/MM/YYYY",
                    key=f"fecha_{tarea['id']}",
                )


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
                    key=f"prioridad_{tarea['id']}",
                )


                # ----------------------------------------------
                # BOTONES
                # ----------------------------------------------

                guardar, eliminar = st.columns(
                    [4, 1]
                )


                with guardar:

                    if st.button(
                        "Guardar cambios",
                        key=f"guardar_{tarea['id']}",
                        type="primary",
                        use_container_width=True,
                    ):

                        actualizar_tarea(
                            tarea_id=tarea["id"],
                            titulo=titulo_editado,
                            descripcion="",
                            responsables_ids=responsables_editados,
                            fecha_entrega=(
                                fecha_editada.isoformat()
                                if fecha_editada
                                else None
                            ),
                            prioridad=prioridad_editada,
                        )

                        st.success(
                            "Tarea actualizada correctamente."
                        )

                        st.rerun()


                with eliminar:

                    if st.button(
                        "Eliminar",
                        key=f"eliminar_{tarea['id']}",
                        use_container_width=True,
                    ):

                        eliminar_tarea(
                            tarea["id"]
                        )

                        st.rerun()
