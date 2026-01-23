"""Modelo de Persona Atendida (Paciente)"""
from sqlalchemy import Column, Integer, String, Date, Text, JSON
from sqlalchemy.orm import relationship
from database import Base

class PersonaAtendida(Base):
    __tablename__ = "personas_atendidas"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_documento = Column(String(20), nullable=False)  # CI, Pasaporte, etc.
    numero_documento = Column(String(50), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(String(10), nullable=False)  # M, F, Otro
    correo = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    direccion = Column(Text, nullable=True)
    contacto_emergencia = Column(JSON, nullable=True)  # {nombre, telefono, relacion}
    alergias = Column(JSON, nullable=True)  # Lista de alergias
    antecedentes_resumen = Column(Text, nullable=True)
    estado = Column(String(20), default="activo")  # activo, inactivo
    
    # Relaciones
    citas = relationship("Cita", back_populates="persona")
    episodios = relationship("EpisodioAtencion", back_populates="persona")
    afiliaciones = relationship("Afiliacion", back_populates="persona")