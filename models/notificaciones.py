"""
Módulo 2.8: Notificaciones y comunicaciones
- Notificacion: mensajes enviados por email/SMS/WhatsApp
Integración con SendGrid
"""
from sqlalchemy import Column, String, DateTime, Integer, Enum, Text, JSON
from models.base import BaseModel
import enum


class TipoNotificacionEnum(str, enum.Enum):
    """Tipos de canales de notificación"""
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    PUSH = "PUSH"


class EstadoNotificacionEnum(str, enum.Enum):
    """Estados de notificaciones"""
    PENDIENTE = "PENDIENTE"
    ENVIADO = "ENVIADO"
    ENTREGADO = "ENTREGADO"
    ERROR = "ERROR"
    REBOTADO = "REBOTADO"


class PlantillaNotificacionEnum(str, enum.Enum):
    """Plantillas predefinidas"""
    CONFIRMACION_CITA = "CONFIRMACION_CITA"
    RECORDATORIO_CITA = "RECORDATORIO_CITA"
    CANCELACION_CITA = "CANCELACION_CITA"
    RESULTADO_DISPONIBLE = "RESULTADO_DISPONIBLE"
    FACTURA_EMITIDA = "FACTURA_EMITIDA"
    PAGO_RECIBIDO = "PAGO_RECIBIDO"
    AUTORIZACION_APROBADA = "AUTORIZACION_APROBADA"
    AUTORIZACION_NEGADA = "AUTORIZACION_NEGADA"


class Notificacion(BaseModel):
    """
    Modelo 2.8.1: Notificaciones
    Gestión de mensajes multi-canal (Email, SMS, WhatsApp)
    REGLA DE NEGOCIO: Idempotencia en reintentos
    """
    __tablename__ = "notificaciones"
    
    # Canal
    tipo = Column(Enum(TipoNotificacionEnum), nullable=False, index=True)
    
    # Destinatario
    destinatario = Column(String(255), nullable=False, index=True, comment="Email, teléfono según tipo")
    
    # Contenido
    plantilla = Column(Enum(PlantillaNotificacionEnum), nullable=True)
    asunto = Column(String(255), nullable=True)
    mensaje = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True, comment="Datos adicionales para renderizar plantilla")
    
    # Control de envío
    estado = Column(Enum(EstadoNotificacionEnum), default=EstadoNotificacionEnum.PENDIENTE, nullable=False, index=True)
    intentos = Column(Integer, default=0, nullable=False)
    max_intentos = Column(Integer, default=3, nullable=False)
    
    # Timestamps
    fecha_programada = Column(DateTime(timezone=True), nullable=True, index=True)
    fecha_enviado = Column(DateTime(timezone=True), nullable=True)
    fecha_entregado = Column(DateTime(timezone=True), nullable=True)
    
    # Tracking externo
    proveedor_id = Column(String(255), nullable=True, comment="ID del proveedor (SendGrid message ID)")
    error_mensaje = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Notificacion(id={self.id}, tipo={self.tipo.value}, estado={self.estado.value})>"