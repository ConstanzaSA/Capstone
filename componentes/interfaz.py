import streamlit as st


def encabezado(titulo: str, subtitulo: str = "") -> None:
    st.markdown(
        f"""
        <div class="encabezado-principal">
            <div>
                <h1>{titulo}</h1>
                <p>{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tarjeta_indicador(titulo: str, valor: str, detalle: str = "") -> None:
    st.markdown(
        f"""
        <div class="tarjeta-indicador">
            <div class="indicador-titulo">{titulo}</div>
            <div class="indicador-valor">{valor}</div>
            <div class="indicador-detalle">{detalle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
