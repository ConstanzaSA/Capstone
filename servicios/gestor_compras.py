from __future__ import annotations

from typing import Any
from uuid import uuid4

from servicios.almacenamiento import (
    cargar_filas,
    insertar_fila,
    actualizar_fila,
    eliminar_fila,
)


# ==========================================================
# OBTENER COMPRAS
# ==========================================================

def obtener_compras() -> list[dict[str, Any]]:
    """
    Obtiene todas las compras registradas.
    """
    return cargar_filas(
        "compras",
        "nombre_compra",
    )


# ==========================================================
# CREAR COMPRA
# ==========================================================

def crear_compra(
    nombre_compra: str,
    cantidad: float,
    link: str,
    precio: float,
    comprador: str | None,
    estado: str,
) -> None:

    nombre_compra = nombre_compra.strip()

    if not nombre_compra:
        raise ValueError(
            "El nombre de la compra es obligatorio."
        )

    if cantidad <= 0:
        raise ValueError(
            "La cantidad debe ser mayor que 0."
        )

    if precio < 0:
        raise ValueError(
            "El precio no puede ser negativo."
        )

    insertar_fila(
        "compras",
        {
            "id": uuid4().hex,
            "nombre_compra": nombre_compra,
            "cantidad": cantidad,
            "link": link.strip(),
            "precio": precio,
            "comprador": comprador,
            "estado": estado,
        },
    )


# ==========================================================
# ACTUALIZAR COMPRA
# ==========================================================

def actualizar_compra(
    compra_id: str,
    nombre_compra: str,
    cantidad: float,
    link: str,
    precio: float,
    comprador: str | None,
    estado: str,
) -> None:

    nombre_compra = nombre_compra.strip()

    if not nombre_compra:
        raise ValueError(
            "El nombre de la compra es obligatorio."
        )

    if cantidad <= 0:
        raise ValueError(
            "La cantidad debe ser mayor que 0."
        )

    if precio < 0:
        raise ValueError(
            "El precio no puede ser negativo."
        )

    actualizar_fila(
        "compras",
        "id",
        compra_id,
        {
            "nombre_compra": nombre_compra,
            "cantidad": cantidad,
            "link": link.strip(),
            "precio": precio,
            "comprador": comprador,
            "estado": estado,
        },
    )


# ==========================================================
# ELIMINAR COMPRA
# ==========================================================

def eliminar_compra(
    compra_id: str,
) -> None:

    eliminar_fila(
        "compras",
        "id",
        compra_id,
    )
