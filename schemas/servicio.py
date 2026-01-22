from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# ============================================
# SCHEMAS PARA SERVICIOS
# ============================================

class ServicioBase(BaseModel):
    """Schema base para Servicio"""
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: float = Field(..., gt=0)
    duracion_minutos: int = Field(default=30, gt=0)
    activo: bool = True

class ServicioCreate(ServicioBase):
    """Schema para crear un servicio"""
    pass

class ServicioUpdate(BaseModel):
    """Schema para actualizar un servicio"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(None, gt=0)
    duracion_minutos: Optional[int] = Field(None, gt=0)
    activo: Optional[bool] = None

class ServicioResponse(ServicioBase):
    """Schema de respuesta para Servicio"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS PARA PACIENTES
# ============================================

class PacienteBase(BaseModel):
    """Schema base para Paciente"""
    cedula: str = Field(..., min_length=5, max_length=20)
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    fecha_nacimiento: Optional[datetime] = None
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: bool = True

class PacienteCreate(PacienteBase):
    """Schema para crear un paciente"""
    pass

class PacienteUpdate(BaseModel):
    """Schema para actualizar un paciente"""
    cedula: Optional[str] = Field(None, min_length=5, max_length=20)
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    fecha_nacimiento: Optional[datetime] = None
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None

class PacienteResponse(PacienteBase):
    """Schema de respuesta para Paciente"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS PARA CITAS
# ============================================

class CitaBase(BaseModel):
    """Schema base para Cita"""
    paciente_id: int = Field(..., gt=0)
    servicio_id: int = Field(..., gt=0)
    fecha_hora: datetime
    estado: str = Field(default="programada", max_length=20)
    observaciones: Optional[str] = None

class CitaCreate(CitaBase):
    """Schema para crear una cita"""
    pass

class CitaUpdate(BaseModel):
    """Schema para actualizar una cita"""
    paciente_id: Optional[int] = Field(None, gt=0)
    servicio_id: Optional[int] = Field(None, gt=0)
    fecha_hora: Optional[datetime] = None
    estado: Optional[str] = Field(None, max_length=20)
    observaciones: Optional[str] = None

class CitaResponse(CitaBase):
    """Schema de respuesta para Cita"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS GENÉRICOS
# ============================================

class MessageResponse(BaseModel):
    """Schema para mensajes de respuesta"""
    message: str
    status: str = "success"

class ErrorResponse(BaseModel):
    """Schema para errores"""
    detail: str
    status: str = "error"
