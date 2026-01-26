"""
Servicio de Notificaciones
Integración con SendGrid para envío de emails
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict
from config import settings
from models.notificaciones import (
    Notificacion, 
    TipoNotificacionEnum, 
    EstadoNotificacionEnum,
    PlantillaNotificacionEnum
)
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Servicio para envío de notificaciones
    Soporta Email (SendGrid), SMS y WhatsApp (simulado)
    """
    
    def __init__(self):
        self.sg_client = None
        if settings.SENDGRID_API_KEY:
            self.sg_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
    
    def send_email(
        self,
        db: Session,
        destinatario: str,
        asunto: str,
        mensaje: str,
        plantilla: Optional[PlantillaNotificacionEnum] = None,
        payload: Optional[Dict] = None
    ) -> Notificacion:
        """
        Envía email usando SendGrid
        Registra en tabla de notificaciones
        """
        # Crear registro de notificación
        notificacion = Notificacion(
            tipo=TipoNotificacionEnum.EMAIL,
            destinatario=destinatario,
            plantilla=plantilla,
            asunto=asunto,
            mensaje=mensaje,
            payload=payload,
            estado=EstadoNotificacionEnum.PENDIENTE
        )
        db.add(notificacion)
        db.commit()
        db.refresh(notificacion)
        
        # Intentar envío
        try:
            if not self.sg_client:
                logger.warning("SendGrid no configurado, simulando envío")
                notificacion.estado = EstadoNotificacionEnum.ENVIADO
                notificacion.fecha_enviado = datetime.utcnow()
                db.commit()
                return notificacion
            
            # Construir email
            from_email = Email(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME)
            to_email = To(destinatario)
            content = Content("text/html", mensaje)
            mail = Mail(from_email, to_email, asunto, content)
            
            # Enviar
            response = self.sg_client.send(mail)
            
            # Actualizar estado
            notificacion.estado = EstadoNotificacionEnum.ENVIADO
            notificacion.fecha_enviado = datetime.utcnow()
            notificacion.proveedor_id = response.headers.get('X-Message-Id', '')
            notificacion.intentos += 1
            
            db.commit()
            logger.info(f"Email enviado a {destinatario}: {asunto}")
            
        except Exception as e:
            # Marcar error
            notificacion.estado = EstadoNotificacionEnum.ERROR
            notificacion.error_mensaje = str(e)
            notificacion.intentos += 1
            db.commit()
            logger.error(f"Error enviando email: {e}")
        
        return notificacion
    
    def send_cita_confirmacion(
        self,
        db: Session,
        email_paciente: str,
        nombre_paciente: str,
        fecha_cita: datetime,
        profesional: str,
        unidad: str
    ) -> Notificacion:
        """Envía confirmación de cita"""
        asunto = "Confirmación de Cita Médica"
        mensaje = f"""
        <h2>Confirmación de Cita</h2>
        <p>Estimado/a {nombre_paciente},</p>
        <p>Su cita ha sido confirmada con los siguientes detalles:</p>
        <ul>
            <li><strong>Fecha y hora:</strong> {fecha_cita.strftime('%d/%m/%Y %H:%M')}</li>
            <li><strong>Profesional:</strong> {profesional}</li>
            <li><strong>Ubicación:</strong> {unidad}</li>
        </ul>
        <p>Por favor llegue 15 minutos antes de su cita.</p>
        <p>Saludos,<br>Sistema Médico</p>
        """
        
        return self.send_email(
            db=db,
            destinatario=email_paciente,
            asunto=asunto,
            mensaje=mensaje,
            plantilla=PlantillaNotificacionEnum.CONFIRMACION_CITA,
            payload={
                "nombre_paciente": nombre_paciente,
                "fecha_cita": fecha_cita.isoformat(),
                "profesional": profesional,
                "unidad": unidad
            }
        )
    
    def send_resultado_disponible(
        self,
        db: Session,
        email_paciente: str,
        nombre_paciente: str,
        tipo_examen: str
    ) -> Notificacion:
        """Notifica disponibilidad de resultados"""
        asunto = "Resultados Disponibles"
        mensaje = f"""
        <h2>Resultados de Examen Disponibles</h2>
        <p>Estimado/a {nombre_paciente},</p>
        <p>Sus resultados de <strong>{tipo_examen}</strong> ya están disponibles.</p>
        <p>Por favor acceda a su portal de paciente o comuníquese con nosotros para obtenerlos.</p>
        <p>Saludos,<br>Sistema Médico</p>
        """
        
        return self.send_email(
            db=db,
            destinatario=email_paciente,
            asunto=asunto,
            mensaje=mensaje,
            plantilla=PlantillaNotificacionEnum.RESULTADO_DISPONIBLE,
            payload={
                "nombre_paciente": nombre_paciente,
                "tipo_examen": tipo_examen
            }
        )
    
    def send_factura_emitida(
        self,
        db: Session,
        email_destinatario: str,
        nombre: str,
        numero_factura: str,
        total: float,
        moneda: str = "USD"
    ) -> Notificacion:
        """Notifica emisión de factura"""
        asunto = f"Factura {numero_factura} Emitida"
        mensaje = f"""
        <h2>Nueva Factura Emitida</h2>
        <p>Estimado/a {nombre},</p>
        <p>Se ha emitido la factura <strong>{numero_factura}</strong> por un monto de <strong>{moneda} {total:.2f}</strong>.</p>
        <p>Por favor proceda con el pago a la brevedad posible.</p>
        <p>Saludos,<br>Departamento de Facturación</p>
        """
        
        return self.send_email(
            db=db,
            destinatario=email_destinatario,
            asunto=asunto,
            mensaje=mensaje,
            plantilla=PlantillaNotificacionEnum.FACTURA_EMITIDA,
            payload={
                "nombre": nombre,
                "numero_factura": numero_factura,
                "total": total,
                "moneda": moneda
            }
        )
    
    def retry_failed_notifications(self, db: Session, max_retries: int = 3):
        """Reintenta notificaciones fallidas"""
        notificaciones_pendientes = db.query(Notificacion).filter(
            Notificacion.estado == EstadoNotificacionEnum.ERROR,
            Notificacion.intentos < max_retries
        ).all()
        
        for notif in notificaciones_pendientes:
            if notif.tipo == TipoNotificacionEnum.EMAIL:
                self.send_email(
                    db=db,
                    destinatario=notif.destinatario,
                    asunto=notif.asunto,
                    mensaje=notif.mensaje,
                    plantilla=notif.plantilla,
                    payload=notif.payload
                )


# Instancia global del servicio
notification_service = NotificationService()