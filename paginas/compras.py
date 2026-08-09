from __future__ import annotations

import streamlit as st

from componentes.interfaz import encabezado

from servicios.gestor_compras import (
    obtener_compras,
    crear_compra,
    marcar_comprado,
    marcar_sin_comprar,
    actualizar_compra,
    eliminar_compra,
)

from servicios.gestor_tareas import (
    obtener_integrantes,
)

from servicios.gestor_inventario import (
    agregar_stock,
)


# ==========================================================
# ENCABEZADO
# ==========================================================

encabezado(
    "Compras",
    "Gestiona los materiales que el equipo necesita comprar",
)


# ==========================================================
# INTEGRANTES
# ==========================================================

integrantes = obtener_integrantes()

nombres = {
    integrante["id"]: integrante["nombre"]
    for integrante in integrantes
}

ids_integrantes = list(
    nombres.keys()
)


# ==========================================================
# AÑADIR COMPRA
# ==========================================================

with st.expander(
    "➕ Añadir una compra",
    expanded=True,
):

    with st.form(
        "formulario_nueva_compra",
        clear_on_submit=True,
    ):

        # --------------------------------------------------
        # NOMBRE
        # --------------------------------------------------

        nombre_compra = st.text_input(
            "Nombre de la compra",
            placeholder="Ej.: Motor DC 12V",
        )

        # --------------------------------------------------
        # CANTIDAD / PRECIO
        # --------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            cantidad = st.number_input(
                "Cantidad",
                min_value=1.0,
                value=1.0,
                step=1.0,
            )

        with col2:

            precio = st.number_input(
                "Precio",
                min_value=0.0,
                value=0.0,
                step=100.0,
            )

        # --------------------------------------------------
        # LINK
        # --------------------------------------------------

        link = st.text_input(
            "🔗 Link del producto",
            placeholder="https://...",
        )

        # --------------------------------------------------
        # CREAR
        # --------------------------------------------------

        crear = st.form_submit_button(
            "Añadir compra",
            type="primary",
            use_container_width=True,
        )

        if crear:

            try:

                crear_compra(
                    nombre_compra,
                    cantidad,
                    link,
                    precio,
                )

                st.success(
                    "Compra añadida correctamente."
                )

                st.rerun()

            except ValueError as error:

                st.error(str(error))


# ==========================================================
# LISTA DE COMPRAS
# ==========================================================

st.subheader("Lista de compras")

compras = obtener_compras()


# ==========================================================
# SEPARAR ESTADOS
# ==========================================================

sin_comprar = [
    compra
    for compra in compras
    if compra.get("estado")
    == "Sin comprar"
]

compradas = [
    compra
    for compra in compras
    if compra.get("estado")
    == "Comprado"
]


# ==========================================================
# POR COMPRAR
# ==========================================================

st.markdown("### 🛒 Por comprar")

if not sin_comprar:

    st.info(
        "No hay compras pendientes."
    )

else:

    for compra in sin_comprar:

        with st.container(
            border=True
        ):

            st.markdown(
                f"### 🟡 "
                f"{compra['nombre_compra']}"
            )

            col1, col2, col3 = st.columns(
                [2, 1, 1]
            )

            with col1:

                st.write(
                    f"**Cantidad:** "
                    f"{compra['cantidad']}"
                )

            with col2:

                st.write(
                    f"**Precio:** "
                    f"${float(compra.get('precio', 0)):,.0f}"
                )

            with col3:

                st.write(
                    "**Estado:** Sin comprar"
                )

            if compra.get("link"):

                st.link_button(
                    "🔗 Ver producto",
                    compra["link"],
                )

            # --------------------------------------------------
            # REGISTRAR COMPRA
            # --------------------------------------------------

            if ids_integrantes:

                comprador = st.selectbox(
                    "¿Quién pagó?",
                    options=ids_integrantes,
                    format_func=lambda x: (
                        nombres[x]
                    ),
                    key=(
                        f"comprador_"
                        f"{compra['id']}"
                    ),
                )

                if st.button(
                    "🛒 Marcar como comprado",
                    key=(
                        f"comprar_"
                        f"{compra['id']}"
                    ),
                    type="primary",
                    use_container_width=True,
                ):

                    try:

                        # ------------------------------------------
                        # 1. MARCAR COMPRA
                        # ------------------------------------------

                        marcar_comprado(
                            compra["id"],
                            comprador,
                        )

                        # ------------------------------------------
                        # 2. AGREGAR AL INVENTARIO
                        # ------------------------------------------

                        agregar_stock(
                            material=(
                                compra[
                                    "nombre_compra"
                                ]
                            ),
                            cantidad=float(
                                compra[
                                    "cantidad"
                                ]
                            ),
                            unidad="unidades",
                            responsable_id=(
                                comprador
                            ),
                            observaciones=(
                                f"Compra "
                                f"#{compra['id']}"
                            ),
                        )

                        st.success(
                            "Compra registrada y "
                            "material añadido al inventario."
                        )

                        st.rerun()

                    except ValueError as error:

                        st.error(
                            str(error)
                        )

            else:

                st.warning(
                    "No hay integrantes registrados."
                )


# ==========================================================
# COMPRADAS
# ==========================================================

st.markdown("### 📦 Comprado")

if not compradas:

    st.info(
        "Todavía no hay compras realizadas."
    )

else:

    for compra in compradas:

        with st.container(
            border=True
        ):

            st.markdown(
                f"### 🟢 "
                f"{compra['nombre_compra']}"
            )

            col1, col2, col3 = st.columns(
                [2, 1, 1]
            )

            with col1:

                st.write(
                    f"**Cantidad:** "
                    f"{compra['cantidad']}"
                )

            with col2:

                st.write(
                    f"**Precio:** "
                    f"${float(compra.get('precio', 0)):,.0f}"
                )

            with col3:

                comprador_id = compra.get(
                    "comprador"
                )

                st.write(
                    "**Pagó:** "
                    + nombres.get(
                        comprador_id,
                        "Desconocido",
                    )
                )

            if compra.get("link"):

                st.link_button(
                    "🔗 Ver producto",
                    compra["link"],
                )

            st.success(
                "📦 Este material fue añadido al inventario."
            )

            # --------------------------------------------------
            # DESHACER
            # --------------------------------------------------

            if st.button(
                "↩️ Volver a Sin comprar",
                key=(
                    f"deshacer_"
                    f"{compra['id']}"
                ),
            ):

                marcar_sin_comprar(
                    compra["id"]
                )

                st.rerun()

            # --------------------------------------------------
            # EDITAR
            # --------------------------------------------------

            with st.expander(
                "✏️ Editar compra"
            ):

                nuevo_nombre = st.text_input(
                    "Nombre",
                    compra.get(
                        "nombre_compra",
                        "",
                    ),
                    key=(
                        f"nombre_edit_"
                        f"{compra['id']}"
                    ),
                )

                nueva_cantidad = st.number_input(
                    "Cantidad",
                    min_value=1.0,
                    value=float(
                        compra.get(
                            "cantidad",
                            1,
                        )
                    ),
                    step=1.0,
                    key=(
                        f"cantidad_edit_"
                        f"{compra['id']}"
                    ),
                )

                nuevo_precio = st.number_input(
                    "Precio",
                    min_value=0.0,
                    value=float(
                        compra.get(
                            "precio",
                            0,
                        )
                    ),
                    step=100.0,
                    key=(
                        f"precio_edit_"
                        f"{compra['id']}"
                    ),
                )

                nuevo_link = st.text_input(
                    "Link",
                    compra.get(
                        "link",
                        "",
                    ),
                    key=(
                        f"link_edit_"
                        f"{compra['id']}"
                    ),
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "Guardar cambios",
                        key=(
                            f"guardar_"
                            f"{compra['id']}"
                        ),
                        type="primary",
                        use_container_width=True,
                    ):

                        try:

                            actualizar_compra(
                                compra["id"],
                                nuevo_nombre,
                                nueva_cantidad,
                                nuevo_link,
                                nuevo_precio,
                            )

                            st.success(
                                "Compra actualizada."
                            )

                            st.rerun()

                        except ValueError as error:

                            st.error(
                                str(error)
                            )

                with col2:

                    if st.button(
                        "Eliminar",
                        key=(
                            f"eliminar_"
                            f"{compra['id']}"
                        ),
                        use_container_width=True,
                    ):

                        eliminar_compra(
                            compra["id"]
                        )

                        st.rerun()
