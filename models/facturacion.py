"""
Módulo 2.7: Facturación y cobros
- Factura: comprobantes de venta
- FacturaItem: detalle de items facturados
- Pago: registros de pagos
- NotaCredito/NotaDebito: ajustes
"""
from sqlalchemy import Column, String, Date, Integer, ForeignKey, Enum, Text, Numeric, JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class EstadoFacturaEnum(str, enum.Enum):
    """Estados de facturas"""
    EMITIDA = "EMITIDA"
    PAGADA = "PAGADA"
    PENDIENTE = "PENDIENTE"
    ANULADA = "ANULADA"
    VENCIDA = "VENCIDA"


class MedioPagoEnum(str, enum.Enum):
    """Medios de pago"""
    EFECTIVO = "EFECTIVO"
    TARJETA_CREDITO = "TARJETA_CREDITO"
    TARJETA_DEBITO = "TARJETA_DEBITO"
    TRANSFERENCIA = "TRANSFERENCIA"
    CHEQUE = "CHEQUE"


class EstadoPagoEnum(str, enum.Enum):
    """Estados de pagos"""
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    REEMBOLSADO = "REEMBOLSADO"


class TipoNotaEnum(str, enum.Enum):
    """Tipos de notas contables"""
    CREDITO = "CREDITO"
    DEBITO = "DEBITO"


class Factura(BaseModel):
    """
    Modelo 2.7.1: Facturas
    Comprobantes de prestaciones realizadas
    REGLA DE NEGOCIO: Solo emitida cuando items tienen precio vigente
    """
    __tablename__ = "facturas"
    
    # Número de factura
    numero = Column(String(50), unique=True, nullable=False, index=True)
    
    # Fechas
    fecha_emision = Column(Date, nullable=False, index=True)
    fecha_vencimiento = Column(Date, nullable=True)
    
    # Relaciones (factura a persona O aseguradora)
    persona_id = Column(Integer, ForeignKey("personas_atendidas.id", ondelete="CASCADE"), nullable=True, index=True)
    aseguradora_id = Column(Integer, ForeignKey("aseguradoras.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Moneda
    moneda = Column(String(10), default="USD", nullable=False)
    
    # Totales
    subtotal = Column(Numeric(12, 2), nullable=False)
    impuestos_total = Column(Numeric(12, 2), default=0, nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    
    # Estado
    estado = Column(Enum(EstadoFacturaEnum), default=EstadoFacturaEnum.EMITIDA, nullable=False, index=True)
    
    # Observaciones
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    persona = relationship("PersonaAtendida", back_populates="facturas")
    aseguradora = relationship("Aseguradora", back_populates="facturas")
    items = relationship("FacturaItem", back_populates="factura", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="factura", cascade="all, delete-orphan")
    notas_ajuste = relationship("NotaAjuste", back_populates="factura", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Factura(id={self.id}, numero={self.numero}, total={self.total})>"


class FacturaItem(BaseModel):
    """
    Modelo 2.7.2: Items de Factura
    Detalle línea por línea de prestaciones facturadas
    """
    __tablename__ = "factura_items"
    
    # Relación
    factura_id = Column(Integer, ForeignKey("facturas.id", ondelete="CASCADE"), nullable=False, index=True)
    prestacion_codigo = Column(String(50), ForeignKey("prestaciones.codigo", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Detalles
    descripcion = Column(String(500), nullable=False)
    cantidad = Column(Integer, default=1, nullable=False)
    valor_unitario = Column(Numeric(12, 2), nullable=False)
    impuestos = Column(Numeric(12, 2), default=0, nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    
    # Datos adicionales
    fecha_prestacion = Column(Date, nullable=True)
    
    # Relaciones
    factura = relationship("Factura", back_populates="items")
    prestacion = relationship("Prestacion")
    
    def __repr__(self):
        return f"<FacturaItem(id={self.id}, factura_id={self.factura_id}, total={self.total})>"


class Pago(BaseModel):
    """
    Modelo 2.7.3: Pagos
    Registros de pagos aplicados a facturas
    REGLA DE NEGOCIO: No exceder saldo pendiente
    """
    __tablename__ = "pagos"
    
    # Relación
    factura_id = Column(Integer, ForeignKey("facturas.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos del pago
    fecha = Column(Date, nullable=False, index=True)
    monto = Column(Numeric(12, 2), nullable=False)
    medio = Column(Enum(MedioPagoEnum), nullable=False)
    referencia = Column(String(100), nullable=True, comment="Número de transacción, cheque, etc.")
    
    # Estado
    estado = Column(Enum(EstadoPagoEnum), default=EstadoPagoEnum.PENDIENTE, nullable=False, index=True)
    
    # Observaciones
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    factura = relationship("Factura", back_populates="pagos")
    
    def __repr__(self):
        return f"<Pago(id={self.id}, factura_id={self.factura_id}, monto={self.monto})>"


class NotaAjuste(BaseModel):
    """
    Modelo 2.7.4: Notas de Crédito/Débito
    Ajustes a facturas emitidas
    """
    __tablename__ = "notas_ajuste"
    
    # Relación
    factura_id = Column(Integer, ForeignKey("facturas.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos de la nota
    numero = Column(String(50), unique=True, nullable=False, index=True)
    tipo = Column(Enum(TipoNotaEnum), nullable=False)
    fecha = Column(Date, nullable=False, index=True)
    monto = Column(Numeric(12, 2), nullable=False)
    motivo = Column(Text, nullable=False)
    
    # Observaciones
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    factura = relationship("Factura", back_populates="notas_ajuste")
    
    def __repr__(self):
        return f"<NotaAjuste(id={self.id}, numero={self.numero}, tipo={self.tipo.value})>"