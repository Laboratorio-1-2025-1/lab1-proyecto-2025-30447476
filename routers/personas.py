from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.repositories import persona_repo
from app.schemas.persona import PersonaCreate, PersonaResponse # Pydantic Schemas

router = APIRouter(prefix="/personas", tags=["Identidades"])

@router.post("/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
def create_persona_atendida(persona: PersonaCreate, db: Session = Depends(get_db)):
    # Lógica de servicio/negocio (ej: validar documento único)
    if persona_repo.get_persona_by_document(db, persona.numeroDocumento):
        raise HTTPException(status_code=400, detail="Documento ya registrado")
    return persona_repo.create_persona(db=db, persona=persona)

@router.get("/{persona_id}", response_model=PersonaResponse)
def read_persona_atendida(persona_id: int, db: Session = Depends(get_db)):
    db_persona = persona_repo.get_persona(db, persona_id=persona_id)
    if db_persona is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return db_persona

# Implementar rutas para GET list (con filtros), PATCH (cambios) y DELETE lógico [cite: 100]