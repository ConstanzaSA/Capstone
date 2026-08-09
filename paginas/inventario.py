from __future__ import annotations

import streamlit as st

from componentes.interfaz import encabezado
from servicios.gestor_inventario import (
    actualizar_material,
    crear_material,
    eliminar_material,
    obtener_inventario,
    obtener_integrantes,
)


# ==========================================================
# ENCABEZADO
# ==========================================================

encabezado(
    "Inventario",
    "Material disponible actualmente para el equipo",
)


# ==========================================================
# DATOS
# ==========================================================

inventario = obtener_inventario()
integrantes = obtener_integrantes()


nombres_integrantes = {
    integrante["id"]: integrante["nombre"]
    for integrante in integrantes
}


ids_integrantes = list(
    nombres_integrantes.keys()
)


# ==========================================================
# AÑADIR MATERIAL
# ==========================================================

with st.expander(
    "➕ Añadir material",
    expanded=True,
):

    with st.form(
        "formulario_nuevo_material",
        clear_on_submit=True,
    ):

        col1, col2 = st.columns(2)

        # --------------------------------------------------
        # MATERIAL
        # --------------------------------------------------

        material = col1.text_input(
            "Material",
            placeholder="Ej.: Motor DC",
        )

        # --------------------------------------------------
        # RESPONSABLE / DUEÑO
        # --------------------------------------------------

        responsable_id = col2.selectbox(
            "Responsable / dueño",
            options=[None] + ids_integrantes,
            format_func=lambda x: (
                "Sin asignar"
                if x is None
                else nombres_integrantes[x]
            ),
            help=(
                "Integrante que actualmente tiene "
                "o es dueño de este material."
            ),
        )

        # --------------------------------------------------
        # UNIDAD
        # --------------------------------------------------

        col3, col4 = st.columns(2)

        unidad = col3.text_input(
            "Unidad",
            placeholder="Ej.: unidades, m, kg...",
        )

        disponible = col4.checkbox(
            "Disponible",
            value=True,
        )

        # --------------------------------------------------
        # OBSERVACIONES
        # --------------------------------------------------

        observaciones = st.text_input(
            "Observaciones",
            placeholder="Información adicional del material...",
        )

        guardar = st.form_submit_button(
            "Añadir al inventario",
            type="primary",
            use_container_width=True,
        )

        if guardar:

            try:

                crear_material(
                    material=material,
                    responsable_id=responsable_id,
                    unidad=unidad,
                    disponible=disponible,
                    observaciones=observaciones,
                )

                st.success(
                    "Material añadido al inventario."
                )

                st.rerun()

            except ValueError as error:

                st.error(str(error))

# ==========================================================
# MODIFICAR INVENTARIO
# ==========================================================

if inventario:

    with st.expander(
        "✏️ Modificar inventario",
        expanded=False,
    ):

        opciones_material = {
            item["id"]: item["material"]
            for item in inventario
        }

        material_id = st.selectbox(
            "Seleccionar material",
            options=list(
                opciones_material.keys()
            ),
            format_func=lambda x: opciones_material[x],
        )

        material_seleccionado = next(
            (
                item
                for item in inventario
                if item["id"] == material_id
            ),
            None,
        )

        if material_seleccionado:

            st.markdown(
                "### Datos del material"
            )

            col1, col2 = st.columns(2)

            # --------------------------------------------------
            # MATERIAL
            # --------------------------------------------------

            nuevo_material = col1.text_input(
                "Material",
                value=material_seleccionado.get(
                    "material",
                    "",
                ),
                key=f"editar_material_{material_id}",
            )

            # --------------------------------------------------
            # RESPONSABLE
            # --------------------------------------------------

            responsable_actual = (
                material_seleccionado.get(
                    "responsable_id"
                )
            )

            opciones_responsable = (
                [None] + ids_integrantes
            )

            if (
                responsable_actual
                not in opciones_responsable
            ):
                responsable_actual = None

            nuevo_responsable = col2.selectbox(
                "Responsable / dueño",
                options=opciones_responsable,
                index=opciones_responsable.index(
                    responsable_actual
                ),
                format_func=lambda x: (
                    "Sin asignar"
                    if x is None
                    else nombres_integrantes[x]
                ),
                key=(
                    f"editar_responsable_"
                    f"{material_id}"
                ),
            )

            # --------------------------------------------------
            # UNIDAD
            # --------------------------------------------------

            col3, col4 = st.columns(2)

            nueva_unidad = col3.text_input(
                "Unidad",
                value=material_seleccionado.get(
                    "unidad",
                    "",
                ),
                key=f"editar_unidad_{material_id}",
            )

            nuevo_estado = col4.checkbox(
                "Disponible",
                value=bool(
                    material_seleccionado.get(
                        "disponible",
                        True,
                    )
                ),
                key=(
                    f"editar_disponible_"
                    f"{material_id}"
                ),
            )

            # --------------------------------------------------
            # OBSERVACIONES
            # --------------------------------------------------

            nuevas_observaciones = st.text_input(
                "Observaciones",
                value=material_seleccionado.get(
                    "observaciones",
                    "",
                ),
                key=(
                    f"editar_observaciones_"
                    f"{material_id}"
                ),
            )

            st.markdown("")

            guardar_col, eliminar_col = st.columns(
                [4, 1]
            )

            # ==================================================
            # GUARDAR
            # ==================================================

            if guardar_col.button(
                "Guardar cambios",
                key=(
                    f"guardar_material_"
                    f"{material_id}"
                ),
                type="primary",
                use_container_width=True,
            ):

                try:

                    actualizar_material(
                        material_id=material_id,
                        material=nuevo_material,
                        responsable_id=(
                            nuevo_responsable
                        ),
                        unidad=nueva_unidad,
                        disponible=nuevo_estado,
                        observaciones=(
                            nuevas_observaciones
                        ),
                    )

                    st.success(
                        "Material actualizado."
                    )

                    st.rerun()

                except ValueError as error:

                    st.error(str(error))

            # ==================================================
            # ELIMINAR
            # ==================================================

            if eliminar_col.button(
                "Eliminar",
                key=(
                    f"eliminar_material_"
                    f"{material_id}"
                ),
                use_container_width=True,
            ):

                eliminar_material(
                    material_id
                )

                st.success(
                    "Material eliminado."
                )

                st.rerun()


# ==========================================================
# MATERIAL DISPONIBLE
# ==========================================================

st.subheader("Material disponible")


if not inventario:

    st.info(
        "Todavía no hay materiales registrados."
    )

else:

    filas_tabla = []

    for item in inventario:

        responsable = nombres_integrantes.get(
            item.get("responsable_id"),
            "Sin asignar",
        )

        filas_tabla.append(
            {
                "Material": item.get(
                    "material",
                    "",
                ),
                "Responsable / dueño": responsable,
                "Unidad": item.get(
                    "unidad",
                    "",
                ),
                "Disponible": (
                    "Sí"
                    if item.get(
                        "disponible",
                        True,
                    )
                    else "No"
                ),
                "Observaciones": item.get(
                    "observaciones",
                    "",
                ),
            }
        )

    st.dataframe(
        filas_tabla,
        use_container_width=True,
        hide_index=True,
    )


