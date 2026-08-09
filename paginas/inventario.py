from __future__ import annotations

import streamlit as st

from componentes.interfaz import encabezado
from servicios.gestor_inventario import (
    actualizar_material,
    crear_material,
    eliminar_material,
    obtener_inventario,
)

encabezado("Inventario", "Material disponible actualmente para el equipo")

with st.expander("➕ Añadir material", expanded=True):
    with st.form("formulario_nuevo_material", clear_on_submit=True):
        col1, col2, col3 = st.columns([2.2, 1, 1])
        material = col1.text_input("Material")
        cantidad = col2.number_input("Cantidad", min_value=0.0, value=1.0, step=1.0)
        unidad = col3.text_input("Unidad", placeholder="unidades, m, kg...")

        col4, col5 = st.columns([1, 3])
        disponible = col4.checkbox("Disponible", value=True)
        observaciones = col5.text_input("Observaciones")

        guardar = st.form_submit_button(
            "Añadir al inventario",
            type="primary",
            use_container_width=True,
        )

        if guardar:
            try:
                crear_material(material, cantidad, unidad, disponible, observaciones)
                st.success("Material añadido al inventario.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))

st.subheader("Material disponible")

inventario = obtener_inventario()

if not inventario:
    st.info("Todavía no hay materiales registrados.")

for item in inventario:
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2.2, 1, 1.2, 1])

        nuevo_material = col1.text_input(
            "Material",
            item.get("material", ""),
            key=f"material_{item['id']}",
        )
        nueva_cantidad = col2.number_input(
            "Cantidad",
            min_value=0.0,
            value=float(item.get("cantidad") or 0),
            step=1.0,
            key=f"cantidad_{item['id']}",
        )
        nueva_unidad = col3.text_input(
            "Unidad",
            item.get("unidad", ""),
            key=f"unidad_{item['id']}",
        )
        nuevo_estado = col4.checkbox(
            "Disponible",
            value=bool(item.get("disponible", True)),
            key=f"disponible_{item['id']}",
        )

        nuevas_observaciones = st.text_input(
            "Observaciones",
            item.get("observaciones", ""),
            key=f"observaciones_{item['id']}",
        )

        guardar_col, eliminar_col = st.columns([4, 1])

        if guardar_col.button(
            "Guardar cambios",
            key=f"guardar_material_{item['id']}",
            type="primary",
            use_container_width=True,
        ):
            actualizar_material(
                item["id"],
                nuevo_material,
                nueva_cantidad,
                nueva_unidad,
                nuevo_estado,
                nuevas_observaciones,
            )
            st.success("Material actualizado.")
            st.rerun()

        if eliminar_col.button(
            "Eliminar",
            key=f"eliminar_material_{item['id']}",
            use_container_width=True,
        ):
            eliminar_material(item["id"])
            st.rerun()
