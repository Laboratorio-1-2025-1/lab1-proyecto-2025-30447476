# app/models/unidad.py
from sqlalchemy import Column, Integer, String, Enum
from models.base import Base

class UnidadAtencion(Base):
    """Corresponde a la entidad UnidadesAtencion - Sección 2.1/2.2"""
    __tablename__ = 'UnidadesAtencion'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(Enum('sede', 'consultorio', 'servicio'), nullable=False)
    direccion = Column(String(255))
    telefono = Column(String(20))
    horarioReferencia = Column(String(255))
    estado = Column(Enum('activo', 'inactivo'), default='activo', nullable=False)