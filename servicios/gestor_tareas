from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from typing import Any

from servicios.almacenamiento import cargar_datos, guardar_datos


def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def obtener_integrantes() -> list[dict[str, Any]]:
    return cargar_datos("integrantes")


def guardar_integrantes(integrantes: list[dict[str, Any]]) -> None:
    guardar_datos("integrantes", integrantes, "Actualiza integrantes del equipo")


def obtener_tareas() -> list[dict[str, Any]]:
    return cargar_datos("tareas")


def obtener_historial() -> list[dict[str, Any]]:
    return cargar_datos("historial")


def _registrar_historial(accion: str, tarea: dict[str, Any], detalle: str) -> None:
    historial = obtener_historial()
    historial.insert(0, {
        "fecha": ahora(),
        "accion": accion,
        "tarea_id": tarea["id"],
        "tarea": tarea["titulo"],
        "detalle": detalle,
    })
    guardar_datos("historial", historial[:500], f"Registra historial: {accion}")


def crear_tarea(titulo: str, descripcion: str, responsable_id: str, semana: str, prioridad: str) -> None:
    tareas = obtener_tareas()
    tarea = {
        "id": uuid4().hex,
        "titulo": titulo.strip(),
        "descripcion": descripcion.strip(),
        "responsable_id": responsable_id,
        "semana": semana.strip(),
        "prioridad": prioridad,
        "estado": "Pendiente",
        "avance": 0,
        "fecha_creacion": ahora(),
        "fecha_actualizacion": ahora(),
    }
    tareas.append(tarea)
    guardar_datos("tareas", tareas, f"Crea tarea: {tarea['titulo']}")
    _registrar_historial("Creación", tarea, f"Asignada a {responsable_id}")


def actualizar_tarea(tarea_id: str, estado: str, avance: int, responsable_id: str) -> None:
    tareas = obtener_tareas()
    tarea = next(t for t in tareas if t["id"] == tarea_id)
    responsable_anterior = tarea["responsable_id"]
    estado_anterior = tarea["estado"]
    avance_anterior = tarea["avance"]

    tarea["responsable_id"] = responsable_id
    tarea["estado"] = estado
    tarea["avance"] = max(0, min(100, int(avance)))
    if estado == "Completada":
        tarea["avance"] = 100
    elif tarea["avance"] == 100:
        tarea["estado"] = "Completada"
    tarea["fecha_actualizacion"] = ahora()

    guardar_datos("tareas", tareas, f"Actualiza tarea: {tarea['titulo']}")

    cambios = []
    if responsable_anterior != responsable_id:
        cambios.append(f"Responsable: {responsable_anterior} → {responsable_id}")
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
        asignadas = [t for t in tareas if t["responsable_id"] == integrante["id"]]
        promedio = round(sum(t["avance"] for t in asignadas) / len(asignadas), 1) if asignadas else 0
        resultado.append({
            "Integrante": integrante["nombre"],
            "Rol": integrante["rol"],
            "Tareas": len(asignadas),
            "Completadas": sum(t["estado"] == "Completada" for t in asignadas),
            "Avance (%)": promedio,
        })
    return resultado
