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


# ==========================================================
# UTILIDADES
# ==========================================================

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
# TAREAS
# ==========================================================

def _responsables_por_tarea() -> dict[str, list[str]]:
    relaciones = cargar_filas("tarea_integrantes")

    resultado: dict[str, list[str]] = {}

    for relacion in relaciones:
        resultado.setdefault(
            relacion["tarea_id"],
            [],
        ).append(
            relacion["integrante_id"]
        )

    return resultado


def _subtareas_por_tarea() -> dict[str, list[dict[str, Any]]]:

    try:
        filas = cargar_filas("subtareas")
    except Exception:
        return {}

    resultado: dict[str, list[dict[str, Any]]] = {}

    for fila in filas:
        resultado.setdefault(
            fila["tarea_id"],
            [],
        ).append(fila)

    return resultado


def obtener_tareas() -> list[dict[str, Any]]:

    tareas = cargar_filas(
        "tareas",
        "fecha_actualizacion",
    )

    responsables = _responsables_por_tarea()
    subtareas = _subtareas_por_tarea()

    for tarea in tareas:

        # --------------------------------------------------
        # RESPONSABLES
        # --------------------------------------------------

        ids = responsables.get(
            tarea["id"],
            [],
        )

        # Compatibilidad con responsable_id antiguo.
        if not ids and tarea.get("responsable_id"):
            ids = [tarea["responsable_id"]]

        tarea["responsables_ids"] = ids

        tarea["responsable_id"] = (
            ids[0]
            if ids
            else None
        )

        # --------------------------------------------------
        # CHECKLIST
        # --------------------------------------------------

        lista_subtareas = subtareas.get(
            tarea["id"],
            [],
        )

        tarea["subtareas"] = lista_subtareas

        # --------------------------------------------------
        # AVANCE INDIVIDUAL
        # --------------------------------------------------

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

        # --------------------------------------------------
        # AVANCE GLOBAL
        # --------------------------------------------------

        if progreso_individual:

            tarea["avance"] = round(
                sum(
                    progreso_individual.values()
                )
                / len(progreso_individual)
            )

        else:
            tarea["avance"] = 0

        # --------------------------------------------------
        # ESTADO
        # --------------------------------------------------

        if tarea["avance"] == 100 and ids:
            tarea["estado"] = "Completada"

        elif tarea["avance"] > 0:
            tarea["estado"] = "En progreso"

        else:
            tarea["estado"] = "Pendiente"

        tarea.setdefault(
            "descripcion",
            "",
        )

        tarea.setdefault(
            "fecha_entrega",
            None,
        )

        tarea.setdefault(
            "prioridad",
            "Baja",
        )

    return tareas


def obtener_tarea(
    tarea_id: str,
) -> dict[str, Any] | None:

    return next(
        (
            tarea
            for tarea in obtener_tareas()
            if tarea["id"] == tarea_id
        ),
        None,
    )


# ==========================================================
# ASIGNACIÓN DE RESPONSABLES
# ==========================================================

def _reemplazar_asignaciones(
    tarea_id: str,
    responsables_ids: list[str],
) -> None:

    actuales = [
        fila
        for fila in cargar_filas(
            "tarea_integrantes"
        )
        if fila["tarea_id"] == tarea_id
    ]

    for fila in actuales:

        (
            obtener_cliente_supabase()
            .table("tarea_integrantes")
            .delete()
            .eq(
                "tarea_id",
                tarea_id,
            )
            .eq(
                "integrante_id",
                fila["integrante_id"],
            )
            .execute()
        )

    for integrante_id in sorted(
        set(responsables_ids)
    ):

        insertar_fila(
            "tarea_integrantes",
            {
                "tarea_id": tarea_id,
                "integrante_id": integrante_id,
                "fecha_asignacion": ahora(),
            },
        )


# ==========================================================
# CHECKLIST
# ==========================================================

def crear_subtarea(
    tarea_id: str,
    integrante_id: str,
    texto: str,
) -> dict[str, Any]:

    texto = texto.strip()

    if not texto:
        raise ValueError(
            "El texto de la checklist no puede estar vacío."
        )

    tarea = obtener_tarea(tarea_id)

    if tarea is None:
        raise ValueError(
            "La tarea no existe."
        )

    # El integrante debe estar asignado a la tarea.
    if integrante_id not in tarea.get(
        "responsables_ids",
        [],
    ):
        raise ValueError(
            "El integrante no está asignado a esta tarea."
        )

    nueva = insertar_fila(
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

    # Actualizar avance global.
    _actualizar_avance_tarea(tarea_id)

    return nueva


def actualizar_subtarea(
    subtarea_id: str,
    completada: bool,
) -> None:

    resultado = (
        obtener_cliente_supabase()
        .table("subtareas")
        .update(
            {
                "completada": bool(completada),
                "fecha_actualizacion": ahora(),
            }
        )
        .eq(
            "id",
            subtarea_id,
        )
        .execute()
    )

    if not resultado.data:
        raise RuntimeError(
            "No se pudo actualizar la checklist."
        )

    # Buscar la tarea asociada.
    try:
        fila = (
            obtener_cliente_supabase()
            .table("subtareas")
            .select("tarea_id")
            .eq(
                "id",
                subtarea_id,
            )
            .limit(1)
            .execute()
        )

        if fila.data:
            _actualizar_avance_tarea(
                fila.data[0]["tarea_id"]
            )

    except Exception:
        pass


def eliminar_subtarea(
    subtarea_id: str,
) -> None:

    try:

        fila = (
            obtener_cliente_supabase()
            .table("subtareas")
            .select("tarea_id")
            .eq(
                "id",
                subtarea_id,
            )
            .limit(1)
            .execute()
        )

        tarea_id = (
            fila.data[0]["tarea_id"]
            if fila.data
            else None
        )

        (
            obtener_cliente_supabase()
            .table("subtareas")
            .delete()
            .eq(
                "id",
                subtarea_id,
            )
            .execute()
        )

        if tarea_id:
            _actualizar_avance_tarea(
                tarea_id
            )

    except Exception as error:
        raise RuntimeError(
            "No se pudo eliminar la checklist."
        ) from error


def _actualizar_avance_tarea(
    tarea_id: str,
) -> None:

    tarea = obtener_tarea(tarea_id)

    if tarea is None:
        return

    avance = tarea.get(
        "avance",
        0,
    )

    estado = "Pendiente"

    if avance == 100 and tarea.get(
        "responsables_ids"
    ):
        estado = "Completada"

    elif avance > 0:
        estado = "En progreso"

    actualizar_fila(
        "tareas",
        "id",
        tarea_id,
        {
            "avance": avance,
            "estado": estado,
            "fecha_actualizacion": ahora(),
        },
    )


# ==========================================================
# CREACIÓN DE TAREAS
# ==========================================================

def _crear_checklists_iniciales(
    tarea_id: str,
    checklists: list[dict[str, str]],
) -> None:

    for checklist in checklists:

        texto = str(
            checklist.get(
                "texto",
                "",
            )
        ).strip()

        integrante_id = checklist.get(
            "integrante_id"
        )

        if not texto or not integrante_id:
            continue

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
    subtareas: list[dict[str, str]] | None = None,
) -> dict[str, Any]:

    titulo = titulo.strip()

    responsables_ids = list(
        dict.fromkeys(
            responsables_ids or []
        )
    )

    if not titulo:
        raise ValueError(
            "El título de la tarea es obligatorio."
        )

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
            "fecha_entrega": (
                fecha_entrega
                or None
            ),
            "prioridad": prioridad,
            "estado": "Pendiente",
            "avance": 0,
            "fecha_creacion": ahora(),
            "fecha_actualizacion": ahora(),
        },
    )

    _reemplazar_asignaciones(
        tarea["id"],
        responsables_ids,
    )

    # Cada checklist tiene su propio responsable.
    if subtareas:
        _crear_checklists_iniciales(
            tarea["id"],
            subtareas,
        )

    registrar_historial(
        "Creación",
        tarea,
        (
            "Responsables: "
            + ", ".join(
                responsables_ids
            )
            if responsables_ids
            else "Sin responsables"
        ),
    )

    return obtener_tarea(
        tarea["id"]
    ) or tarea


# ==========================================================
# ACTUALIZACIÓN DE TAREAS
# ==========================================================

def actualizar_tarea(
    tarea_id: str,
    titulo: str,
    descripcion: str,
    responsables_ids: list[str],
    fecha_entrega: str | None,
    prioridad: str,
    subtareas_por_integrante: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:

    tarea_anterior = obtener_tarea(
        tarea_id
    )

    if tarea_anterior is None:
        raise ValueError(
            "La tarea no existe."
        )

    titulo = titulo.strip()

    responsables_ids = list(
        dict.fromkeys(
            responsables_ids
        )
    )

    if not titulo:
        raise ValueError(
            "El título de la tarea es obligatorio."
        )

    # --------------------------------------------------
    # SOLO DATOS PRINCIPALES DE LA TAREA
    # --------------------------------------------------

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
            "fecha_entrega": (
                fecha_entrega
                or None
            ),
            "prioridad": prioridad,
            "fecha_actualizacion": ahora(),
        },
    )

    _reemplazar_asignaciones(
        tarea_id,
        responsables_ids,
    )

    # --------------------------------------------------
    # IMPORTANTE:
    # Si subtareas_por_integrante es None,
    # NO tocamos las checklist.
    #
    # Esto permite que "Editar tarea" modifique
    # solamente:
    # título / responsables / fecha / prioridad.
    # --------------------------------------------------

    if subtareas_por_integrante is not None:

        _guardar_subtareas(
            tarea_id,
            subtareas_por_integrante,
        )

    tarea = obtener_tarea(
        tarea_id
    )

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
        "Datos principales de la tarea modificados",
    )

    return (
        obtener_tarea(tarea_id)
        or tarea_anterior
    )


def _eliminar_subtareas(
    tarea_id: str,
) -> None:

    try:

        (
            obtener_cliente_supabase()
            .table("subtareas")
            .delete()
            .eq(
                "tarea_id",
                tarea_id,
            )
            .execute()
        )

    except Exception:
        pass


def _guardar_subtareas(
    tarea_id: str,
    subtareas_por_integrante: dict[
        str,
        list[dict[str, Any]]
    ],
) -> None:

    _eliminar_subtareas(
        tarea_id
    )

    for integrante_id, subtareas in (
        subtareas_por_integrante.items()
    ):

        for subtarea in subtareas:

            texto = str(
                subtarea.get(
                    "texto",
                    "",
                )
            ).strip()

            if not texto:
                continue

            insertar_fila(
                "subtareas",
                {
                    "id": (
                        subtarea.get("id")
                        or uuid4().hex
                    ),
                    "tarea_id": tarea_id,
                    "integrante_id": integrante_id,
                    "texto": texto,
                    "completada": bool(
                        subtarea.get(
                            "completada",
                            False,
                        )
                    ),
                    "fecha_actualizacion": ahora(),
                },
            )


# ==========================================================
# ELIMINAR TAREA
# ==========================================================

def eliminar_tarea(
    tarea_id: str,
) -> None:

    tarea = obtener_tarea(
        tarea_id
    )

    if tarea is None:
        return

    _eliminar_subtareas(
        tarea_id
    )

    (
        obtener_cliente_supabase()
        .table("tarea_integrantes")
        .delete()
        .eq(
            "tarea_id",
            tarea_id,
        )
        .execute()
    )

    eliminar_fila(
        "tareas",
        "id",
        tarea_id,
    )

    registrar_historial(
        "Eliminación",
        tarea,
        "Tarea eliminada",
    )


# ==========================================================
# HISTORIAL
# ==========================================================

def obtener_historial() -> list[dict[str, Any]]:
    return cargar_filas(
        "historial",
        "fecha",
    )


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
            "tarea": tarea.get(
                "titulo",
                "",
            ),
            "detalle": detalle,
        },
    )


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

def obtener_configuracion() -> dict[str, Any]:

    filas = cargar_filas(
        "configuracion"
    )

    configuracion = {
        fila["clave"]: fila.get(
            "valor",
            "",
        )
        for fila in filas
    }

    configuracion.setdefault(
        "nombre_proyecto",
        "Capstone Robótica",
    )

    configuracion.setdefault(
        "proxima_entrega",
        "",
    )

    return configuracion


def guardar_configuracion(
    configuracion: dict[str, Any],
) -> None:

    actuales = {
        fila["clave"]: fila
        for fila in cargar_filas(
            "configuracion"
        )
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
            in tarea.get(
                "responsables_ids",
                [],
            )
        ]

        avances = [
            tarea[
                "progreso_individual"
            ].get(
                integrante["id"],
                0,
            )
            for tarea in asignadas
        ]

        promedio = (
            round(
                sum(avances)
                / len(avances),
                1,
            )
            if avances
            else 0
        )

        resultado.append(
            {
                "Integrante": integrante[
                    "nombre"
                ],
                "Rol": integrante[
                    "rol"
                ],
                "Tareas": len(
                    asignadas
                ),
                "Completadas": sum(
                    avance == 100
                    for avance in avances
                ),
                "Avance (%)": promedio,
            }
        )

    return resultado
