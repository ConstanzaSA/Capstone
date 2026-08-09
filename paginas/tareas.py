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

integrantes = obtener_integrantes()
nombres = {
    integrante["id"]: integrante["nombre"]
    for integrante in integrantes
}
ids_integrantes = list(nombres.keys())


def nombres_responsables(ids: list[str]) -> str:
    if not ids:
        return "Sin asignar"

    return ", ".join(
        nombres.get(integrante_id, "Sin asignar")
        for integrante_id in ids
    )


def formulario_subtareas(
    prefijo: str,
    subtareas_iniciales: list[dict] | None = None,
) -> list[str]:
    iniciales = subtareas_iniciales or []

    textos = []

    if iniciales:
        for i, subtarea in enumerate(iniciales):
            texto = st.text_input(
                f"Subtarea {i + 1}",
                value=subtarea.get("texto", ""),
                key=f"{prefijo}_sub_{i}",
            )
            textos.append(texto)
    else:
        texto = st.text_input(
            "Subtarea 1",
            key=f"{prefijo}_sub_0",
            placeholder="Ej.: Diseñar soporte",
        )
        if texto:
            textos.append(texto)

    cantidad = st.number_input(
        "Cantidad de casillas adicionales",
        min_value=0,
        max_value=20,
        value=0,
        step=1,
        key=f"{prefijo}_cantidad_extra",
        help="Permite crear varias casillas de checklist de una vez.",
    )

    for i in range(int(cantidad)):
        textos.append(
            st.text_input(
                f"Subtarea adicional {i + 1}",
                key=f"{prefijo}_extra_{i}",
            )
        )

    return textos


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
        # ==================================================
        # TÍTULO
        # ==================================================

        titulo = st.text_input(
            "Título de la tarea",
            placeholder="Ej.: Diseñar soporte del motor",
        )

        # ==================================================
        # RESPONSABLES Y FECHA
        # ==================================================

        col1, col2 = st.columns(2)

        with col1:
            responsables = st.multiselect(
                "Responsables",
                options=ids_integrantes,
                format_func=lambda x: nombres[x],
                help=(
                    "Puedes seleccionar uno, varios o ninguno. "
                    "Cada responsable tendrá su propio checklist "
                    "y avance individual."
                ),
            )

        with col2:
            fecha_entrega = st.date_input(
                "Fecha de entrega",
                value=None,
                format="DD/MM/YYYY",
                help="Día exacto en que la tarea debe estar lista.",
            )

        # ==================================================
        # PRIORIDAD
        # ==================================================

        prioridad = st.selectbox(
            "Prioridad",
            ["Baja", "Media", "Alta"],
        )

        # ==================================================
        # CHECKLIST
        # ==================================================

        st.markdown("### Checklist")

        st.caption(
            "Añade las etapas que deberán completar los "
            "responsables. El avance se calculará "
            "automáticamente a partir de estas casillas."
        )

        # Número de casillas que se están mostrando.
        if "nueva_tarea_checklist_cantidad" not in st.session_state:
            st.session_state.nueva_tarea_checklist_cantidad = 1

        cantidad = st.session_state.nueva_tarea_checklist_cantidad

        subtareas_nuevas = []

        for i in range(cantidad):

            col_check, col_delete = st.columns([10, 1])

            with col_check:
                texto = st.text_input(
                    f"Checklist {i + 1}",
                    key=f"nueva_tarea_check_{i}",
                    label_visibility="collapsed",
                    placeholder="Ej.: Comprar material",
                )

                subtareas_nuevas.append(texto)

            with col_delete:
                eliminar = st.form_submit_button(
                    "🗑",
                    key=f"eliminar_check_{i}",
                )

                if eliminar:
                    # Eliminar esta casilla desplazando
                    # las siguientes hacia arriba.
                    for j in range(i, cantidad - 1):
                        anterior = st.session_state.get(
                            f"nueva_tarea_check_{j + 1}",
                            "",
                        )

                        st.session_state[
                            f"nueva_tarea_check_{j}"
                        ] = anterior

                    st.session_state.pop(
                        f"nueva_tarea_check_{cantidad - 1}",
                        None,
                    )

                    st.session_state.nueva_tarea_checklist_cantidad = max(
                        0,
                        cantidad - 1,
                    )

                    st.rerun()

        # ==================================================
        # BOTÓN AÑADIR CHECKLIST
        # ==================================================

        agregar_checklist = st.form_submit_button(
            "＋ Añadir checklist",
            use_container_width=True,
        )

        if agregar_checklist:
            st.session_state.nueva_tarea_checklist_cantidad += 1
            st.rerun()

        # ==================================================
        # CREAR TAREA
        # ==================================================

        enviar = st.form_submit_button(
            "Crear tarea",
            type="primary",
            use_container_width=True,
        )

        if enviar:

            # Eliminamos casillas vacías.
            subtareas_nuevas = [
                texto.strip()
                for texto in subtareas_nuevas
                if texto.strip()
            ]

            if not titulo.strip():

                st.error(
                    "El título de la tarea es obligatorio."
                )

            else:

                crear_tarea(
                    titulo=titulo.strip(),

                    # Ya no utilizamos descripción.
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

                # Reiniciar el editor de checklist
                # después de crear la tarea.
                st.session_state.nueva_tarea_checklist_cantidad = 1

                for key in list(st.session_state.keys()):
                    if key.startswith("nueva_tarea_check_"):
                        del st.session_state[key]

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

        st.caption(
            f"Entrega: {tarea.get('fecha_entrega') or 'Sin fecha'} · "
            f"Prioridad: {tarea['prioridad']} · "
            f"Avance global: {tarea['avance']}%"
        )

        if tarea.get("descripcion"):
            st.write(tarea["descripcion"])

        st.markdown(
            "**Responsables:** "
            + nombres_responsables(
                tarea.get("responsables_ids", [])
            )
        )

        st.progress(
            tarea["avance"] / 100,
            text=f"Avance global: {tarea['avance']}%",
        )

        # Mostrar avance individual.
        if tarea.get("responsables_ids"):
            st.markdown("**Avance individual**")

            for integrante_id in tarea["responsables_ids"]:
                nombre = nombres.get(
                    integrante_id,
                    "Sin asignar",
                )
                avance = tarea["progreso_individual"].get(
                    integrante_id,
                    0,
                )

                st.caption(
                    f"{nombre}: {avance}%"
                )
                st.progress(
                    avance / 100,
                    text=f"{nombre} · {avance}%",
                )

        with st.expander(
            "✏️ Editar tarea",
            expanded=False,
        ):
            titulo_editado = st.text_input(
                "Título",
                value=tarea["titulo"],
                key=f"titulo_{tarea['id']}",
            )

            descripcion_editada = st.text_area(
                "Descripción",
                value=tarea.get("descripcion", ""),
                key=f"descripcion_{tarea['id']}",
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
                help=(
                    "Puedes agregar o quitar responsables."
                ),
            )

            fecha_editada = st.date_input(
                "Fecha de entrega",
                value=(
                    __import__("datetime")
                    .datetime.strptime(
                        tarea["fecha_entrega"],
                        "%Y-%m-%d",
                    ).date()
                    if tarea.get("fecha_entrega")
                    else None
                ),
                format="DD/MM/YYYY",
                key=f"fecha_{tarea['id']}",
            )

            prioridades = ["Baja", "Media", "Alta"]
            prioridad_actual = tarea.get(
                "prioridad",
                "Baja",
            )

            prioridad_editada = st.selectbox(
                "Prioridad",
                prioridades,
                index=(
                    prioridades.index(prioridad_actual)
                    if prioridad_actual in prioridades
                    else 0
                ),
                key=f"prioridad_{tarea['id']}",
            )

            st.markdown("**Checklist de la tarea**")
            st.caption(
                "Cada responsable tendrá una copia independiente "
                "de estas casillas."
            )

            actuales = tarea.get("subtareas", [])

            textos_base = {}

            for integrante_id in responsables_editados:
                propias = [
                    sub
                    for sub in actuales
                    if sub.get("integrante_id") == integrante_id
                ]

                st.markdown(
                    f"**{nombres[integrante_id]}**"
                )

                if propias:
                    for sub in propias:
                        texto = st.text_input(
                            "Descripción de la casilla",
                            value=sub.get("texto", ""),
                            key=(
                                f"subtexto_"
                                f"{tarea['id']}_"
                                f"{integrante_id}_"
                                f"{sub['id']}"
                            ),
                        )

                        marcada = st.checkbox(
                            "Completada",
                            value=bool(
                                sub.get("completada")
                            ),
                            key=(
                                f"subcheck_"
                                f"{tarea['id']}_"
                                f"{integrante_id}_"
                                f"{sub['id']}"
                            ),
                        )

                        textos_base.setdefault(
                            integrante_id,
                            [],
                        ).append(
                            {
                                "id": sub["id"],
                                "texto": texto,
                                "completada": marcada,
                            }
                        )
                else:
                    texto = st.text_input(
                        "Nueva casilla",
                        key=(
                            f"nueva_sub_"
                            f"{tarea['id']}_"
                            f"{integrante_id}"
                        ),
                    )

                    if texto:
                        textos_base.setdefault(
                            integrante_id,
                            [],
                        ).append(
                            {
                                "id": None,
                                "texto": texto,
                                "completada": False,
                            }
                        )

            if responsables_editados:
                st.markdown(
                    "Añadir una nueva casilla a todos los responsables"
                )

                nueva_casilla = st.text_input(
                    "Nueva casilla",
                    key=f"nueva_casilla_{tarea['id']}",
                    placeholder="Ej.: Probar funcionamiento",
                )

                if nueva_casilla.strip():
                    for integrante_id in responsables_editados:
                        textos_base.setdefault(
                            integrante_id,
                            [],
                        ).append(
                            {
                                "id": None,
                                "texto": nueva_casilla,
                                "completada": False,
                            }
                        )

            guardar, eliminar = st.columns([4, 1])

            if guardar.button(
                "Guardar cambios",
                key=f"guardar_{tarea['id']}",
                type="primary",
                use_container_width=True,
            ):
                actualizar_tarea(
                    tarea_id=tarea["id"],
                    titulo=titulo_editado,
                    descripcion=descripcion_editada,
                    responsables_ids=responsables_editados,
                    fecha_entrega=(
                        fecha_editada.isoformat()
                        if fecha_editada
                        else None
                    ),
                    prioridad=prioridad_editada,
                    subtareas_por_integrante=textos_base,
                )

                st.success(
                    "Tarea actualizada correctamente."
                )
                st.rerun()

            if eliminar.button(
                "Eliminar",
                key=f"eliminar_{tarea['id']}",
                use_container_width=True,
            ):
                eliminar_tarea(tarea["id"])
                st.rerun()
