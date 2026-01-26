"""Router: Arancel (Tarifas)"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from database import get_db
from models.catalogo import Arancel
from schemas.base import ResponseSchema

router_arancel = APIRouter(prefix="/arancel", tags=["Arancel"])

@router_arancel.post("/")
def crear_arancel(
    prestacion_codigo: str,
    valor_base: float,
    plan_id: Optional[int] = None,
    impuestos: float = 0,
    vigente_desde: date = None,
    vigente_hasta: Optional[date] = None,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db)
):
    arancel = Arancel(
        prestacion_codigo=prestacion_codigo,
        plan_id=plan_id,
        valor_base=valor_base,
        impuestos=impuestos,
        vigente_desde=vigente_desde or date.today(),
        vigente_hasta=vigente_hasta,
        observaciones=observaciones
    )
    db.add(arancel)
    db.commit()
    db.refresh(arancel)
    return ResponseSchema(success=True, message="Arancel creado", data=arancel.to_dict())

@router_arancel.get("/")
def listar_arancel(
    prestacion_codigo: Optional[str] = None,
    plan_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Arancel)
    if prestacion_codigo:
        query = query.filter(Arancel.prestacion_codigo == prestacion_codigo)
    if plan_id:
        query = query.filter(Arancel.plan_id == plan_id)
    
    arancel = query.all()
    return ResponseSchema(success=True, data=[a.to_dict() for a in arancel])