"""
Schemas base de Pydantic para validación
Define esquemas comunes y respuestas estándar
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Any
from datetime import datetime, date


class BaseSchema(BaseModel):
    """Schema base con configuración común"""
    model_config = ConfigDict(from_attributes=True)


class ResponseSchema(BaseSchema):
    """Schema estándar de respuesta"""
    success: bool = True
    message: str = "Operación exitosa"
    data: Optional[Any] = None


class ErrorDetail(BaseSchema):
    """Detalle de error"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseSchema):
    """Respuesta de error estandarizada"""
    success: bool = False
    message: str
    code: str
    details: Optional[List[ErrorDetail]] = None


class PaginationParams(BaseSchema):
    """Parámetros de paginación"""
    page: int = Field(1, ge=1, description="Número de página")
    page_size: int = Field(20, ge=1, le=100, description="Tamaño de página")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseSchema):
    """Respuesta paginada"""
    success: bool = True
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# Schemas de auditoría comunes
class AuditInfo(BaseSchema):
    """Información de auditoría"""
    created_at: datetime
    updated_at: datetime
    is_active: bool = True