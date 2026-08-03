from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from servicios.almacenamiento import cargar_datos, guardar_datos


def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def obtener_integrantes() -> list[dict[str, Any]]:
    return cargar_datos("integrantes")


def guardar_integrantes(integrantes: list[dict[str, Any]]) -> None:
    guardar_datos("integrantes", integrantes, "Actualiza integrantes del equipo")


def obtener_tareas() -> list[dict[str, Any]]:
    tareas = cargar_datos("tareas")
    # Compatibilidad con tareas creadas por la versión anterior.
    for tarea in tareas:
        tarea.setdefault("responsable_id", None)
        tarea.setdefault("fecha_entrega", "")
        if not tarea["fecha_entrega"] and tarea.get("semana"):
            tarea["fecha_entrega"] = tarea["semana"]
    return tareas


def obtener_historial() -> list[dict[str, Any]]:
    return cargar_datos("historial")


def obtener_configuracion() -> dict[str, Any]:
    configuracion = cargar_datos("configuracion")
    configuracion.setdefault("nombre_proyecto", "Capstone Robótica")
    configuracion.setdefault("proxima_entrega", "")
    return configuracion


def guardar_configuracion(configuracion: dict[str, Any]) -> None:
    guardar_datos("configuracion", configuracion, "Actualiza configuración del proyecto")


def _registrar_historial(accion: str, tarea: dict[str, Any], detalle: str) -> None:
    historial = obtener_historial()
    historial.insert(
        0,
        {
            "fecha": ahora(),
            "accion": accion,
            "tarea_id": tarea["id"],
            "tarea": tarea["titulo"],
            "detalle": detalle,
        },
    )
    guardar_datos("historial", historial[:500], f"Registra historial: {accion}")


def crear_tarea(
    titulo: str,
    descripcion: str,
    responsable_id: str | None,
    fecha_entrega: str,
    prioridad: str,
) -> None:
    tareas = obtener_tareas()
    tarea = {
        "id": uuid4().hex,
        "titulo": titulo.strip(),
        "descripcion": descripcion.strip(),
        "responsable_id": responsable_id,
        "fecha_entrega": fecha_entrega,
        "prioridad": prioridad,
        "estado": "Pendiente",
        "avance": 0,
        "fecha_creacion": ahora(),
        "fecha_actualizacion": ahora(),
    }
    tareas.append(tarea)
    guardar_datos("tareas", tareas, f"Crea tarea: {tarea['titulo']}")
    asignacion = responsable_id or "Sin asignar"
    _registrar_historial("Creación", tarea, f"Responsable: {asignacion}")


def actualizar_tarea(
    tarea_id: str,
    estado: str,
    avance: int,
    responsable_id: str | None,
    fecha_entrega: str,
) -> None:
    tareas = obtener_tareas()
    tarea = next(t for t in tareas if t["id"] == tarea_id)
    responsable_anterior = tarea.get("responsable_id")
    estado_anterior = tarea["estado"]
    avance_anterior = tarea["avance"]
    entrega_anterior = tarea.get("fecha_entrega", "")

    tarea["responsable_id"] = responsable_id
    tarea["fecha_entrega"] = fecha_entrega
    tarea["estado"] = estado
    tarea["avance"] = max(0, min(100, int(avance)))

    if estado == "Completada":
        tarea["avance"] = 100
    elif tarea["avance"] == 100:
        tarea["estado"] = "Completada"

    tarea["fecha_actualizacion"] = ahora()
    tarea.pop("semana", None)
    guardar_datos("tareas", tareas, f"Actualiza tarea: {tarea['titulo']}")

    cambios = []
    if responsable_anterior != responsable_id:
        cambios.append(
            f"Responsable: {responsable_anterior or 'Sin asignar'} → "
            f"{responsable_id or 'Sin asignar'}"
        )
    if entrega_anterior != fecha_entrega:
        cambios.append(f"Fecha de entrega: {entrega_anterior or 'Sin fecha'} → {fecha_entrega}")
    if estado_anterior != tarea["estado"]:
        cambios.append(f"Estado: {estado_anterior} → {tarea['estado']}")
    if avance_anterior != tarea["avance"]:
        cambios.append(f"Avance: {avance_anterior}% → {tarea['avance']}%")
    _registrar_historial("Actualización", tarea, "; ".join(cambios) or "Sin cambios")


def eliminar_tarea(tarea_id: str) -> None:
    tareas = obtener_tareas()
    tarea = next(t for t in tareas if t["id"] == tarea_id)
    tareas = [t for t in tareas if t["id"] != tarea_id]
    guardar_datos("tareas", tareas, f"Elimina tarea: {tarea['titulo']}")
    _registrar_historial("Eliminación", tarea, "Tarea eliminada")


def avance_por_integrante() -> list[dict[str, Any]]:
    integrantes = obtener_integrantes()
    tareas = obtener_tareas()
    resultado = []
    for integrante in integrantes:
        asignadas = [t for t in tareas if t.get("responsable_id") == integrante["id"]]
        promedio = (
            round(sum(t["avance"] for t in asignadas) / len(asignadas), 1)
            if asignadas
            else 0
        )
        resultado.append(
            {
                "Integrante": integrante["nombre"],
                "Rol": integrante["rol"],
                "Tareas": len(asignadas),
                "Completadas": sum(t["estado"] == "Completada" for t in asignadas),
                "Avance (%)": promedio,
            }
        )
    return resultado
