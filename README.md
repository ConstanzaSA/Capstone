# Seguimiento de Robótica

Aplicación web hecha solamente con Python y Streamlit para organizar tareas semanales de cuatro integrantes.

## Publicación en Streamlit Community Cloud

1. Sube esta carpeta completa a un repositorio de GitHub.
2. En Streamlit Community Cloud selecciona el repositorio.
3. Indica `aplicacion.py` como archivo principal.
4. Despliega la aplicación.

## Guardado compartido mediante GitHub

La aplicación funciona localmente sin configuración adicional. Para que los cambios realizados desde Streamlit Cloud queden guardados en el repositorio, agrega estos secretos en la configuración de la aplicación:

```toml
[github]
token = "TOKEN_DE_GITHUB"
repositorio = "usuario/nombre_del_repositorio"
rama = "main"
carpeta_datos = "datos"
```

El token necesita permiso de escritura sobre el contenido del repositorio. Nunca subas `secrets.toml` a GitHub.

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run aplicacion.py
```

## Estructura

- `aplicacion.py`: entrada principal.
- `paginas/`: pantallas de la aplicación.
- `componentes/`: elementos visuales reutilizables.
- `servicios/`: lectura, guardado y lógica de tareas.
- `datos/`: archivos JSON compartidos.
- `recursos/`: estilos de la interfaz.
