"""
Schemas del Módulo 2.1: Identidades
PersonaAtendida, Profesional, UnidadAtencion
"""
from pydantic import EmailStr, Field, field_validator
from typing import Optional, List, Dict
from datetime import date
from schemas.base import BaseSchema, AuditInfo
from models.identidades import TipoDocumentoEnum, SexoEnum, EstadoGeneralEnum, TipoUnidadEnum


# ==================== PERSONA ATENDIDA ====================

class PersonaAtendidaBase(BaseSchema):
    """Schema base de Persona Atendida"""
    tipo_documento: TipoDocumentoEnum
    numero_documento: str = Field(..., min_length=5, max_length=50)
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    fecha_nacimiento: date
    sexo: SexoEnum
    correo: EmailStr
    telefono: str = Field(..., pattern=r"^\+?[\d\s\-\(\)]+$")
    direccion: str = Field(..., min_length=5, max_length=255)
    contacto_emergencia: str = Field(..., min_length=5, max_length=100)
    alergias: Optional[List[str]] = None
    antecedentes_resumen: Optional[str] = None
    estado: EstadoGeneralEnum = EstadoGeneralEnum.ACTIVO


class PersonaAtendidaCreate(PersonaAtendidaBase):
    """Schema para crear Persona Atendida"""
    pass


class PersonaAtendidaUpdate(BaseSchema):
    """Schema para actualizar Persona Atendida"""
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    alergias: Optional[List[str]] = None
    antecedentes_resumen: Optional[str] = None
    estado: Optional[EstadoGeneralEnum] = None


class PersonaAtendidaResponse(PersonaAtendidaBase, AuditInfo):
    """Schema de respuesta de Persona Atendida"""
    id: int


# ==================== PROFESIONAL ====================

class ProfesionalBase(BaseSchema):
    """Schema base de Profesional"""
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    registro_profesional: str = Field(..., min_length=3, max_length=50)
    especialidad: str = Field(..., min_length=3, max_length=100)
    correo: EmailStr
    telefono: str = Field(..., pattern=r"^\+?[\d\s\-\(\)]+$")
    agenda_habilitada: bool = True
    estado: EstadoGeneralEnum = EstadoGeneralEnum.ACTIVO


class ProfesionalCreate(ProfesionalBase):
    """Schema para crear Profesional"""
    pass


class ProfesionalUpdate(BaseSchema):
    """Schema para actualizar Profesional"""
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    especialidad: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    agenda_habilitada: Optional[bool] = None
    estado: Optional[EstadoGeneralEnum] = None


class ProfesionalResponse(ProfesionalBase, AuditInfo):
    """Schema de respuesta de Profesional"""
    id: int


# ==================== UNIDAD ATENCION ====================

class UnidadAtencionBase(BaseSchema):
    """Schema base de Unidad de Atención"""
    nombre: str = Field(..., min_length=3, max_length=150)
    tipo: TipoUnidadEnum
    direccion: str = Field(..., min_length=5, max_length=255)
    telefono: str = Field(..., pattern=r"^\+?[\d\s\-\(\)]+$")
    horario_referencia: Optional[Dict] = None
    estado: EstadoGeneralEnum = EstadoGeneralEnum.ACTIVO


class UnidadAtencionCreate(UnidadAtencionBase):
    """Schema para crear Unidad de Atención"""
    pass


class UnidadAtencionUpdate(BaseSchema):
    """Schema para actualizar Unidad de Atención"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=150)
    tipo: Optional[TipoUnidadEnum] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    horario_referencia: Optional[Dict] = None
    estado: Optional[EstadoGeneralEnum] = None


class UnidadAtencionResponse(UnidadAtencionBase, AuditInfo):
    """Schema de respuesta de Unidad de Atención"""
    id: int