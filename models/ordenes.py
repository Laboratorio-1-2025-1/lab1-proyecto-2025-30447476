"""
Módulo 2.4: Órdenes y prestaciones
- Orden: exámenes, imágenes, procedimientos
- OrdenItem: detalle de cada orden
- Prescripcion: medicamentos e insumos
- Resultado: actas y resultados de órdenes
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Text, JSON, Numeric, Boolean
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class TipoOrdenEnum(str, enum.Enum):
    """Tipos de órdenes médicas"""
    LABORATORIO = "LABORATORIO"
    IMAGEN = "IMAGEN"
    PROCEDIMIENTO = "PROCEDIMIENTO"
    INTERCONSULTA = "INTERCONSULTA"


class PrioridadOrdenEnum(str, enum.Enum):
    """Prioridad de ejecución"""
    NORMAL = "NORMAL"
    URGENTE = "URGENTE"
    EMERGENCIA = "EMERGENCIA"


class EstadoOrdenEnum(str, enum.Enum):
    """Estados de órdenes"""
    EMITIDA = "EMITIDA"
    AUTORIZADA = "AUTORIZADA"
    EN_CURSO = "EN_CURSO"
    COMPLETADA = "COMPLETADA"
    ANULADA = "ANULADA"


class Orden(BaseModel):
    """
    Modelo 2.4.1: Órdenes Médicas
    Solicitudes de exámenes, imágenes, procedimientos
    """
    __tablename__ = "ordenes"
    
    # Relación
    episodio_id = Column(Integer, ForeignKey("episodios_atencion.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos de la orden
    tipo = Column(Enum(TipoOrdenEnum), nullable=False)
    prioridad = Column(Enum(PrioridadOrdenEnum), default=PrioridadOrdenEnum.NORMAL, nullable=False)
    estado = Column(Enum(EstadoOrdenEnum), default=EstadoOrdenEnum.EMITIDA, nullable=False, index=True)
    
    # Fechas
    fecha_emision = Column(DateTime(timezone=True), nullable=False, index=True)
    fecha_autorizacion = Column(DateTime(timezone=True), nullable=True)
    fecha_completado = Column(DateTime(timezone=True), nullable=True)
    
    # Observaciones
    indicaciones_generales = Column(Text, nullable=True)
    
    # Relaciones
    episodio = relationship("EpisodioAtencion", back_populates="ordenes")
    items = relationship("OrdenItem", back_populates="orden", cascade="all, delete-orphan")
    resultados = relationship("Resultado", back_populates="orden", cascade="all, delete-orphan")
    autorizaciones = relationship("Autorizacion", back_populates="orden", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Orden(id={self.id}, tipo={self.tipo.value}, estado={self.estado.value})>"


class OrdenItem(BaseModel):
    """
    Modelo 2.4.2: Items de Orden
    Detalle específico de cada examen/procedimiento solicitado
    """
    __tablename__ = "orden_items"
    
    # Relación
    orden_id = Column(Integer, ForeignKey("ordenes.id", ondelete="CASCADE"), nullable=False, index=True)
    prestacion_codigo = Column(String(50), ForeignKey("prestaciones.codigo", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Detalles
    descripcion = Column(String(500), nullable=False)
    indicaciones = Column(Text, nullable=True)
    cantidad = Column(Integer, default=1, nullable=False)
    
    # Relaciones
    orden = relationship("Orden", back_populates="items")
    prestacion = relationship("Prestacion")
    
    def __repr__(self):
        return f"<OrdenItem(id={self.id}, orden_id={self.orden_id}, codigo={self.prestacion_codigo})>"


class Prescripcion(BaseModel):
    """
    Modelo 2.4.3: Prescripciones (Medicamentos)
    Recetas médicas
    """
    __tablename__ = "prescripciones"
    
    # Relación
    episodio_id = Column(Integer, ForeignKey("episodios_atencion.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos generales
    fecha_emision = Column(DateTime(timezone=True), nullable=False, index=True)
    observaciones = Column(Text, nullable=True)
    
    # Items de prescripción (JSON array)
    items = Column(JSON, nullable=False, comment="[{medicamentoCodigo, nombre, dosis, via, frecuencia, duracion}]")
    
    # Control
    vigente = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    episodio = relationship("EpisodioAtencion", back_populates="prescripciones")
    
    def __repr__(self):
        return f"<Prescripcion(id={self.id}, episodio_id={self.episodio_id})>"


class Resultado(BaseModel):
    """
    Modelo 2.4.4: Resultados de Órdenes
    Actas de exámenes, imágenes, procedimientos con versionado
    """
    __tablename__ = "resultados"
    
    # Relación
    orden_id = Column(Integer, ForeignKey("ordenes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos del resultado
    fecha = Column(DateTime(timezone=True), nullable=False, index=True)
    resumen = Column(Text, nullable=True)
    
    # Archivo
    archivo_id = Column(String(255), nullable=True, comment="ID o ruta del archivo de resultado")
    
    # Versionado
    version = Column(Integer, nullable=False, default=1)
    resultado_padre_id = Column(Integer, ForeignKey("resultados.id", ondelete="SET NULL"), nullable=True)
    
    # Validación profesional
    validado_por_id = Column(Integer, ForeignKey("profesionales.id", ondelete="SET NULL"), nullable=True)
    fecha_validacion = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    orden = relationship("Orden", back_populates="resultados")
    versiones_hijas = relationship("Resultado", remote_side=[resultado_padre_id])
    validado_por = relationship("Profesional")
    
    def __repr__(self):
        return f"<Resultado(id={self.id}, orden_id={self.orden_id}, version={self.version})>"