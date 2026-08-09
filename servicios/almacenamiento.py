from __future__ import annotations
from typing import Any
import streamlit as st
from supabase import Client, create_client

@st.cache_resource
def obtener_cliente_supabase() -> Client:
    try:
        url=str(st.secrets["supabase"]["url"]).strip()
        key=str(st.secrets["supabase"]["key"]).strip()
    except Exception as error:
        raise RuntimeError("Faltan [supabase] url y key en los Secrets de Streamlit.") from error
    return create_client(url,key)

def inicializar_datos() -> None:
    obtener_cliente_supabase().table("configuracion").select("clave").limit(1).execute()

def cargar_filas(tabla:str, orden:str|None=None)->list[dict[str,Any]]:
    q=obtener_cliente_supabase().table(tabla).select("*")
    if orden: q=q.order(orden,desc=True)
    return list(q.execute().data or [])

def insertar_fila(tabla:str,fila:dict[str,Any])->dict[str,Any]:
    r=obtener_cliente_supabase().table(tabla).insert(fila).execute()
    if not r.data: raise RuntimeError(f"No se pudo insertar en {tabla}.")
    return dict(r.data[0])

def actualizar_fila(tabla:str,columna:str,valor:Any,cambios:dict[str,Any])->dict[str,Any]:
    r=obtener_cliente_supabase().table(tabla).update(cambios).eq(columna,valor).execute()
    if not r.data: raise RuntimeError(f"No se pudo actualizar en {tabla}.")
    return dict(r.data[0])

def eliminar_fila(tabla:str,columna:str,valor:Any)->None:
    obtener_cliente_supabase().table(tabla).delete().eq(columna,valor).execute()

def obtener_fila(tabla:str,columna:str,valor:Any)->dict[str,Any]|None:
    r=obtener_cliente_supabase().table(tabla).select("*").eq(columna,valor).limit(1).execute()
    return dict(r.data[0]) if r.data else None
