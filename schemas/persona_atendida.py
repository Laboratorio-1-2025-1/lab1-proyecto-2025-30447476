"""Schemas para PersonaAtendida"""
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, List, Dict

class ContactoEmergencia(BaseModel):
    nombre: str
    telefono: str
    relacion: str

class PersonaAtendidaBase(BaseModel):
    tipo_documento: str = Field(..., example="CI")
    numero_documento: str = Field(..., example="12345678")
    nombres: str = Field(..., example="Juan Carlos")
    apellidos: str = Field(..., example="Pérez González")
    fecha_nacimiento: date
    sexo: str = Field(..., example="M")
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    contacto_emergencia: Optional[ContactoEmergencia] = None
    alergias: Optional[List[str]] = []
    antecedentes_resumen: Optional[str] = None

class PersonaAtendidaCreate(PersonaAtendidaBase):
    pass

class PersonaAtendidaUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    contacto_emergencia: Optional[ContactoEmergencia] = None
    alergias: Optional[List[str]] = None
    antecedentes_resumen: Optional[str] = None
    estado: Optional[str] = None

class PersonaAtendidaResponse(PersonaAtendidaBase):
    id: int
    estado: str
    
    class Config:
        from_attributes = True