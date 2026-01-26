"""Router: Autorizaciones"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from database import get_db
from models.aseguradoras import Autorizacion, EstadoAutorizacionEnum
from schemas.base import ResponseSchema

router_autorizaciones = APIRouter(prefix="/autorizaciones", tags=["Autorizaciones"])

@router_autorizaciones.post("/")
def solicitar_autorizacion(
    plan_id: int,
    orden_id: Optional[int] = None,
    procedimiento_codigo: Optional[str] = None,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """REGLA DE NEGOCIO: Requerida para prestaciones marcadas"""
    autorizacion = Autorizacion(
        orden_id=orden_id,
        plan_id=plan_id,
        procedimiento_codigo=procedimiento_codigo,
        fecha_solicitud=date.today(),
        estado=EstadoAutorizacionEnum.SOLICITADA,
        observaciones=observaciones
    )
    db.add(autorizacion)
    db.commit()
    db.refresh(autorizacion)
    return ResponseSchema(success=True, message="Autorización solicitada", data=autorizacion.to_dict())

@router_autorizaciones.patch("/{autorizacion_id}/aprobar")
def aprobar_autorizacion(
    autorizacion_id: int,
    numero_autorizacion: str,
    fecha_vencimiento: Optional[date] = None,
    db: Session = Depends(get_db)
):
    autorizacion = db.query(Autorizacion).filter(Autorizacion.id == autorizacion_id).first()
    if not autorizacion:
        raise HTTPException(status_code=404, detail="Autorización no encontrada")
    
    autorizacion.estado = EstadoAutorizacionEnum.APROBADA
    autorizacion.numero_autorizacion = numero_autorizacion
    autorizacion.fecha_respuesta = date.today()
    autorizacion.fecha_vencimiento = fecha_vencimiento
    db.commit()
    return ResponseSchema(success=True, message="Autorización aprobada")

@router_autorizaciones.patch("/{autorizacion_id}/negar")
def negar_autorizacion(
    autorizacion_id: int,
    motivo_negacion: str,
    db: Session = Depends(get_db)
):
    autorizacion = db.query(Autorizacion).filter(Autorizacion.id == autorizacion_id).first()
    if not autorizacion:
        raise HTTPException(status_code=404, detail="Autorización no encontrada")
    
    autorizacion.estado = EstadoAutorizacionEnum.NEGADA
    autorizacion.motivo_negacion = motivo_negacion
    autorizacion.fecha_respuesta = date.today()
    db.commit()
    return ResponseSchema(success=True, message="Autorización negada")
