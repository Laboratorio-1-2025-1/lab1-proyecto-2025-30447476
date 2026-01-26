"""Router: Planes de Cobertura"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from database import get_db
from models.aseguradoras import PlanCobertura
from schemas.base import ResponseSchema

router_planes = APIRouter(prefix="/planes", tags=["Planes de Cobertura"])

@router_planes.post("/")
def crear_plan(
    aseguradora_id: int,
    nombre: str,
    codigo: str,
    cobertura_porcentaje: Optional[float] = None,
    condiciones_generales: Optional[str] = None,
    vigente_desde: date = None,
    vigente_hasta: Optional[date] = None,
    db: Session = Depends(get_db)
):
    # Validar código único
    existe = db.query(PlanCobertura).filter(PlanCobertura.codigo == codigo).first()
    if existe:
        raise HTTPException(status_code=400, detail="Código de plan ya existe")
    
    plan = PlanCobertura(
        aseguradora_id=aseguradora_id,
        nombre=nombre,
        codigo=codigo,
        cobertura_porcentaje=cobertura_porcentaje,
        condiciones_generales=condiciones_generales,
        vigente_desde=vigente_desde or date.today(),
        vigente_hasta=vigente_hasta
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return ResponseSchema(success=True, message="Plan creado", data=plan.to_dict())

@router_planes.get("/")
def listar_planes(
    aseguradora_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(PlanCobertura)
    if aseguradora_id:
        query = query.filter(PlanCobertura.aseguradora_id == aseguradora_id)
    
    planes = query.all()
    return ResponseSchema(success=True, data=[p.to_dict() for p in planes])