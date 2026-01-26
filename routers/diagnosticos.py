"""
Router: Diagnósticos - Módulo 2.3
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.registro_clinico import Diagnostico, TipoDiagnosticoEnum
from schemas.base import ResponseSchema

router_diagnosticos = APIRouter(prefix="/diagnosticos", tags=["Diagnósticos"])

@router_diagnosticos.post("/", status_code=status.HTTP_201_CREATED)
def crear_diagnostico(
    episodio_id: int,
    codigo: str,
    descripcion: str,
    tipo: TipoDiagnosticoEnum,
    principal: bool = False,
    notas: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """REGLA DE NEGOCIO: Solo un diagnóstico principal por episodio"""
    if principal:
        # Verificar que no exista otro diagnóstico principal
        existe_principal = db.query(Diagnostico).filter(
            Diagnostico.episodio_id == episodio_id,
            Diagnostico.principal == True
        ).first()
        
        if existe_principal:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un diagnóstico principal en este episodio"
            )
    
    diagnostico = Diagnostico(
        episodio_id=episodio_id,
        codigo=codigo,
        descripcion=descripcion,
        tipo=tipo,
        principal=principal,
        notas=notas
    )
    db.add(diagnostico)
    db.commit()
    db.refresh(diagnostico)
    return ResponseSchema(success=True, message="Diagnóstico creado", data=diagnostico.to_dict())

@router_diagnosticos.get("/episodio/{episodio_id}")
def listar_diagnosticos_episodio(episodio_id: int, db: Session = Depends(get_db)):
    diagnosticos = db.query(Diagnostico).filter(Diagnostico.episodio_id == episodio_id).all()
    return ResponseSchema(success=True, data=[d.to_dict() for d in diagnosticos])
