from __future__ import annotations

from servicios.almacenamiento import supabase


# ==========================================================
# OBTENER COMPRAS
# ==========================================================

def obtener_compras():

    respuesta = (
        supabase
        .table("compras")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    return respuesta.data or []


# ==========================================================
# CREAR COMPRA
# ==========================================================

def crear_compra(
    nombre_compra,
    cantidad,
    link,
    precio,
):

    datos = {
        "nombre_compra": nombre_compra.strip(),
        "cantidad": cantidad,
        "link": link.strip(),
        "precio": precio,
        "comprador": None,
        "estado": "Sin comprar",
    }

    respuesta = (
        supabase
        .table("compras")
        .insert(datos)
        .execute()
    )

    return respuesta.data


# ==========================================================
# MARCAR COMO COMPRADO
# ==========================================================

def marcar_comprado(
    compra_id,
    comprador,
):

    datos = {
        "comprador": comprador,
        "estado": "Comprado",
    }

    respuesta = (
        supabase
        .table("compras")
        .update(datos)
        .eq("id", compra_id)
        .execute()
    )

    return respuesta.data


# ==========================================================
# ACTUALIZAR COMPRA
# ==========================================================

def actualizar_compra(
    compra_id,
    nombre_compra,
    cantidad,
    link,
    precio,
):

    datos = {
        "nombre_compra": nombre_compra.strip(),
        "cantidad": cantidad,
        "link": link.strip(),
        "precio": precio,
    }

    respuesta = (
        supabase
        .table("compras")
        .update(datos)
        .eq("id", compra_id)
        .execute()
    )

    return respuesta.data


# ==========================================================
# VOLVER A "SIN COMPRAR"
# ==========================================================

def marcar_sin_comprar(
    compra_id,
):

    datos = {
        "comprador": None,
        "estado": "Sin comprar",
    }

    respuesta = (
        supabase
        .table("compras")
        .update(datos)
        .eq("id", compra_id)
        .execute()
    )

    return respuesta.data


# ==========================================================
# ELIMINAR COMPRA
# ==========================================================

def eliminar_compra(
    compra_id,
):

    respuesta = (
        supabase
        .table("compras")
        .delete()
        .eq("id", compra_id)
        .execute()
    )

    return respuesta.data
