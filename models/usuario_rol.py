"""Tabla intermedia Usuario-Rol"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UsuarioRol(Base):
    __tablename__ = "usuario_rol"
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="roles")
    rol = relationship("Rol", back_populates="usuarios")