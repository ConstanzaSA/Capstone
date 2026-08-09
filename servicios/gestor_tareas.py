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
    obtener_cliente_supabase,
)


def ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ==========================================================
# INTEGRANTES
# ==========================================================

def obtener_integrantes() -> list[dict[str, Any]]:
    return cargar_filas("integrantes", "nombre")


def guardar_integrantes(integrantes: list[dict[str, Any]]) -> None:
    for integrante in integrantes:
        actualizar_fila(
            "integrantes",
            "id",
            integrante["id"],
            {
                "nombre": integrante.get("nombre", "").strip(),
                "rol": integrante.get("rol", "").strip(),
                "fecha_actualizacion": ahora(),
            },
        )
        registrar_evento(
            "Perfil",
            None,
            integrante.get("nombre", "Integrante"),
            "Se actualizaron los datos del integrante.",
        )


# ==========================================================
# TAREAS Y MULTIASIGNACIÓN
# ==========================================================

def _asignaciones_de_tarea(tarea_id: str) -> list[str]:
    filas = (
        obtener_cliente_supabase()
        .table("tarea_integrantes")
        .select("integrante_id")
        .eq("tarea_id", tarea_id)
        .execute()
        .data
        or []
    )
    return [fila["integrante_id"] for fila in filas]


def _guardar_asignaciones(tarea_id: str, integrante_ids: list[str] | None) -> None:
    integrante_ids = list(dict.fromkeys(integrante_ids or []))

    # Reemplazamos las asignaciones actuales por las nuevas.
    obtener_cliente_supabase().table("tarea_integrantes").delete().eq("tarea_id", tarea_id).execute()

    if integrante_ids:
        obtener_cliente_supabase().table("tarea_integrantes").insert(
            [
                {"tarea_id": tarea_id, "integrante_id": integrante_id}
                for integrante_id in integrante_ids
            ]
        ).execute()


def obtener_tareas() -> list[dict[str, Any]]:
    tareas = cargar_filas("tareas", "fecha_entrega")

    for tarea in tareas:
        responsable_ids = _asignaciones_de_tarea(tarea["id"])

        # Compatibilidad con datos antiguos que tenían un solo responsable_id.
        if not responsable_ids and tarea.get("responsable_id"):
            responsable_ids = [tarea["responsable_id"]]
            _guardar_asignaciones(tarea["id"], responsable_ids)

        tarea["responsable_ids"] = responsable_ids
        # Campo legado para que cualquier parte antigua de la aplicación no falle.
        tarea["responsable_id"] = responsable_ids[0] if len(responsable_ids) == 1 else None
        tarea.setdefault("fecha_entrega", "")
        tarea.setdefault("prioridad", "Baja")
        tarea.setdefault("estado", "Pendiente")
        tarea.setdefault("avance", 0)

    return tareas


def obtener_historial() -> list[dict[str, Any]]:
    return cargar_filas("historial", "fecha")


def obtener_configuracion() -> dict[str, Any]:
    configuracion = {"nombre_proyecto": "Capstone Robótica", "proxima_entrega": ""}
    for fila in cargar_filas("configuracion"):
        if fila.get("clave") in configuracion:
            configuracion[fila["clave"]] = fila.get("valor") or ""
    return configuracion


def guardar_configuracion(configuracion: dict[str, Any]) -> None:
    for clave in ("nombre_proyecto", "proxima_entrega"):
        valor = configuracion.get(clave, "")
        existente = obtener_fila("configuracion", "clave", clave)
        if existente:
            actualizar_fila(
                "configuracion",
                "clave",
                clave,
                {"valor": valor, "fecha_actualizacion": ahora()},
            )
        else:
            insertar_fila(
                "configuracion",
                {"clave": clave, "valor": valor, "fecha_actualizacion": ahora()},
            )
    registrar_evento("Configuración", None, "Proyecto", "Se actualizó la configuración general.")


def registrar_evento(
    accion: str,
    tarea_id: str | None,
    tarea: str,
    detalle: str,
) -> None:
    insertar_fila(
        "historial",
        {
            "id": uuid4().hex,
            "fecha": ahora(),
            "accion": accion,
            "tarea_id": tarea_id,
            "tarea": tarea,
            "detalle": detalle,
        },
    )


def crear_tarea(
    titulo: str,
    descripcion: str,
    responsable_ids: list[str] | None,
    fecha_entrega: str,
    prioridad: str,
) -> None:
    tarea_id = uuid4().hex
    ahora_actual = ahora()

    tarea = insertar_fila(
        "tareas",
        {
            "id": tarea_id,
            "titulo": titulo.strip(),
            "descripcion": descripcion.strip(),
            "responsable_id": (responsable_ids or [None])[0],
            "fecha_entrega": fecha_entrega,
            "prioridad": prioridad,
            "estado": "Pendiente",
            "avance": 0,
            "fecha_creacion": ahora_actual,
            "fecha_actualizacion": ahora_actual,
        },
    )

    _guardar_asignaciones(tarea_id, responsable_ids)

    nombres = _nombres_integrantes(responsable_ids or [])
    responsables_texto = ", ".join(nombres) if nombres else "Sin asignar"
    registrar_evento(
        "Creación",
        tarea["id"],
        tarea["titulo"],
        f"Responsables: {responsables_texto}",
    )


def actualizar_tarea(
    tarea_id: str,
    estado: str,
    avance: int,
    responsable_ids: list[str] | None,
    fecha_entrega: str,
) -> None:
    tarea = obtener_fila("tareas", "id", tarea_id)
    if not tarea:
        raise RuntimeError("No se encontró la tarea.")

    responsables_anteriores = _asignaciones_de_tarea(tarea_id)
    if not responsables_anteriores and tarea.get("responsable_id"):
        responsables_anteriores = [tarea["responsable_id"]]

    estado_anterior = tarea.get("estado", "Pendiente")
    avance_anterior = int(tarea.get("avance") or 0)
    fecha_anterior = tarea.get("fecha_entrega") or ""

    responsable_ids = list(dict.fromkeys(responsable_ids or []))
    avance = max(0, min(100, int(avance)))

    if estado == "Completada":
        avance = 100
    elif avance == 100:
        estado = "Completada"

    actual = actualizar_fila(
        "tareas",
        "id",
        tarea_id,
        {
            # Campo legado: conserva el primer responsable para compatibilidad.
            "responsable_id": responsable_ids[0] if responsable_ids else None,
            "fecha_entrega": fecha_entrega,
            "estado": estado,
            "avance": avance,
            "fecha_actualizacion": ahora(),
        },
    )

    _guardar_asignaciones(tarea_id, responsable_ids)

    cambios: list[str] = []

    if set(responsables_anteriores) != set(responsable_ids):
        anteriores = ", ".join(_nombres_integrantes(responsables_anteriores)) or "Sin asignar"
        nuevos = ", ".join(_nombres_integrantes(responsable_ids)) or "Sin asignar"
        cambios.append(f"Responsables: {anteriores} → {nuevos}")

    if fecha_anterior != fecha_entrega:
        cambios.append(
            f"Fecha de entrega: {fecha_anterior or 'Sin fecha'} → {fecha_entrega or 'Sin fecha'}"
        )
    if estado_anterior != actual["estado"]:
        cambios.append(f"Estado: {estado_anterior} → {actual['estado']}")
    if avance_anterior != actual["avance"]:
        cambios.append(f"Avance: {avance_anterior}% → {actual['avance']}%")

    registrar_evento(
        "Actualización",
        tarea_id,
        actual["titulo"],
        "; ".join(cambios) or "Sin cambios",
    )


def eliminar_tarea(tarea_id: str) -> None:
    tarea = obtener_fila("tareas", "id", tarea_id)
    if not tarea:
        return

    eliminar_fila("tareas", "id", tarea_id)
    registrar_evento(
        "Eliminación",
        tarea_id,
        tarea["titulo"],
        "Tarea eliminada. El historial se conserva.",
    )


def _nombres_integrantes(integrante_ids: list[str]) -> list[str]:
    if not integrante_ids:
        return []
    nombres = {
        integrante["id"]: integrante["nombre"]
        for integrante in obtener_integrantes()
    }
    return [nombres.get(integrante_id, integrante_id) for integrante_id in integrante_ids]


def avance_por_integrante() -> list[dict[str, Any]]:
    tareas = obtener_tareas()
    resultado = []

    for integrante in obtener_integrantes():
        asignadas = [
            tarea
            for tarea in tareas
            if integrante["id"] in tarea.get("responsable_ids", [])
        ]
        promedio = (
            round(
                sum(int(tarea.get("avance") or 0) for tarea in asignadas)
                / len(asignadas),
                1,
            )
            if asignadas
            else 0
        )
        resultado.append(
            {
                "Integrante": integrante["nombre"],
                "Rol": integrante.get("rol", ""),
                "Tareas": len(asignadas),
                "Completadas": sum(
                    tarea.get("estado") == "Completada" for tarea in asignadas
                ),
                "Avance (%)": promedio,
            }
        )

    return resultado
