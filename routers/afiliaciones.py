"""Router: Afiliaciones Persona-Plan"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from database import get_db
from models.aseguradoras import Afiliacion
from schemas.base import ResponseSchema

router_afiliaciones = APIRouter(prefix="/afiliaciones", tags=["Afiliaciones"])

@router_afiliaciones.post("/")
def crear_afiliacion(
    persona_id: int,
    plan_id: int,
    numero_poliza: str,
    vigente_desde: date,
    vigente_hasta: Optional[date] = None,
    copago: Optional[float] = None,
    cuota_moderadora: Optional[float] = None,
    db: Session = Depends(get_db)
):
    # Validar póliza única
    existe = db.query(Afiliacion).filter(Afiliacion.numero_poliza == numero_poliza).first()
    if existe:
        raise HTTPException(status_code=400, detail="Número de póliza ya existe")
    
    afiliacion = Afiliacion(
        persona_id=persona_id,
        plan_id=plan_id,
        numero_poliza=numero_poliza,
        vigente_desde=vigente_desde,
        vigente_hasta=vigente_hasta,
        copago=copago,
        cuota_moderadora=cuota_moderadora,
        activa=True
    )
    db.add(afiliacion)
    db.commit()
    db.refresh(afiliacion)
    return ResponseSchema(success=True, message="Afiliación creada", data=afiliacion.to_dict())

@router_afiliaciones.get("/persona/{persona_id}")
def listar_afiliaciones_persona(persona_id: int, db: Session = Depends(get_db)):
    afiliaciones = db.query(Afiliacion).filter(Afiliacion.persona_id == persona_id).all()
    return ResponseSchema(success=True, data=[a.to_dict() for a in afiliaciones])
