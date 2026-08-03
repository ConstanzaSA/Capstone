import html

import streamlit as st


def encabezado(titulo: str, subtitulo: str = "") -> None:
    """Muestra el encabezado morado principal de cada página."""
    titulo_seguro = html.escape(str(titulo))
    subtitulo_seguro = html.escape(str(subtitulo))

    st.markdown(
        f"""
        <div class="encabezado-principal">
            <div class="encabezado-texto">
                <h1>{titulo_seguro}</h1>
                <p>{subtitulo_seguro}</p>
            </div>
            <div class="icono-robot" aria-hidden="true">🤖</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tarjeta_indicador(titulo: str, valor: str, detalle: str = "") -> None:
    """Muestra una tarjeta de resumen en la página principal."""
    st.markdown(
        f"""
        <div class="tarjeta-indicador">
            <div class="indicador-titulo">{html.escape(str(titulo))}</div>
            <div class="indicador-valor">{html.escape(str(valor))}</div>
            <div class="indicador-detalle">{html.escape(str(detalle))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
