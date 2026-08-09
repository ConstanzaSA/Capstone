from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from servicios.almacenamiento import (
    actualizar_fila,
    cargar_filas,
    eliminar_fila,
    insertar_fila,
)


def ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ==========================================================
# INVENTARIO
# ==========================================================

def obtener_inventario() -> list[dict[str, Any]]:
    """
    Obtiene todos los materiales registrados.
    Se ordenan alfabéticamente por material.
    """
    return cargar_filas("inventario", "material")


def obtener_integrantes() -> list[dict[str, Any]]:
    """
    Obtiene los integrantes disponibles para asignar
    como responsables/dueños de un material.
    """
    return cargar_filas("integrantes", "nombre")


def crear_material(
    material: str,
    responsable_id: str | None,
    unidad: str,
    disponible: bool,
    observaciones: str,
) -> None:
    """
    Crea un nuevo material en el inventario.
    """

    material = material.strip()

    if not material:
        raise ValueError(
            "El nombre del material es obligatorio."
        )

    insertar_fila(
        "inventario",
        {
            "id": uuid4().hex,
            "material": material,
            "responsable_id": responsable_id,
            "cantidad": 0,
            "unidad": unidad.strip(),
            "disponible": disponible,
            "observaciones": observaciones.strip(),
            "fecha_actualizacion": ahora(),
        },
    )


def actualizar_material(
    material_id: str,
    material: str,
    responsable_id: str | None,
    unidad: str,
    disponible: bool,
    observaciones: str,
) -> None:
    """
    Actualiza un material existente.
    """

    material = material.strip()

    if not material:
        raise ValueError(
            "El nombre del material es obligatorio."
        )

    actualizar_fila(
        "inventario",
        "id",
        material_id,
        {
            "material": material,
            "responsable_id": responsable_id,
            "unidad": unidad.strip(),
            "disponible": disponible,
            "observaciones": observaciones.strip(),
            "fecha_actualizacion": ahora(),
        },
    )


def eliminar_material(material_id: str) -> None:
    """
    Elimina definitivamente un material.
    """

    eliminar_fila(
        "inventario",
        "id",
        material_id,
    )

def agregar_stock(
    material: str,
    cantidad: float,
    unidad: str,
    responsable_id: str | None = None,
    observaciones: str = "",
) -> None:
    """
    Agrega una cantidad de un material al inventario.

    Si el material ya existe, aumenta su cantidad.
    Si no existe, crea un nuevo registro.
    """

    material = material.strip()

    if not material:
        raise ValueError(
            "El nombre del material es obligatorio."
        )

    if cantidad <= 0:
        raise ValueError(
            "La cantidad debe ser mayor que 0."
        )

    inventario = obtener_inventario()

    # Buscar si el material ya existe
    existente = next(
        (
            item
            for item in inventario
            if item.get("material", "").strip().lower()
            == material.lower()
        ),
        None,
    )

    # ======================================================
    # MATERIAL YA EXISTENTE
    # ======================================================

    if existente:

        cantidad_actual = float(
            existente.get("cantidad") or 0
        )

        actualizar_fila(
            "inventario",
            "id",
            existente["id"],
            {
                "cantidad": (
                    cantidad_actual
                    + cantidad
                ),
                "responsable_id": (
                    responsable_id
                    if responsable_id is not None
                    else existente.get(
                        "responsable_id"
                    )
                ),
                "disponible": True,
                "fecha_actualizacion": ahora(),
            },
        )

    # ======================================================
    # MATERIAL NUEVO
    # ======================================================

    else:

        insertar_fila(
            "inventario",
            {
                "id": uuid4().hex,
                "material": material,
                "responsable_id": responsable_id,
                "cantidad": cantidad,
                "unidad": unidad.strip(),
                "disponible": True,
                "observaciones": observaciones.strip(),
                "fecha_actualizacion": ahora(),
            },
        )


def agregar_stock_compra(
    compra_id: str,
    material: str,
    cantidad: float,
    responsable_id: str | None,
) -> None:
    """
    Añade al inventario un material proveniente
    de una compra.

    La compra queda identificada mediante
    una observación interna.
    """

    material = material.strip()

    if not material:
        raise ValueError(
            "El nombre del material es obligatorio."
        )

    if cantidad <= 0:
        raise ValueError(
            "La cantidad debe ser mayor que 0."
        )

    inventario = obtener_inventario()

    marca_compra = f"Compra:{compra_id}"

    # Buscar si esta compra ya fue añadida
    existente = next(
        (
            item
            for item in inventario
            if item.get("observaciones", "")
            == marca_compra
        ),
        None,
    )

    if existente:

        actualizar_fila(
            "inventario",
            "id",
            existente["id"],
            {
                "material": material,
                "cantidad": cantidad,
                "responsable_id": responsable_id,
                "disponible": True,
                "observaciones": marca_compra,
                "fecha_actualizacion": ahora(),
            },
        )

    else:

        insertar_fila(
            "inventario",
            {
                "id": uuid4().hex,
                "material": material,
                "responsable_id": responsable_id,
                "cantidad": cantidad,
                "unidad": "unidades",
                "disponible": True,
                "observaciones": marca_compra,
                "fecha_actualizacion": ahora(),
            },
        )


def eliminar_stock_compra(
    compra_id: str,
) -> None:
    """
    Elimina del inventario el material asociado
    a una compra específica.
    """

    inventario = obtener_inventario()

    marca_compra = f"Compra:{compra_id}"

    existente = next(
        (
            item
            for item in inventario
            if item.get("observaciones", "")
            == marca_compra
        ),
        None,
    )

    if existente:

        eliminar_material(
            existente["id"]
        )
