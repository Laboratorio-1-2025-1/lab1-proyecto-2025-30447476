"""
Módulo 2.5: Cobertura, autorizaciones y planes
- Aseguradora: entidades pagadoras
- PlanCobertura: planes de salud
- Afiliacion: persona-plan
- Autorizacion: aprobaciones de prestaciones
"""
from sqlalchemy import Column, String, Date, Integer, ForeignKey, Enum, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class EstadoAseguradoraEnum(str, enum.Enum):
    """Estados de aseguradoras"""
    ACTIVA = "ACTIVA"
    INACTIVA = "INACTIVA"
    SUSPENDIDA = "SUSPENDIDA"


class EstadoAutorizacionEnum(str, enum.Enum):
    """Estados de autorización"""
    SOLICITADA = "SOLICITADA"
    APROBADA = "APROBADA"
    NEGADA = "NEGADA"
    PENDIENTE_INFORMACION = "PENDIENTE_INFORMACION"
    EXPIRADA = "EXPIRADA"


class Aseguradora(BaseModel):
    """
    Modelo 2.5.1: Aseguradoras / Entidades Pagadoras
    EPS, seguros, medicina prepagada
    """
    __tablename__ = "aseguradoras"
    
    # Datos de la aseguradora
    nombre = Column(String(200), nullable=False)
    nit = Column(String(50), unique=True, nullable=False, index=True)
    contacto = Column(String(255), nullable=True)
    
    # Datos adicionales
    telefono = Column(String(20), nullable=True)
    correo = Column(String(100), nullable=True)
    direccion = Column(String(255), nullable=True)
    
    # Estado
    estado = Column(Enum(EstadoAseguradoraEnum), default=EstadoAseguradoraEnum.ACTIVA, nullable=False)
    
    # Relaciones
    planes = relationship("PlanCobertura", back_populates="aseguradora", cascade="all, delete-orphan")
    facturas = relationship("Factura", back_populates="aseguradora", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Aseguradora(id={self.id}, nombre={self.nombre}, nit={self.nit})>"


class PlanCobertura(BaseModel):
    """
    Modelo 2.5.2: Planes de Cobertura
    Planes de salud ofrecidos por aseguradoras
    """
    __tablename__ = "planes_cobertura"
    
    # Relación
    aseguradora_id = Column(Integer, ForeignKey("aseguradoras.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos del plan
    nombre = Column(String(200), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    
    # Condiciones
    condiciones_generales = Column(Text, nullable=True)
    cobertura_porcentaje = Column(Numeric(5, 2), nullable=True, comment="Porcentaje de cobertura general")
    
    # Vigencia
    vigente_desde = Column(Date, nullable=False)
    vigente_hasta = Column(Date, nullable=True)
    
    # Relaciones
    aseguradora = relationship("Aseguradora", back_populates="planes")
    afiliaciones = relationship("Afiliacion", back_populates="plan", cascade="all, delete-orphan")
    arancel = relationship("Arancel", back_populates="plan", cascade="all, delete-orphan")
    autorizaciones = relationship("Autorizacion", back_populates="plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PlanCobertura(id={self.id}, nombre={self.nombre}, codigo={self.codigo})>"


class Afiliacion(BaseModel):
    """
    Modelo 2.5.3: Afiliaciones Persona-Plan
    Vinculación de pacientes a planes de cobertura
    """
    __tablename__ = "afiliaciones"
    
    # Relaciones
    persona_id = Column(Integer, ForeignKey("personas_atendidas.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("planes_cobertura.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos de la afiliación
    numero_poliza = Column(String(100), unique=True, nullable=False, index=True)
    
    # Vigencia
    vigente_desde = Column(Date, nullable=False)
    vigente_hasta = Column(Date, nullable=True)
    
    # Condiciones económicas
    copago = Column(Numeric(10, 2), nullable=True, comment="Monto fijo por consulta")
    cuota_moderadora = Column(Numeric(5, 2), nullable=True, comment="Porcentaje que paga el paciente")
    
    # Estado
    activa = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relaciones
    persona = relationship("PersonaAtendida", back_populates="afiliaciones")
    plan = relationship("PlanCobertura", back_populates="afiliaciones")
    
    def __repr__(self):
        return f"<Afiliacion(id={self.id}, poliza={self.numero_poliza}, activa={self.activa})>"


class Autorizacion(BaseModel):
    """
    Modelo 2.5.4: Autorizaciones de Prestaciones
    Aprobaciones de aseguradoras para procedimientos
    REGLA DE NEGOCIO: Requerida para prestaciones marcadas
    """
    __tablename__ = "autorizaciones"
    
    # Relaciones
    orden_id = Column(Integer, ForeignKey("ordenes.id", ondelete="CASCADE"), nullable=True, index=True)
    plan_id = Column(Integer, ForeignKey("planes_cobertura.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos de autorización
    procedimiento_codigo = Column(String(50), nullable=True, comment="Código si no hay orden")
    numero_autorizacion = Column(String(100), unique=True, nullable=True, index=True)
    
    # Fechas
    fecha_solicitud = Column(Date, nullable=False, index=True)
    fecha_respuesta = Column(Date, nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)
    
    # Estado
    estado = Column(Enum(EstadoAutorizacionEnum), default=EstadoAutorizacionEnum.SOLICITADA, nullable=False, index=True)
    
    # Observaciones
    observaciones = Column(Text, nullable=True)
    motivo_negacion = Column(Text, nullable=True)
    
    # Relaciones
    orden = relationship("Orden", back_populates="autorizaciones")
    plan = relationship("PlanCobertura", back_populates="autorizaciones")
    
    def __repr__(self):
        return f"<Autorizacion(id={self.id}, numero={self.numero_autorizacion}, estado={self.estado.value})>"