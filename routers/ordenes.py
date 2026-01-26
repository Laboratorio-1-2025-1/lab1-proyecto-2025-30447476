"""Router: Órdenes Médicas - Módulo 2.4"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from database import get_db
from models.ordenes import Orden, TipoOrdenEnum, PrioridadOrdenEnum, EstadoOrdenEnum
from schemas.base import ResponseSchema

router_ordenes = APIRouter(prefix="/ordenes", tags=["Órdenes Médicas"])

@router_ordenes.post("/", status_code=status.HTTP_201_CREATED)
def crear_orden(
    episodio_id: int,
    tipo: TipoOrdenEnum,
    prioridad: PrioridadOrdenEnum = PrioridadOrdenEnum.NORMAL,
    indicaciones_generales: Optional[str] = None,
    db: Session = Depends(get_db)
):
    orden = Orden(
        episodio_id=episodio_id,
        tipo=tipo,
        prioridad=prioridad,
        estado=EstadoOrdenEnum.EMITIDA,
        fecha_emision=datetime.utcnow(),
        indicaciones_generales=indicaciones_generales
    )
    db.add(orden)
    db.commit()
    db.refresh(orden)
    return ResponseSchema(success=True, message="Orden creada", data=orden.to_dict())

@router_ordenes.get("/")
def listar_ordenes(
    episodio_id: Optional[int] = None,
    tipo: Optional[TipoOrdenEnum] = None,
    estado: Optional[EstadoOrdenEnum] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Orden)
    if episodio_id:
        query = query.filter(Orden.episodio_id == episodio_id)
    if tipo:
        query = query.filter(Orden.tipo == tipo)
    if estado:
        query = query.filter(Orden.estado == estado)
    
    ordenes = query.all()
    return ResponseSchema(success=True, data=[o.to_dict() for o in ordenes])

@router_ordenes.patch("/{orden_id}/estado")
def actualizar_estado_orden(
    orden_id: int,
    estado: EstadoOrdenEnum,
    db: Session = Depends(get_db)
):
    orden = db.query(Orden).filter(Orden.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    orden.estado = estado
    if estado == EstadoOrdenEnum.AUTORIZADA:
        orden.fecha_autorizacion = datetime.utcnow()
    elif estado == EstadoOrdenEnum.COMPLETADA:
        orden.fecha_completado = datetime.utcnow()
    
    db.commit()
    return ResponseSchema(success=True, message=f"Orden {estado.value}")
