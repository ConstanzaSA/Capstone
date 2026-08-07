from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from servicios.almacenamiento import cargar_filas,insertar_fila,actualizar_fila,eliminar_fila,obtener_fila

def ahora()->str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def obtener_integrantes()->list[dict[str,Any]]:
    return cargar_filas("integrantes","nombre")

def guardar_integrantes(integrantes:list[dict[str,Any]])->None:
    for i in integrantes:
        actualizar_fila("integrantes","id",i["id"],{"nombre":i.get("nombre","").strip(),"rol":i.get("rol","").strip(),"fecha_actualizacion":ahora()})
    registrar_evento("Perfil",None,"Integrantes","Se actualizaron los datos de un integrante.")

def obtener_tareas()->list[dict[str,Any]]:
    tareas=cargar_filas("tareas","fecha_entrega")
    for t in tareas:
        t.setdefault("responsable_id",None); t.setdefault("fecha_entrega","")
        t.setdefault("prioridad","Baja"); t.setdefault("estado","Pendiente"); t.setdefault("avance",0)
    return tareas

def obtener_historial()->list[dict[str,Any]]:
    return cargar_filas("historial","fecha")

def obtener_configuracion()->dict[str,Any]:
    c={"nombre_proyecto":"Capstone Robótica","proxima_entrega":""}
    for f in cargar_filas("configuracion"):
        if f.get("clave") in c: c[f["clave"]]=f.get("valor") or ""
    return c

def guardar_configuracion(configuracion:dict[str,Any])->None:
    for clave in ("nombre_proyecto","proxima_entrega"):
        valor=configuracion.get(clave,"")
        existente=obtener_fila("configuracion","clave",clave)
        if existente:
            actualizar_fila("configuracion","clave",clave,{"valor":valor,"fecha_actualizacion":ahora()})
        else:
            insertar_fila("configuracion",{"clave":clave,"valor":valor,"fecha_actualizacion":ahora()})
    registrar_evento("Configuración",None,"Proyecto","Se actualizó la configuración general.")

def registrar_evento(accion:str,tarea_id:str|None,tarea:str,detalle:str)->None:
    insertar_fila("historial",{"id":uuid4().hex,"fecha":ahora(),"accion":accion,"tarea_id":tarea_id,"tarea":tarea,"detalle":detalle})

def crear_tarea(titulo:str,descripcion:str,responsable_id:str|None,fecha_entrega:str,prioridad:str)->None:
    t=insertar_fila("tareas",{"id":uuid4().hex,"titulo":titulo.strip(),"descripcion":descripcion.strip(),"responsable_id":responsable_id,"fecha_entrega":fecha_entrega,"prioridad":prioridad,"estado":"Pendiente","avance":0,"fecha_creacion":ahora(),"fecha_actualizacion":ahora()})
    registrar_evento("Creación",t["id"],t["titulo"],f"Responsable: {responsable_id or 'Sin asignar'}")

def actualizar_tarea(tarea_id:str,estado:str,avance:int,responsable_id:str|None,fecha_entrega:str)->None:
    t=obtener_fila("tareas","id",tarea_id)
    if not t: raise RuntimeError("No se encontró la tarea.")
    ant_resp=t.get("responsable_id"); ant_estado=t.get("estado"); ant_avance=int(t.get("avance") or 0); ant_fecha=t.get("fecha_entrega") or ""
    avance=max(0,min(100,int(avance)))
    if estado=="Completada": avance=100
    elif avance==100: estado="Completada"
    actual=actualizar_fila("tareas","id",tarea_id,{"responsable_id":responsable_id,"fecha_entrega":fecha_entrega,"estado":estado,"avance":avance,"fecha_actualizacion":ahora()})
    cambios=[]
    if ant_resp!=responsable_id: cambios.append(f"Responsable: {ant_resp or 'Sin asignar'} → {responsable_id or 'Sin asignar'}")
    if ant_fecha!=fecha_entrega: cambios.append(f"Fecha de entrega: {ant_fecha or 'Sin fecha'} → {fecha_entrega or 'Sin fecha'}")
    if ant_estado!=actual["estado"]: cambios.append(f"Estado: {ant_estado} → {actual['estado']}")
    if ant_avance!=actual["avance"]: cambios.append(f"Avance: {ant_avance}% → {actual['avance']}%")
    registrar_evento("Actualización",tarea_id,actual["titulo"],"; ".join(cambios) or "Sin cambios")

def eliminar_tarea(tarea_id:str)->None:
    t=obtener_fila("tareas","id",tarea_id)
    if not t: return
    eliminar_fila("tareas","id",tarea_id)
    registrar_evento("Eliminación",tarea_id,t["titulo"],"Tarea eliminada. El historial se conserva.")

def avance_por_integrante()->list[dict[str,Any]]:
    tareas=obtener_tareas(); resultado=[]
    for i in obtener_integrantes():
        asignadas=[t for t in tareas if t.get("responsable_id")==i["id"]]
        promedio=round(sum(int(t.get("avance") or 0) for t in asignadas)/len(asignadas),1) if asignadas else 0
        resultado.append({"Integrante":i["nombre"],"Rol":i.get("rol",""),"Tareas":len(asignadas),"Completadas":sum(t.get("estado")=="Completada" for t in asignadas),"Avance (%)":promedio})
    return resultado
