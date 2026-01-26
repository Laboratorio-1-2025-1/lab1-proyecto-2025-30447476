# app/models/profesional.py
from sqlalchemy import Column, Integer, String, Enum, Boolean
from models.base import Base

class Profesional(Base):
    """Corresponde a la entidad Profesionales - Sección 2.1/2.2"""
    __tablename__ = 'Profesionales'

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    registroProfesional = Column(String(50), unique=True, nullable=False)
    especialidad = Column(String(100))
    correo = Column(String(100))
    telefono = Column(String(20))
    agendaHabilitada = Column(Boolean, default=True)
    estado = Column(Enum('activo', 'inactivo'), default='activo', nullable=False)