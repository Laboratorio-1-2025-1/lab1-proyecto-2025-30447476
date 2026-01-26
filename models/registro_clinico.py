"""
Módulo 2.3: Registro clínico (historia y episodios)
- EpisodioAtencion: contenedor por motivo/proceso
- NotaClinica: registros SOAP
- Diagnostico: códigos CIE-10
- Consentimiento: aceptación informada
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class TipoEpisodioEnum(str, enum.Enum):
    """Tipos de episodio de atención"""
    CONSULTA = "CONSULTA"
    PROCEDIMIENTO = "PROCEDIMIENTO"
    CONTROL = "CONTROL"
    URGENCIA_AMBULATORIA = "URGENCIA_AMBULATORIA"
    HOSPITALIZACION = "HOSPITALIZACION"


class EstadoEpisodioEnum(str, enum.Enum):
    """Estados de episodios"""
    ABIERTO = "ABIERTO"
    CERRADO = "CERRADO"
    SUSPENDIDO = "SUSPENDIDO"


class TipoDiagnosticoEnum(str, enum.Enum):
    """Tipos de diagnóstico"""
    PRESUNTIVO = "PRESUNTIVO"
    DEFINITIVO = "DEFINITIVO"
    DIFERENCIAL = "DIFERENCIAL"


class MetodoConsentimientoEnum(str, enum.Enum):
    """Métodos de obtención de consentimiento"""
    FIRMA_DIGITAL = "FIRMA_DIGITAL"
    ACEPTACION_VERBAL = "ACEPTACION_VERBAL"
    FIRMA_FISICA_ESCANEADA = "FIRMA_FISICA_ESCANEADA"


class EpisodioAtencion(BaseModel):
    """
    Modelo 2.3.1: Episodios de Atención
    Contenedor de proceso asistencial completo
    REGLA DE NEGOCIO: Solo puede cerrarse si no hay órdenes en curso
    """
    __tablename__ = "episodios_atencion"
    
    # Relación
    persona_id = Column(Integer, ForeignKey("personas_atendidas.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos del episodio
    fecha_apertura = Column(DateTime(timezone=True), nullable=False, index=True)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)
    motivo = Column(String(255), nullable=False)
    tipo = Column(Enum(TipoEpisodioEnum), nullable=False)
    estado = Column(Enum(EstadoEpisodioEnum), default=EstadoEpisodioEnum.ABIERTO, nullable=False, index=True)
    
    # Resumen
    resumen_final = Column(Text, nullable=True)
    
    # Relaciones
    persona = relationship("PersonaAtendida", back_populates="episodios")
    notas_clinicas = relationship("NotaClinica", back_populates="episodio", cascade="all, delete-orphan")
    diagnosticos = relationship("Diagnostico", back_populates="episodio", cascade="all, delete-orphan")
    ordenes = relationship("Orden", back_populates="episodio", cascade="all, delete-orphan")
    prescripciones = relationship("Prescripcion", back_populates="episodio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EpisodioAtencion(id={self.id}, persona_id={self.persona_id}, tipo={self.tipo.value})>"


class NotaClinica(BaseModel):
    """
    Modelo 2.3.2: Notas Clínicas (Registro SOAP)
    Progreso médico con versionado
    REGLA DE NEGOCIO: No sobrescribir, crear nueva versión
    """
    __tablename__ = "notas_clinicas"
    
    # Relaciones
    episodio_id = Column(Integer, ForeignKey("episodios_atencion.id", ondelete="CASCADE"), nullable=False, index=True)
    profesional_id = Column(Integer, ForeignKey("profesionales.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos de la nota
    fecha = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # SOAP
    subjetivo = Column(Text, nullable=True, comment="Síntomas reportados por paciente")
    objetivo = Column(Text, nullable=True, comment="Hallazgos del examen físico")
    analisis = Column(Text, nullable=True, comment="Evaluación e interpretación")
    plan = Column(Text, nullable=True, comment="Plan de tratamiento")
    
    # Adjuntos y versionado
    adjuntos = Column(JSON, nullable=True, comment="Lista de archivos adjuntos")
    version = Column(Integer, nullable=False, default=1)
    nota_padre_id = Column(Integer, ForeignKey("notas_clinicas.id", ondelete="SET NULL"), nullable=True)
    
    # Relaciones
    episodio = relationship("EpisodioAtencion", back_populates="notas_clinicas")
    profesional = relationship("Profesional", back_populates="notas_clinicas")
    versiones_hijas = relationship("NotaClinica", remote_side=[nota_padre_id])
    
    def __repr__(self):
        return f"<NotaClinica(id={self.id}, episodio_id={self.episodio_id}, version={self.version})>"


class Diagnostico(BaseModel):
    """
    Modelo 2.3.3: Diagnósticos
    Códigos estandarizados CIE-10
    REGLA DE NEGOCIO: Solo un diagnóstico principal por episodio
    """
    __tablename__ = "diagnosticos"
    
    # Relación
    episodio_id = Column(Integer, ForeignKey("episodios_atencion.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos del diagnóstico
    codigo = Column(String(20), nullable=False, index=True, comment="Código CIE-10")
    descripcion = Column(String(500), nullable=False)
    tipo = Column(Enum(TipoDiagnosticoEnum), nullable=False)
    principal = Column(Boolean, default=False, nullable=False, index=True)
    
    # Observaciones
    notas = Column(Text, nullable=True)
    
    # Relaciones
    episodio = relationship("EpisodioAtencion", back_populates="diagnosticos")
    
    def __repr__(self):
        return f"<Diagnostico(id={self.id}, codigo={self.codigo}, principal={self.principal})>"


class Consentimiento(BaseModel):
    """
    Modelo 2.3.4: Consentimientos Informados
    Aceptación de procedimientos
    """
    __tablename__ = "consentimientos"
    
    # Relación
    persona_id = Column(Integer, ForeignKey("personas_atendidas.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos del consentimiento
    tipo_procedimiento = Column(String(255), nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=False, index=True)
    metodo = Column(Enum(MetodoConsentimientoEnum), nullable=False)
    
    # Archivo adjunto
    archivo_id = Column(String(255), nullable=True, comment="ID o ruta del archivo")
    
    # Detalles
    descripcion = Column(Text, nullable=True)
    riesgos_explicados = Column(Text, nullable=True)
    
    # Relaciones
    persona = relationship("PersonaAtendida", back_populates="consentimientos")
    
    def __repr__(self):
        return f"<Consentimiento(id={self.id}, persona_id={self.persona_id}, tipo={self.tipo_procedimiento})>"