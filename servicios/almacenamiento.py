from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import requests
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DATOS_DIR = BASE_DIR / "datos"

ARCHIVOS = {
    "integrantes": DATOS_DIR / "integrantes.json",
    "tareas": DATOS_DIR / "tareas.json",
    "historial": DATOS_DIR / "historial.json",
    "configuracion": DATOS_DIR / "configuracion.json",
}

DATOS_INICIALES: dict[str, Any] = {
    "integrantes": [
        {"id": "integrante_1", "nombre": "Integrante 1", "rol": "Mecánica"},
        {"id": "integrante_2", "nombre": "Integrante 2", "rol": "Electrónica"},
        {"id": "integrante_3", "nombre": "Integrante 3", "rol": "Programación"},
        {"id": "integrante_4", "nombre": "Integrante 4", "rol": "Control"},
    ],
    "tareas": [],
    "historial": [],
    "configuracion": {
        "nombre_proyecto": "Capstone Robótica",
        "proxima_entrega": "",
    },
}


def _configuracion_github() -> dict[str, str] | None:
    try:
        datos = st.secrets.get("github", {})
    except Exception:
        return None

    requeridos = ("token", "repositorio", "rama")
    if not datos or not all(datos.get(clave) for clave in requeridos):
        return None

    return {
        "token": str(datos["token"]),
        "repositorio": str(datos["repositorio"]),
        "rama": str(datos["rama"]),
        "carpeta_datos": str(datos.get("carpeta_datos", "datos")),
    }


def inicializar_datos() -> None:
    DATOS_DIR.mkdir(parents=True, exist_ok=True)
    for nombre, ruta in ARCHIVOS.items():
        if not ruta.exists():
            ruta.write_text(
                json.dumps(DATOS_INICIALES[nombre], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )


def _leer_local(nombre: str) -> Any:
    inicializar_datos()
    return json.loads(ARCHIVOS[nombre].read_text(encoding="utf-8"))


def _guardar_local(nombre: str, datos: Any) -> None:
    ARCHIVOS[nombre].write_text(
        json.dumps(datos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _ruta_github(nombre: str, config: dict[str, str]) -> str:
    return f"{config['carpeta_datos'].strip('/')}/{nombre}.json"


def _leer_github(nombre: str, config: dict[str, str]) -> tuple[Any, str]:
    ruta = _ruta_github(nombre, config)
    url = f"https://api.github.com/repos/{config['repositorio']}/contents/{ruta}"
    respuesta = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {config['token']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        params={"ref": config["rama"]},
        timeout=30,
    )
    respuesta.raise_for_status()
    contenido = respuesta.json()
    texto = base64.b64decode(contenido["content"]).decode("utf-8")
    return json.loads(texto), contenido["sha"]


def _guardar_github(nombre: str, datos: Any, mensaje: str, config: dict[str, str]) -> None:
    _, sha = _leer_github(nombre, config)
    ruta = _ruta_github(nombre, config)
    url = f"https://api.github.com/repos/{config['repositorio']}/contents/{ruta}"
    contenido = base64.b64encode(
        json.dumps(datos, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("ascii")
    respuesta = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {config['token']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={
            "message": mensaje,
            "content": contenido,
            "sha": sha,
            "branch": config["rama"],
        },
        timeout=30,
    )
    respuesta.raise_for_status()


def cargar_datos(nombre: str) -> Any:
    config = _configuracion_github()
    if config:
        try:
            datos, _ = _leer_github(nombre, config)
            return datos
        except requests.RequestException as error:
            st.warning(
                f"No se pudo leer {nombre}.json desde GitHub. "
                f"Se usará la copia local. Detalle: {error}"
            )
    return _leer_local(nombre)


def guardar_datos(nombre: str, datos: Any, mensaje: str) -> None:
    _guardar_local(nombre, datos)
    config = _configuracion_github()
    if config:
        try:
            _guardar_github(nombre, datos, mensaje, config)
        except requests.RequestException as error:
            raise RuntimeError(
                "El cambio quedó guardado en la instancia actual, pero no pudo "
                f"subirse a GitHub: {error}"
            ) from error
