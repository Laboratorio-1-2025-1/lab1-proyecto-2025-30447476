"""Modelo de Usuario"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    estado = Column(String(20), default="activo")  # activo, inactivo, bloqueado
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    ultimo_acceso = Column(DateTime, nullable=True)
    
    # Relaciones
    roles = relationship("UsuarioRol", back_populates="usuario")
    bitacora = relationship("BitacoraAcceso", back_populates="usuario")