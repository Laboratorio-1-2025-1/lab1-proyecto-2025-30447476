"""
Script para generar datos iniciales (seed data)
Crea usuarios, roles, permisos, prestaciones, etc.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, init_db, Base, engine
from models import *
from services.auth_service import AuthService
from datetime import datetime, date, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Crear todas las tablas en la base de datos"""
    logger.info("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tablas creadas exitosamente")


def create_roles_and_permissions(db):
    """Crea roles y permisos iniciales"""
    logger.info("Creando roles y permisos...")
    
    # Crear permisos básicos
    permisos_data = [
        # Personas
        ("personas.create", "Crear personas", "personas", "create"),
        ("personas.read", "Leer personas", "personas", "read"),
        ("personas.update", "Actualizar personas", "personas", "update"),
        ("personas.delete", "Eliminar personas", "personas", "delete"),
        
        # Citas
        ("citas.create", "Crear citas", "citas", "create"),
        ("citas.read", "Leer citas", "citas", "read"),
        ("citas.update", "Actualizar citas", "citas", "update"),
        ("citas.delete", "Eliminar citas", "citas", "delete"),
        
        # Registros clínicos
        ("clinica.read", "Leer registros clínicos", "clinica", "read"),
        ("clinica.write", "Escribir registros clínicos", "clinica", "write"),
        
        # Facturación
        ("facturas.create", "Crear facturas", "facturas", "create"),
        ("facturas.read", "Leer facturas", "facturas", "read"),
        ("facturas.update", "Actualizar facturas", "facturas", "update"),
        
        # Auditoría
        ("auditoria.read", "Leer auditoría", "auditoria", "read"),
    ]
    
    permisos = {}
    for clave, desc, recurso, accion in permisos_data:
        permiso = Permiso(clave=clave, descripcion=desc, recurso=recurso, accion=accion)
        db.add(permiso)
        permisos[clave] = permiso
    
    db.flush()
    
    # Crear roles
    roles_data = {
        "administrador": {
            "descripcion": "Administrador del sistema con acceso completo",
            "permisos": list(permisos.values())
        },
        "profesional": {
            "descripcion": "Profesional de salud (médico, enfermera, etc.)",
            "permisos": [
                permisos["personas.read"],
                permisos["citas.read"],
                permisos["citas.update"],
                permisos["clinica.read"],
                permisos["clinica.write"]
            ]
        },
        "cajero": {
            "descripcion": "Personal de facturación y cobros",
            "permisos": [
                permisos["personas.read"],
                permisos["facturas.create"],
                permisos["facturas.read"],
                permisos["facturas.update"]
            ]
        },
        "auditor": {
            "descripcion": "Auditor de sistema",
            "permisos": [
                permisos["personas.read"],
                permisos["citas.read"],
                permisos["clinica.read"],
                permisos["facturas.read"],
                permisos["auditoria.read"]
            ]
        }
    }
    
    roles = {}
    for nombre, data in roles_data.items():
        rol = Rol(nombre=nombre, descripcion=data["descripcion"])
        rol.permisos = data["permisos"]
        db.add(rol)
        roles[nombre] = rol
    
    db.commit()
    logger.info(f"Creados {len(permisos)} permisos y {len(roles)} roles")
    return roles


def create_users(db, roles):
    """Crea usuarios iniciales"""
    logger.info("Creando usuarios...")
    
    usuarios_data = [
        ("admin", "admin@medical.com", "Admin123!", ["administrador"]),
        ("medico1", "medico1@medical.com", "Medico123!", ["profesional"]),
        ("cajero1", "cajero1@medical.com", "Cajero123!", ["cajero"]),
        ("auditor1", "auditor1@medical.com", "Auditor123!", ["auditor"])
    ]
    
    for username, email, password, rol_nombres in usuarios_data:
        usuario = AuthService.create_user(
            db=db,
            username=username,
            email=email,
            password=password,
            roles=rol_nombres
        )
        logger.info(f"Usuario creado: {username}")


def create_prestaciones(db):
    """Crea catálogo de prestaciones"""
    logger.info("Creando prestaciones...")
    
    prestaciones_data = [
        ("CONS001", "Consulta Medicina General", GrupoPrestacionEnum.CONSULTA, 30, False),
        ("CONS002", "Consulta Especialista", GrupoPrestacionEnum.CONSULTA, 45, True),
        ("LAB001", "Hemograma Completo", GrupoPrestacionEnum.LABORATORIO, 15, False),
        ("LAB002", "Perfil Lipídico", GrupoPrestacionEnum.LABORATORIO, 20, False),
        ("IMG001", "Radiografía Tórax", GrupoPrestacionEnum.IMAGENOLOGIA, 30, True),
        ("PROC001", "Sutura Simple", GrupoPrestacionEnum.PROCEDIMIENTO_NO_QUIRURGICO, 45, False),
    ]
    
    for codigo, nombre, grupo, tiempo, req_aut in prestaciones_data:
        prestacion = Prestacion(
            codigo=codigo,
            nombre=nombre,
            grupo=grupo,
            tiempo_estimado=tiempo,
            requiere_autorizacion=req_aut,
            vigente=True
        )
        db.add(prestacion)
    
    db.commit()
    logger.info(f"Creadas {len(prestaciones_data)} prestaciones")


def create_sample_data(db):
    """Crea datos de ejemplo"""
    logger.info("Creando datos de ejemplo...")
    
    # 2 Profesionales
    prof1 = Profesional(
        nombres="Juan Carlos",
        apellidos="Pérez López",
        registro_profesional="MED12345",
        especialidad="Medicina General",
        correo="jperez@medical.com",
        telefono="+1234567890",
        agenda_habilitada=True,
        estado=EstadoGeneralEnum.ACTIVO
    )
    
    prof2 = Profesional(
        nombres="María Elena",
        apellidos="García Rodríguez",
        registro_profesional="MED67890",
        especialidad="Cardiología",
        correo="mgarcia@medical.com",
        telefono="+0987654321",
        agenda_habilitada=True,
        estado=EstadoGeneralEnum.ACTIVO
    )
    
    db.add_all([prof1, prof2])
    db.flush()
    
    # 1 Unidad de Atención
    unidad = UnidadAtencion(
        nombre="Consultorio Central",
        tipo=TipoUnidadEnum.CONSULTORIO,
        direccion="Calle Principal 123",
        telefono="+1111111111",
        horario_referencia={"lunes_viernes": "08:00-17:00"},
        estado=EstadoGeneralEnum.ACTIVO
    )
    db.add(unidad)
    db.flush()
    
    # 1 Paciente
    paciente = PersonaAtendida(
        tipo_documento=TipoDocumentoEnum.CEDULA,
        numero_documento="12345678",
        nombres="Pedro Antonio",
        apellidos="Martínez Sánchez",
        fecha_nacimiento=date(1985, 5, 15),
        sexo=SexoEnum.MASCULINO,
        correo="pmartinez@example.com",
        telefono="+5555555555",
        direccion="Avenida Libertad 456",
        contacto_emergencia="Ana Martínez +5555555556",
        alergias=["Penicilina"],
        estado=EstadoGeneralEnum.ACTIVO
    )
    db.add(paciente)
    db.flush()
    
    # 1 Bloque de Agenda
    mañana = datetime.now() + timedelta(days=1)
    inicio = mañana.replace(hour=9, minute=0, second=0, microsecond=0)
    fin = mañana.replace(hour=12, minute=0, second=0, microsecond=0)
    
    bloque = BloqueAgenda(
        profesional_id=prof1.id,
        unidad_id=unidad.id,
        inicio=inicio,
        fin=fin,
        capacidad=3,
        estado=EstadoBloqueEnum.ABIERTO
    )
    db.add(bloque)
    
    # 1 Aseguradora y Plan
    aseguradora = Aseguradora(
        nombre="Seguros Salud Plus",
        nit="900123456",
        contacto="contacto@saludplus.com",
        telefono="+2222222222",
        estado=EstadoAseguradoraEnum.ACTIVA
    )
    db.add(aseguradora)
    db.flush()
    
    plan = PlanCobertura(
        aseguradora_id=aseguradora.id,
        nombre="Plan Básico",
        codigo="PLAN001",
        cobertura_porcentaje=80.00,
        vigente_desde=date.today(),
        vigente_hasta=date(2026, 12, 31)
    )
    db.add(plan)
    
    db.commit()
    logger.info("Datos de ejemplo creados")


def main():
    """Ejecuta seed de datos"""
    logger.info("=== Iniciando seed de datos ===")
    
    # Inicializar BD
    init_db()
    
    # Crear tablas
    create_tables()
    
    db = SessionLocal()
    try:
        # Crear estructura de seguridad
        roles = create_roles_and_permissions(db)
        create_users(db, roles)
        
        # Crear catálogos
        create_prestaciones(db)
        
        # Crear datos de ejemplo
        create_sample_data(db)
        
        logger.info("=== Seed completado exitosamente ===")
        logger.info("\nUsuarios creados:")
        logger.info("  admin / Admin123!")
        logger.info("  medico1 / Medico123!")
        logger.info("  cajero1 / Cajero123!")
        logger.info("  auditor1 / Auditor123!")
        
    except Exception as e:
        logger.error(f"Error en seed: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()