"""
Módulo de operaciones de negocio
Contiene funciones auxiliares y lógica de negocio reutilizable
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from models.servicio import Servicio, Paciente, Cita

def validar_cedula(cedula: str) -> bool:
    if not cedula:
        return False
    cedula_limpia = cedula.replace("-", "").replace(" ", "")
    return cedula_limpia.isdigit() and 5 <= len(cedula_limpia) <= 20

def validar_email(email: str) -> bool:
    if not email:
        return False
    return "@" in email and "." in email.split("@")[-1]

def buscar_paciente_por_cedula(db: Session, cedula: str) -> Optional[Paciente]:
    return db.query(Paciente).filter(Paciente.cedula == cedula).first()

def buscar_servicios_activos(db: Session) -> List[Servicio]:
    return db.query(Servicio).filter(Servicio.activo == True).all()

def verificar_disponibilidad_cita(
    db: Session,
    fecha_hora: datetime,
    duracion_minutos: int = 30
) -> bool:
    hora_inicio = fecha_hora
    hora_fin = fecha_hora + timedelta(minutes=duracion_minutos)
    
    citas_solapadas = db.query(Cita).filter(
        Cita.fecha_hora < hora_fin,
        Cita.fecha_hora >= hora_inicio,
        Cita.estado.in_(["programada", "confirmada"])
    ).count()
    
    return citas_solapadas == 0

def calcular_edad(fecha_nacimiento: datetime) -> int:
    hoy = datetime.now()
    edad = hoy.year - fecha_nacimiento.year
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad