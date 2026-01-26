"""Router: Prescripciones (Recetas)"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.ordenes import Prescripcion
from schemas.base import ResponseSchema

router_prescripciones = APIRouter(prefix="/prescripciones", tags=["Prescripciones"])

@router_prescripciones.post("/")
def crear_prescripcion(
    episodio_id: int,
    items: list,
    observaciones: str = None,
    db: Session = Depends(get_db)
):
    """
    items = [
        {
            "medicamentoCodigo": "MED001",
            "nombre": "Paracetamol",
            "dosis": "500mg",
            "via": "oral",
            "frecuencia": "cada 8 horas",
            "duracion": "7 días"
        }
    ]
    """
    prescripcion = Prescripcion(
        episodio_id=episodio_id,
        fecha_emision=datetime.utcnow(),
        items=items,
        observaciones=observaciones,
        vigente=True
    )
    db.add(prescripcion)
    db.commit()
    db.refresh(prescripcion)
    return ResponseSchema(success=True, message="Prescripción creada", data=prescripcion.to_dict())

@router_prescripciones.get("/episodio/{episodio_id}")
def listar_prescripciones_episodio(episodio_id: int, db: Session = Depends(get_db)):
    prescripciones = db.query(Prescripcion).filter(Prescripcion.episodio_id == episodio_id).all()
    return ResponseSchema(success=True, data=[p.to_dict() for p in prescripciones])
