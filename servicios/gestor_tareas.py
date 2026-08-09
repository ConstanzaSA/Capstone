from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from servicios.almacenamiento import (
    cargar_filas,
    insertar_fila,
    actualizar_fila,
    eliminar_fila,
    obtener_cliente_supabase,
)


def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ==========================================================
# INTEGRANTES
# ==========================================================

def obtener_integrantes() -> list[dict[str, Any]]:
    return cargar_filas("integrantes", "fecha_actualizacion")


def crear_integrante(nombre: str, rol: str) -> dict[str, Any]:
    nombre = nombre.strip()
    rol = rol.strip()

    if not nombre:
        raise ValueError("El nombre del integrante es obligatorio.")

    return insertar_fila(
        "integrantes",
        {
            "id": f"integrante_{uuid4().hex}",
            "nombre": nombre,
            "rol": rol,
            "fecha_actualizacion": ahora(),
        },
    )


def actualizar_integrante(
    integrante_id: str,
    nombre: str,
    rol: str,
) -> dict[str, Any]:
    nombre = nombre.strip()
    rol = rol.strip()

    if not nombre:
        raise ValueError("El nombre del integrante es obligatorio.")

    return actualizar_fila(
        "integrantes",
        "id",
        integrante_id,
        {
            "nombre": nombre,
            "rol": rol,
            "fecha_actualizacion": ahora(),
        },
    )


# ==========================================================
# TAREAS Y SUBTAREAS
# ==========================================================

def _responsables_por_tarea() -> dict[str, list[str]]:
    relaciones = cargar_filas("tarea_integrantes")
    resultado: dict[str, list[str]] = {}

    for relacion in relaciones:
        resultado.setdefault(relacion["tarea_id"], []).append(
            relacion["integrante_id"]
        )

    return resultado


def _subtareas_por_tarea() -> dict[str, list[dict[str, Any]]]:
    """
    Las subtareas se guardan en la tabla 'subtareas'.

    Cada subtarea tiene:
      id, tarea_id, integrante_id, texto, completada,
      fecha_actualizacion

    La misma subtarea puede existir para distintos integrantes.
    """
    try:
        filas = cargar_filas("subtareas")
    except Exception:
        return {}

    resultado: dict[str, list[dict[str, Any]]] = {}

    for fila in filas:
        resultado.setdefault(fila["tarea_id"], []).append(fila)

    return resultado


def obtener_tareas() -> list[dict[str, Any]]:
    tareas = cargar_filas("tareas", "fecha_actualizacion")
    responsables = _responsables_por_tarea()
    subtareas = _subtareas_por_tarea()

    for tarea in tareas:
        ids = responsables.get(tarea["id"], [])

        if not ids and tarea.get("responsable_id"):
            ids = [tarea["responsable_id"]]

        tarea["responsables_ids"] = ids
        tarea["responsable_id"] = ids[0] if ids else None

        lista_subtareas = subtareas.get(tarea["id"], [])
        tarea["subtareas"] = lista_subtareas

        # Progreso individual.
        progreso_individual: dict[str, int] = {}

        for integrante_id in ids:
            propias = [
                sub
                for sub in lista_subtareas
                if sub.get("integrante_id") == integrante_id
            ]

            if propias:
                progreso_individual[integrante_id] = round(
                    100
                    * sum(
                        bool(sub.get("completada"))
                        for sub in propias
                    )
                    / len(propias)
                )
            else:
                progreso_individual[integrante_id] = 0

        tarea["progreso_individual"] = progreso_individual

        # El avance global de la tarea es el promedio de los
        # avances individuales de todos sus responsables.
        tarea["avance"] = (
            round(
                sum(progreso_individual.values())
                / len(progreso_individual)
            )
            if progreso_individual
            else 0
        )

        if tarea["avance"] == 100 and ids:
            tarea["estado"] = "Completada"
        elif tarea["avance"] > 0:
            tarea["estado"] = "En progreso"
        else:
            tarea["estado"] = "Pendiente"

        tarea.setdefault("descripcion", "")
        tarea.setdefault("fecha_entrega", None)
        tarea.setdefault("prioridad", "Baja")

    return tareas


def obtener_tarea(tarea_id: str) -> dict[str, Any] | None:
    return next(
        (tarea for tarea in obtener_tareas() if tarea["id"] == tarea_id),
        None,
    )


def _reemplazar_asignaciones(
    tarea_id: str,
    responsables_ids: list[str],
) -> None:
    actuales = [
        fila
        for fila in cargar_filas("tarea_integrantes")
        if fila["tarea_id"] == tarea_id
    ]

    for fila in actuales:
        (
            obtener_cliente_supabase()
            .table("tarea_integrantes")
            .delete()
            .eq("tarea_id", tarea_id)
            .eq("integrante_id", fila["integrante_id"])
            .execute()
        )

    for integrante_id in sorted(set(responsables_ids)):
        insertar_fila(
            "tarea_integrantes",
            {
                "tarea_id": tarea_id,
                "integrante_id": integrante_id,
                "fecha_asignacion": ahora(),
            },
        )


def _crear_subtareas_iniciales(
    tarea_id: str,
    responsables_ids: list[str],
    textos: list[str],
) -> None:
    textos_limpios = [
        texto.strip()
        for texto in textos
        if texto.strip()
    ]

    for integrante_id in responsables_ids:
        for texto in textos_limpios:
            insertar_fila(
                "subtareas",
                {
                    "id": uuid4().hex,
                    "tarea_id": tarea_id,
                    "integrante_id": integrante_id,
                    "texto": texto,
                    "completada": False,
                    "fecha_actualizacion": ahora(),
                },
            )


def crear_tarea(
    titulo: str,
    descripcion: str,
    responsables_ids: list[str] | None,
    fecha_entrega: str | None,
    prioridad: str,
    subtareas: list[str] | None = None,
) -> dict[str, Any]:
    titulo = titulo.strip()
    responsables_ids = list(dict.fromkeys(responsables_ids or []))

    if not titulo:
        raise ValueError("El título de la tarea es obligatorio.")

    tarea = insertar_fila(
        "tareas",
        {
            "id": uuid4().hex,
            "titulo": titulo,
            "descripcion": descripcion.strip(),
            "responsable_id": (
                responsables_ids[0]
                if responsables_ids
                else None
            ),
            "fecha_entrega": fecha_entrega or None,
            "prioridad": prioridad,
            "estado": "Pendiente",
            "avance": 0,
            "fecha_creacion": ahora(),
            "fecha_actualizacion": ahora(),
        },
    )

    _reemplazar_asignaciones(tarea["id"], responsables_ids)

    if responsables_ids and subtareas:
        _crear_subtareas_iniciales(
            tarea["id"],
            responsables_ids,
            subtareas,
        )

    registrar_historial(
        "Creación",
        tarea,
        (
            "Responsables: "
            + ", ".join(responsables_ids)
            if responsables_ids
            else "Sin responsables"
        ),
    )

    return obtener_tarea(tarea["id"]) or tarea


def _eliminar_subtareas(tarea_id: str) -> None:
    try:
        (
            obtener_cliente_supabase()
            .table("subtareas")
            .delete()
            .eq("tarea_id", tarea_id)
            .execute()
        )
    except Exception:
        pass


def _guardar_subtareas(
    tarea_id: str,
    subtareas_por_integrante: dict[str, list[dict[str, Any]]],
) -> None:
    _eliminar_subtareas(tarea_id)

    for integrante_id, subtareas in subtareas_por_integrante.items():
        for subtarea in subtareas:
            texto = str(subtarea.get("texto", "")).strip()

            if not texto:
                continue

            insertar_fila(
                "subtareas",
                {
                    "id": subtarea.get("id") or uuid4().hex,
                    "tarea_id": tarea_id,
                    "integrante_id": integrante_id,
                    "texto": texto,
                    "completada": bool(
                        subtarea.get("completada", False)
                    ),
                    "fecha_actualizacion": ahora(),
                },
            )


def actualizar_tarea(
    tarea_id: str,
    titulo: str,
    descripcion: str,
    responsables_ids: list[str],
    fecha_entrega: str | None,
    prioridad: str,
    subtareas_por_integrante: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    tarea_anterior = obtener_tarea(tarea_id)

    if tarea_anterior is None:
        raise ValueError("La tarea no existe.")

    titulo = titulo.strip()
    responsables_ids = list(dict.fromkeys(responsables_ids))

    if not titulo:
        raise ValueError("El título de la tarea es obligatorio.")

    actualizar_fila(
        "tareas",
        "id",
        tarea_id,
        {
            "titulo": titulo,
            "descripcion": descripcion.strip(),
            "responsable_id": (
                responsables_ids[0]
                if responsables_ids
                else None
            ),
            "fecha_entrega": fecha_entrega or None,
            "prioridad": prioridad,
            "fecha_actualizacion": ahora(),
        },
    )

    _reemplazar_asignaciones(tarea_id, responsables_ids)
    _guardar_subtareas(
        tarea_id,
        subtareas_por_integrante,
    )

    tarea = obtener_tarea(tarea_id)

    if tarea:
        actualizar_fila(
            "tareas",
            "id",
            tarea_id,
            {
                "estado": tarea["estado"],
                "avance": tarea["avance"],
                "fecha_actualizacion": ahora(),
            },
        )

    registrar_historial(
        "Actualización",
        tarea or tarea_anterior,
        "Tarea, responsables o subtareas modificados",
    )

    return obtener_tarea(tarea_id) or tarea_anterior


def actualizar_subtarea(
    subtarea_id: str,
    completada: bool,
) -> None:
    (
        obtener_cliente_supabase()
        .table("subtareas")
        .update(
            {
                "completada": bool(completada),
                "fecha_actualizacion": ahora(),
            }
        )
        .eq("id", subtarea_id)
        .execute()
    )


def eliminar_tarea(tarea_id: str) -> None:
    tarea = obtener_tarea(tarea_id)

    if tarea is None:
        return

    _eliminar_subtareas(tarea_id)

    (
        obtener_cliente_supabase()
        .table("tarea_integrantes")
        .delete()
        .eq("tarea_id", tarea_id)
        .execute()
    )

    eliminar_fila("tareas", "id", tarea_id)

    registrar_historial(
        "Eliminación",
        tarea,
        "Tarea eliminada",
    )


# ==========================================================
# HISTORIAL
# ==========================================================

def obtener_historial() -> list[dict[str, Any]]:
    return cargar_filas("historial", "fecha")


def registrar_historial(
    accion: str,
    tarea: dict[str, Any],
    detalle: str,
) -> None:
    insertar_fila(
        "historial",
        {
            "id": uuid4().hex,
            "fecha": ahora(),
            "accion": accion,
            "tarea_id": tarea.get("id"),
            "tarea": tarea.get("titulo", ""),
            "detalle": detalle,
        },
    )


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

def obtener_configuracion() -> dict[str, Any]:
    filas = cargar_filas("configuracion")

    configuracion = {
        fila["clave"]: fila.get("valor", "")
        for fila in filas
    }

    configuracion.setdefault(
        "nombre_proyecto",
        "Capstone Robótica",
    )
    configuracion.setdefault("proxima_entrega", "")

    return configuracion


def guardar_configuracion(
    configuracion: dict[str, Any],
) -> None:
    actuales = {
        fila["clave"]: fila
        for fila in cargar_filas("configuracion")
    }

    for clave, valor in configuracion.items():
        if clave in actuales:
            actualizar_fila(
                "configuracion",
                "clave",
                clave,
                {
                    "valor": str(valor),
                    "fecha_actualizacion": ahora(),
                },
            )
        else:
            insertar_fila(
                "configuracion",
                {
                    "clave": clave,
                    "valor": str(valor),
                    "fecha_actualizacion": ahora(),
                },
            )


# ==========================================================
# RESUMEN
# ==========================================================

def avance_por_integrante() -> list[dict[str, Any]]:
    integrantes = obtener_integrantes()
    tareas = obtener_tareas()

    resultado = []

    for integrante in integrantes:
        asignadas = [
            tarea
            for tarea in tareas
            if integrante["id"]
            in tarea.get("responsables_ids", [])
        ]

        avances = [
            tarea["progreso_individual"].get(
                integrante["id"],
                0,
            )
            for tarea in asignadas
        ]

        promedio = (
            round(sum(avances) / len(avances), 1)
            if avances
            else 0
        )

        resultado.append(
            {
                "Integrante": integrante["nombre"],
                "Rol": integrante["rol"],
                "Tareas": len(asignadas),
                "Completadas": sum(
                    avance == 100
                    for avance in avances
                ),
                "Avance (%)": promedio,
            }
        )

    return resultado
