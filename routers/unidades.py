"""
Router: Unidades de Atención - Módulo 2.1
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.identidades import UnidadAtencion, TipoUnidadEnum, EstadoGeneralEnum
from schemas.base import ResponseSchema, PaginatedResponse

router_unidades = APIRouter(prefix="/unidades", tags=["Unidades de Atención"])

@router_unidades.post("/", status_code=status.HTTP_201_CREATED)
def crear_unidad(
    nombre: str,
    tipo: TipoUnidadEnum,
    direccion: str,
    telefono: str,
    horario_referencia: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    unidad = UnidadAtencion(
        nombre=nombre,
        tipo=tipo,
        direccion=direccion,
        telefono=telefono,
        horario_referencia=horario_referencia,
        estado=EstadoGeneralEnum.ACTIVO
    )
    db.add(unidad)
    db.commit()
    db.refresh(unidad)
    return ResponseSchema(success=True, message="Unidad creada", data=unidad.to_dict())

@router_unidades.get("/")
def listar_unidades(
    tipo: Optional[TipoUnidadEnum] = None,
    estado: Optional[EstadoGeneralEnum] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(UnidadAtencion)
    if tipo:
        query = query.filter(UnidadAtencion.tipo == tipo)
    if estado:
        query = query.filter(UnidadAtencion.estado == estado)
    
    total = query.count()
    unidades = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        success=True,
        data=[u.to_dict() for u in unidades],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router_unidades.get("/{unidad_id}")
def obtener_unidad(unidad_id: int, db: Session = Depends(get_db)):
    unidad = db.query(UnidadAtencion).filter(UnidadAtencion.id == unidad_id).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return ResponseSchema(success=True, data=unidad.to_dict())

@router_unidades.patch("/{unidad_id}")
def actualizar_unidad(
    unidad_id: int,
    nombre: Optional[str] = None,
    direccion: Optional[str] = None,
    telefono: Optional[str] = None,
    horario_referencia: Optional[dict] = None,
    estado: Optional[EstadoGeneralEnum] = None,
    db: Session = Depends(get_db)
):
    unidad = db.query(UnidadAtencion).filter(UnidadAtencion.id == unidad_id).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    
    if nombre:
        unidad.nombre = nombre
    if direccion:
        unidad.direccion = direccion
    if telefono:
        unidad.telefono = telefono
    if horario_referencia:
        unidad.horario_referencia = horario_referencia
    if estado:
        unidad.estado = estado
    
    db.commit()
    db.refresh(unidad)
    return ResponseSchema(success=True, message="Unidad actualizada", data=unidad.to_dict())

@router_unidades.delete("/{unidad_id}")
def eliminar_unidad(unidad_id: int, db: Session = Depends(get_db)):
    unidad = db.query(UnidadAtencion).filter(UnidadAtencion.id == unidad_id).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    
    unidad.estado = EstadoGeneralEnum.INACTIVO
    unidad.is_active = False
    db.commit()
    return ResponseSchema(success=True, message="Unidad eliminada")
