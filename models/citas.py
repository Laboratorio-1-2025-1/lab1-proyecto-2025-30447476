# app/models/cita.py
from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.base import Base

class Cita(Base):
    """Corresponde a la entidad Citas - Sección 2.2"""
    __tablename__ = 'Citas'

    id = Column(Integer, primary_key=True, index=True)
    personaId = Column(Integer, ForeignKey('PersonasAtendidas.id'), nullable=False)
    profesionalId = Column(Integer, ForeignKey('Profesionales.id'), nullable=False)
    unidadId = Column(Integer, ForeignKey('UnidadesAtencion.id'), nullable=False)
    
    # Nota: No usamos AgendaId directamente para permitir flexibilidad, 
    # pero el servicio debe validar que caiga en un bloque de Agenda.
    inicio = Column(DateTime, nullable=False)
    fin = Column(DateTime, nullable=False)
    
    motivo = Column(String(255))
    canal = Column(Enum('presencial', 'virtual'), nullable=False)
    estado = Column(Enum('solicitada', 'confirmada', 'cumplida', 'cancelada', 'noAsistida'), 
                   default='solicitada', nullable=False)
    observaciones = Column(Text)

    # Relaciones
    persona = relationship("PersonaAtendida")
    profesional = relationship("Profesional")
    unidad = relationship("UnidadAtencion")