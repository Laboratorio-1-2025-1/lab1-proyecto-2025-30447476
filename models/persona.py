# app/models/persona.py
from sqlalchemy import Column, Integer, String, Date, Enum
from models.base import Base

class PersonaAtendida(Base):
    """Corresponde a la entidad PersonasAtendidas (Pacientes) - Sección 2.1"""
    __tablename__ = 'PersonasAtendidas'

    id = Column(Integer, primary_key=True, index=True)
    tipoDocumento = Column(String(10), nullable=False)
    numeroDocumento = Column(String(20), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fechaNacimiento = Column(Date, nullable=False)
    sexo = Column(Enum('M', 'F', 'Otro'), nullable=False)
    correo = Column(String(100))
    telefono = Column(String(20))
    direccion = Column(String(255))
    contactoEmergencia = Column(String(255))
    estado = Column(Enum('activo', 'inactivo'), default='activo', nullable=False)
    # Los opcionales (alergias/antecedentes) se omiten por simplicidad inicial, 
    # pero deben considerarse en la entrega final.