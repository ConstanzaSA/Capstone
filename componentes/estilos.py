from pathlib import Path
import streamlit as st


def aplicar_estilos() -> None:
    ruta = Path(__file__).resolve().parents[1] / "recursos" / "estilos.css"
    if ruta.exists():
        st.markdown(f"<style>{ruta.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
