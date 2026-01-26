from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database import Base

class Servicio(Base):
    """Modelo para la tabla de servicios médicos"""
    __tablename__ = "servicios"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    duracion_minutos = Column(Integer, nullable=False, default=30)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Servicio(id={self.id}, nombre='{self.nombre}', precio={self.precio})>"
