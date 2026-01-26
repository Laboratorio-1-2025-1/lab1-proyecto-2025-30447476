# app/routers/agenda.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.agenda import Agenda
from schemas.agenda import AgendaBase, AgendaResponse

router = APIRouter(
    prefix="/agenda",
    tags=["2.2 Disponibilidad - Agenda"]
)

# ----------------- Funciones CRUD Básicas -----------------

def create_agenda_block(db: Session, agenda: AgendaBase):
    # Regla de negocio: Asegurar inicio < fin (Validación Pydantic o en servicio)
    if agenda.inicio >= agenda.fin:
        raise HTTPException(status_code=400, detail="La hora de inicio debe ser anterior a la hora de fin.")
        
    db_agenda = Agenda(**agenda.model_dump())
    db.add(db_agenda)
    try:
        db.commit()
        db.refresh(db_agenda)
        return db_agenda
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Error de conflicto: Bloque de agenda ya existe para ese profesional en ese horario.")

# ----------------- Endpoints -----------------

@router.post("/", response_model=AgendaResponse, status_code=status.HTTP_201_CREATED)
def crear_bloque_agenda(agenda: AgendaBase, db: Session = Depends(get_db)):
    return create_agenda_block(db, agenda)

@router.get("/", response_model=List[AgendaResponse])
def listar_bloques_agenda(db: Session = Depends(get_db)):
    return db.query(Agenda).all()