"""
Router: Consentimientos Informados - Módulo 2.3
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from database import get_db
from models.registro_clinico import Consentimiento, MetodoConsentimientoEnum
from schemas.base import ResponseSchema

router_consentimientos = APIRouter(prefix="/consentimientos", tags=["Consentimientos"])

@router_consentimientos.post("/", status_code=status.HTTP_201_CREATED)
def crear_consentimiento(
    persona_id: int,
    tipo_procedimiento: str,
    metodo: MetodoConsentimientoEnum,
    descripcion: Optional[str] = None,
    riesgos_explicados: Optional[str] = None,
    archivo_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    consentimiento = Consentimiento(
        persona_id=persona_id,
        tipo_procedimiento=tipo_procedimiento,
        fecha=datetime.utcnow(),
        metodo=metodo,
        descripcion=descripcion,
        riesgos_explicados=riesgos_explicados,
        archivo_id=archivo_id
    )
    db.add(consentimiento)
    db.commit()
    db.refresh(consentimiento)
    return ResponseSchema(success=True, message="Consentimiento creado", data=consentimiento.to_dict())

@router_consentimientos.get("/persona/{persona_id}")
def listar_consentimientos_persona(persona_id: int, db: Session = Depends(get_db)):
    consentimientos = db.query(Consentimiento).filter(Consentimiento.persona_id == persona_id).all()
    return ResponseSchema(success=True, data=[c.to_dict() for c in consentimientos])
