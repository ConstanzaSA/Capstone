from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from servicios.almacenamiento import (
    actualizar_fila,
    cargar_filas,
    eliminar_fila,
    insertar_fila,
    obtener_fila,
)


def ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def obtener_inventario() -> list[dict[str, Any]]:
    return cargar_filas("inventario", "material")


def crear_material(
    material: str,
    cantidad: float,
    unidad: str,
    disponible: bool,
    observaciones: str,
) -> None:
    material = material.strip()
    if not material:
        raise ValueError("El nombre del material es obligatorio.")

    insertar_fila(
        "inventario",
        {
            "id": uuid4().hex,
            "material": material,
            "cantidad": cantidad,
            "unidad": unidad.strip(),
            "disponible": disponible,
            "observaciones": observaciones.strip(),
            "fecha_actualizacion": ahora(),
        },
    )


def actualizar_material(
    material_id: str,
    material: str,
    cantidad: float,
    unidad: str,
    disponible: bool,
    observaciones: str,
) -> None:
    actualizar_fila(
        "inventario",
        "id",
        material_id,
        {
            "material": material.strip(),
            "cantidad": cantidad,
            "unidad": unidad.strip(),
            "disponible": disponible,
            "observaciones": observaciones.strip(),
            "fecha_actualizacion": ahora(),
        },
    )


def eliminar_material(material_id: str) -> None:
    eliminar_fila("inventario", "id", material_id)
