from __future__ import annotations

import streamlit as st

from componentes.interfaz import encabezado

from servicios.gestor_compras import (
    obtener_compras,
    crear_compra,
    actualizar_compra,
    eliminar_compra,
)

from servicios.gestor_tareas import (
    obtener_integrantes,
)

from servicios.gestor_inventario import (
    agregar_stock_compra,
    eliminar_stock_compra,
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
# COMPRAS EXISTENTES
# ==========================================================

compras = obtener_compras()


# ==========================================================
# CREAR COMPRA
# ==========================================================

with st.expander(
    "➕ Añadir compra",
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

        link = st.text_area(
        "Observaciones",
        placeholder=(
            "Pega aquí el link del producto u otra información "
            "importante sobre la compra."
        ),
        height=80,
    )
        # --------------------------------------------------
        # COMPRADOR
        # --------------------------------------------------

        opciones_comprador = [
            None
        ] + ids_integrantes

        comprador = st.selectbox(
            "Comprador",
            options=opciones_comprador,
            format_func=lambda x: (
                "Sin Definir"
                if x is None
                else nombres[x]
            ),
        )

        # --------------------------------------------------
        # ESTADO
        # --------------------------------------------------

        estado = st.selectbox(
            "Estado",
            [
                "Sin comprar",
                "Comprado",
            ],
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

                # Si está comprado pero no tiene
                # comprador, no permitirlo.

                if (
                    estado == "Comprado"
                    and comprador is None
                ):
                    st.error(
                        "Debes seleccionar quién "
                        "realizó la compra."
                    )

                else:

                    crear_compra(
                        nombre_compra=nombre_compra,
                        cantidad=cantidad,
                        link=link,
                        precio=precio,
                        comprador=comprador,
                        estado=estado,
                    )

                    # ------------------------------------------
                    # SI SE CREA COMO COMPRADO
                    # ------------------------------------------

                    if estado == "Comprado":

                        nueva_compra = obtener_compras()

                        compra_creada = next(
                            (
                                compra
                                for compra
                                in nueva_compra
                                if (
                                    compra[
                                        "nombre_compra"
                                    ]
                                    == nombre_compra.strip()
                                    and
                                    compra[
                                        "cantidad"
                                    ]
                                    == cantidad
                                )
                            ),
                            None,
                        )

                        if compra_creada:

                            agregar_stock_compra(
                                compra_creada["id"],
                                nombre_compra,
                                cantidad,
                                comprador,
                            )

                    st.success(
                        "Compra añadida correctamente."
                    )

                    st.rerun()

            except ValueError as error:

                st.error(str(error))


# ==========================================================
# EDITAR COMPRAS
# ==========================================================

with st.expander(
    "✏️ Editar compras",
    expanded=False,
):

    if not compras:

        st.info(
            "Todavía no hay compras para editar."
        )

    else:

        # --------------------------------------------------
        # SELECCIONAR COMPRA
        # --------------------------------------------------

        compra_id = st.selectbox(
            "Selecciona una compra",
            options=[
                compra["id"]
                for compra in compras
            ],
            format_func=lambda x: next(
                (
                    compra[
                        "nombre_compra"
                    ]
                    for compra in compras
                    if compra["id"] == x
                ),
                x,
            ),
        )

        compra = next(
            (
                item
                for item in compras
                if item["id"] == compra_id
            ),
            None,
        )

        if compra:

            st.divider()

            # --------------------------------------------------
            # NOMBRE
            # --------------------------------------------------

            nuevo_nombre = st.text_input(
                "Nombre de la compra",
                value=compra.get(
                    "nombre_compra",
                    "",
                ),
            )

            # --------------------------------------------------
            # CANTIDAD / PRECIO
            # --------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

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
                )

            with col2:

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
                )

            # --------------------------------------------------
            # LINK
            # --------------------------------------------------

            nuevo_link = st.text_area(
                "Observaciones",
                value=compra.get(
                    "link",
                    "",
                ),
                height=80,
            )
            # --------------------------------------------------
            # COMPRADOR
            # --------------------------------------------------

            comprador_actual = compra.get(
                "comprador"
            )

            opciones_comprador = [
                None
            ] + ids_integrantes

            if (
                comprador_actual
                not in opciones_comprador
            ):
                comprador_actual = None

            nuevo_comprador = st.selectbox(
                "Comprador",
                options=opciones_comprador,
                index=opciones_comprador.index(
                    comprador_actual
                ),
                format_func=lambda x: (
                    "Sin Definir"
                    if x is None
                    else nombres[x]
                ),
            )

            # --------------------------------------------------
            # ESTADO
            # --------------------------------------------------

            estado_actual = compra.get(
                "estado",
                "Sin comprar",
            )

            nuevo_estado = st.selectbox(
                "Estado",
                [
                    "Sin comprar",
                    "Comprado",
                ],
                index=(
                    1
                    if estado_actual
                    == "Comprado"
                    else 0
                ),
            )

            st.divider()

            # --------------------------------------------------
            # GUARDAR
            # --------------------------------------------------

            col1, col2 = st.columns(
                [3, 1]
            )

            with col1:

                guardar = st.button(
                    "Guardar cambios",
                    key=(
                        f"guardar_compra_"
                        f"{compra_id}"
                    ),
                    type="primary",
                    use_container_width=True,
                )

            with col2:

                eliminar = st.button(
                    "Eliminar",
                    key=(
                        f"eliminar_compra_"
                        f"{compra_id}"
                    ),
                    use_container_width=True,
                )

            # ==================================================
            # GUARDAR CAMBIOS
            # ==================================================

            if guardar:

                if (
                    nuevo_estado == "Comprado"
                    and nuevo_comprador is None
                ):

                    st.error(
                        "Debes seleccionar quién "
                        "realizó la compra."
                    )

                else:

                    estado_anterior = compra.get(
                        "estado",
                        "Sin comprar",
                    )

                    # ------------------------------------------
                    # ACTUALIZAR COMPRA
                    # ------------------------------------------

                    actualizar_compra(
                        compra_id=compra_id,
                        nombre_compra=nuevo_nombre,
                        cantidad=nueva_cantidad,
                        link=nuevo_link,
                        precio=nuevo_precio,
                        comprador=nuevo_comprador,
                        estado=nuevo_estado,
                    )

                    # ------------------------------------------
                    # SIN COMPRAR → COMPRADO
                    # ------------------------------------------

                    if (
                        nuevo_estado
                        == "Comprado"
                    ):

                        agregar_stock_compra(
                            compra_id,
                            nuevo_nombre,
                            nueva_cantidad,
                            nuevo_comprador,
                        )

                    # ------------------------------------------
                    # COMPRADO → SIN COMPRAR
                    # ------------------------------------------

                    elif (
                        nuevo_estado
                        == "Sin comprar"
                    ):

                        eliminar_stock_compra(
                            compra_id
                        )

                    st.success(
                        "Compra actualizada."
                    )

                    st.rerun()

            # ==================================================
            # ELIMINAR
            # ==================================================

            if eliminar:

                # Si estaba comprada, sacar
                # también del inventario.

                if (
                    compra.get("estado")
                    == "Comprado"
                ):

                    eliminar_stock_compra(
                        compra_id
                    )

                eliminar_compra(
                    compra_id
                )

                st.success(
                    "Compra eliminada."
                )

                st.rerun()


# ==========================================================
# LISTA DE COMPRAS
# ==========================================================

st.subheader("Lista de compras")

if not compras:

    st.info(
        "Todavía no hay compras registradas."
    )

else:

    datos_tabla = []

    for compra in compras:

        comprador_id = compra.get(
            "comprador"
        )

        comprador_nombre = (
            nombres.get(
                comprador_id,
                "Sin Definir",
            )
            if comprador_id
            else "Sin Definir"
        )

        estado = compra.get(
            "estado",
            "Sin comprar",
        )

        # Mostrar el estado de forma visual
        if estado == "Comprado":

            estado_mostrar = (
                "🟢 Comprado"
            )

        else:

            estado_mostrar = (
                "🟡 Sin comprar"
            )

        datos_tabla.append(
            {
                "Nombre": compra.get(
                    "nombre_compra",
                    "",
                ),

                "Precio": (
                    f"${float(
                        compra.get(
                            "precio",
                            0,
                        )
                    ):,.0f}"
                ),

                "Cantidad": compra.get(
                    "cantidad",
                    0,
                ),

                "Estado": estado_mostrar,

                "Comprador": comprador_nombre,

                "Observaciones": compra.get(
                    "link",
                    "",
                ),
            }
        )

    st.dataframe(
        datos_tabla,
        use_container_width=True,
        hide_index=True,
    )
