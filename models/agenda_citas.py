"""
Módulo 2.2: Disponibilidad y citas
- BloqueAgenda: bloques de tiempo publicables
- Cita: gestión completa de citas médicas
- HistorialCita: trazabilidad de cambios
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class EstadoBloqueEnum(str, enum.Enum):
    """Estados de bloques de agenda"""
    ABIERTO = "ABIERTO"
    CERRADO = "CERRADO"
    RESERVADO = "RESERVADO"
    BLOQUEADO = "BLOQUEADO"


class EstadoCitaEnum(str, enum.Enum):
    """Estados de citas"""
    SOLICITADA = "SOLICITADA"
    CONFIRMADA = "CONFIRMADA"
    CUMPLIDA = "CUMPLIDA"
    CANCELADA = "CANCELADA"
    NO_ASISTIDA = "NO_ASISTIDA"
    REPROGRAMADA = "REPROGRAMADA"


class CanalCitaEnum(str, enum.Enum):
    """Canales de atención"""
    PRESENCIAL = "PRESENCIAL"
    VIRTUAL = "VIRTUAL"
    TELEFONICA = "TELEFONICA"
    DOMICILIARIA = "DOMICILIARIA"


class BloqueAgenda(BaseModel):
    """
    Modelo 2.2.1: Bloques de Agenda
    Define disponibilidad de profesionales en unidades
    """
    __tablename__ = "bloques_agenda"
    
    # Relaciones
    profesional_id = Column(Integer, ForeignKey("profesionales.id", ondelete="CASCADE"), nullable=False, index=True)
    unidad_id = Column(Integer, ForeignKey("unidades_atencion.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tiempo
    inicio = Column(DateTime(timezone=True), nullable=False, index=True)
    fin = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Configuración
    capacidad = Column(Integer, nullable=False, default=1, comment="Número de citas simultáneas permitidas")
    estado = Column(Enum(EstadoBloqueEnum), default=EstadoBloqueEnum.ABIERTO, nullable=False)
    
    # Metadatos
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    profesional = relationship("Profesional", back_populates="bloques_agenda")
    unidad = relationship("UnidadAtencion", back_populates="bloques_agenda")
    citas = relationship("Cita", back_populates="bloque_agenda", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BloqueAgenda(id={self.id}, profesional_id={self.profesional_id}, inicio={self.inicio})>"


class Cita(BaseModel):
    """
    Modelo 2.2.2: Citas Médicas
    Gestiona agendamiento y atención de pacientes
    REGLA DE NEGOCIO: Debe pertenecer a bloque abierto y no exceder capacidad
    """
    __tablename__ = "citas"
    
    # Relaciones
    persona_id = Column(Integer, ForeignKey("personas_atendidas.id", ondelete="CASCADE"), nullable=False, index=True)
    profesional_id = Column(Integer, ForeignKey("profesionales.id", ondelete="CASCADE"), nullable=False, index=True)
    unidad_id = Column(Integer, ForeignKey("unidades_atencion.id", ondelete="CASCADE"), nullable=False, index=True)
    bloque_agenda_id = Column(Integer, ForeignKey("bloques_agenda.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Tiempo
    inicio = Column(DateTime(timezone=True), nullable=False, index=True)
    fin = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Detalles
    motivo = Column(String(255), nullable=False)
    canal = Column(Enum(CanalCitaEnum), default=CanalCitaEnum.PRESENCIAL, nullable=False)
    estado = Column(Enum(EstadoCitaEnum), default=EstadoCitaEnum.SOLICITADA, nullable=False, index=True)
    observaciones = Column(Text, nullable=True)
    
    # Información adicional
    datos_virtuales = Column(JSON, nullable=True, comment="Link de reunión, credenciales, etc.")
    
    # Relaciones
    persona = relationship("PersonaAtendida", back_populates="citas")
    profesional = relationship("Profesional", back_populates="citas")
    unidad = relationship("UnidadAtencion", back_populates="citas")
    bloque_agenda = relationship("BloqueAgenda", back_populates="citas")
    historial = relationship("HistorialCita", back_populates="cita", cascade="all, delete-orphan", order_by="HistorialCita.created_at")
    
    def __repr__(self):
        return f"<Cita(id={self.id}, persona_id={self.persona_id}, estado={self.estado.value})>"


class HistorialCita(BaseModel):
    """
    Modelo 2.2.3: Historial de Cambios de Cita
    Trazabilidad completa de modificaciones
    """
    __tablename__ = "historial_citas"
    
    # Relación
    cita_id = Column(Integer, ForeignKey("citas.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Cambios
    estado_anterior = Column(Enum(EstadoCitaEnum), nullable=True)
    estado_nuevo = Column(Enum(EstadoCitaEnum), nullable=False)
    accion = Column(String(50), nullable=False, comment="crear, confirmar, cancelar, reprogramar, marcar_no_asistida")
    motivo_cambio = Column(Text, nullable=True)
    
    # Auditoría
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    datos_adicionales = Column(JSON, nullable=True, comment="Fecha anterior si hubo reprogramación, etc.")
    
    # Relaciones
    cita = relationship("Cita", back_populates="historial")
    usuario = relationship("Usuario")
    
    def __repr__(self):
        return f"<HistorialCita(id={self.id}, cita_id={self.cita_id}, accion={self.accion})>"