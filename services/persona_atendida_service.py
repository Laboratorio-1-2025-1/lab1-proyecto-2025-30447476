"""Servicio de PersonasAtendidas"""
from sqlalchemy.orm import Session
from models.persona_atendida import PersonaAtendida
from schemas.persona_atendida import PersonaAtendidaCreate, PersonaAtendidaUpdate
from fastapi import HTTPException, status
from typing import Optional

class PersonaAtendidaService:
    
    @staticmethod
    def create(db: Session, persona_data: PersonaAtendidaCreate):
        """Crear nueva persona atendida"""
        # Verificar documento único
        existing = db.query(PersonaAtendida).filter(
            PersonaAtendida.numero_documento == persona_data.numero_documento
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de documento ya registrado"
            )
        
        persona = PersonaAtendida(**persona_data.model_dump())
        db.add(persona)
        db.commit()
        db.refresh(persona)
        return persona
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, 
                documento: Optional[str] = None, 
                edad_min: Optional[int] = None,
                edad_max: Optional[int] = None,
                sexo: Optional[str] = None):
        """Listar personas con filtros"""
        query = db.query(PersonaAtendida)
        
        if documento:
            query = query.filter(PersonaAtendida.numero_documento.contains(documento))
        if sexo:
            query = query.filter(PersonaAtendida.sexo == sexo)
        # Filtros de edad requieren cálculo...
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, persona_id: int):
        """Obtener persona por ID"""
        persona = db.query(PersonaAtendida).filter(PersonaAtendida.id == persona_id).first()
        if not persona:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona no encontrada"
            )
        return persona
    
    @staticmethod
    def update(db: Session, persona_id: int, persona_data: PersonaAtendidaUpdate):
        """Actualizar persona"""
        persona = PersonaAtendidaService.get_by_id(db, persona_id)
        
        for field, value in persona_data.model_dump(exclude_unset=True).items():
            setattr(persona, field, value)
        
        db.commit()
        db.refresh(persona)
        return persona
    
    @staticmethod
    def delete(db: Session, persona_id: int):
        """Eliminación lógica"""
        persona = PersonaAtendidaService.get_by_id(db, persona_id)
        persona.estado = "inactivo"
        db.commit()
        return {"message": "Persona desactivada"}