"""Modelo de Rol"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

class Rol(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)  # administracion, profesional, cajero, auditor
    descripcion = Column(Text, nullable=True)
    
    # Relaciones
    usuarios = relationship("UsuarioRol", back_populates="rol")
    permisos = relationship("RolPermiso", back_populates="rol")