
"""Endpoints para PersonasAtendidas"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.persona_atendida import PersonaAtendidaCreate, PersonaAtendidaUpdate, PersonaAtendidaResponse
from services.persona_atendida_service import PersonaAtendidaService
from middleware.jwt_middleware import get_current_user, require_roles
from typing import List, Optional

router = APIRouter(prefix="/personas", tags=["Personas Atendidas"])

@router.post("/", response_model=PersonaAtendidaResponse, status_code=201)
def crear_persona(
    persona: PersonaAtendidaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["administracion", "profesional"]))
):
    """Crear nueva persona atendida"""
    return PersonaAtendidaService.create(db, persona)

@router.get("/", response_model=List[PersonaAtendidaResponse])
def listar_personas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    documento: Optional[str] = None,
    edad_min: Optional[int] = None,
    edad_max: Optional[int] = None,
    sexo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Listar personas con filtros y paginación"""
    return PersonaAtendidaService.get_all(
        db, skip, limit, documento, edad_min, edad_max, sexo
    )

@router.get("/{persona_id}", response_model=PersonaAtendidaResponse)
def obtener_persona(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtener persona por ID"""
    return PersonaAtendidaService.get_by_id(db, persona_id)

@router.patch("/{persona_id}", response_model=PersonaAtendidaResponse)
def actualizar_persona(
    persona_id: int,
    persona_data: PersonaAtendidaUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["administracion", "profesional"]))
):
    """Actualizar datos de persona"""
    return PersonaAtendidaService.update(db, persona_id, persona_data)

@router.delete("/{persona_id}")
def eliminar_persona(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["administracion"]))
):
    """Desactivar persona (eliminación lógica)"""
    return PersonaAtendidaService.delete(db, persona_id)