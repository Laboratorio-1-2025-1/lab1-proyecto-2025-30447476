"""Router: Prestaciones (Catálogo) - Módulo 2.6"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.catalogo import Prestacion, GrupoPrestacionEnum
from schemas.base import ResponseSchema

router_prestaciones = APIRouter(prefix="/prestaciones", tags=["Prestaciones"])

@router_prestaciones.post("/")
def crear_prestacion(
    codigo: str,
    nombre: str,
    grupo: GrupoPrestacionEnum,
    descripcion: Optional[str] = None,
    requisitos: Optional[str] = None,
    requiere_autorizacion: bool = False,
    tiempo_estimado: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # Validar código único
    existe = db.query(Prestacion).filter(Prestacion.codigo == codigo).first()
    if existe:
        raise HTTPException(status_code=400, detail="Código ya existe")
    
    prestacion = Prestacion(
        codigo=codigo,
        nombre=nombre,
        descripcion=descripcion,
        grupo=grupo,
        requisitos=requisitos,
        requiere_autorizacion=requiere_autorizacion,
        tiempo_estimado=tiempo_estimado,
        vigente=True
    )
    db.add(prestacion)
    db.commit()
    db.refresh(prestacion)
    return ResponseSchema(success=True, message="Prestación creada", data=prestacion.to_dict())

@router_prestaciones.get("/")
def listar_prestaciones(
    grupo: Optional[GrupoPrestacionEnum] = None,
    vigente: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Prestacion)
    if grupo:
        query = query.filter(Prestacion.grupo == grupo)
    if vigente is not None:
        query = query.filter(Prestacion.vigente == vigente)
    
    prestaciones = query.all()
    return ResponseSchema(success=True, data=[p.to_dict() for p in prestaciones])
