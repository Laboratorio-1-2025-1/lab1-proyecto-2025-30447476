"""
Script para inicializar la base de datos con datos de prueba
Ejecutar: python init_db.py
"""

from database import SessionLocal, create_tables, check_connection
from models.servicio import Servicio, Paciente, Cita
from datetime import datetime, timedelta

def init_database():
    """Inicializar base de datos con datos de ejemplo"""
    
    print("🔧 Iniciando proceso de inicialización de base de datos...")
    
    # Verificar conexión
    if not check_connection():
        print("❌ Error: No se pudo conectar a la base de datos")
        return
    
    # Crear tablas
    print("📋 Creando tablas...")
    create_tables()
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        # ============================================
        # CREAR SERVICIOS DE EJEMPLO
        # ============================================
        print("💉 Creando servicios de ejemplo...")
        
        servicios_data = [
            {
                "nombre": "Consulta General",
                "descripcion": "Consulta médica general",
                "precio": 50.00,
                "duracion_minutos": 30
            },
            {
                "nombre": "Consulta Especializada",
                "descripcion": "Consulta con médico especialista",
                "precio": 80.00,
                "duracion_minutos": 45
            },
            {
                "nombre": "Análisis de Sangre",
                "descripcion": "Examen de laboratorio completo",
                "precio": 35.00,
                "duracion_minutos": 15
            },
            {
                "nombre": "Radiografía",
                "descripcion": "Estudio radiográfico",
                "precio": 60.00,
                "duracion_minutos": 20
            },
            {
                "nombre": "Ecografía",
                "descripcion": "Estudio ecográfico",
                "precio": 75.00,
                "duracion_minutos": 30
            }
        ]
        
        for servicio_data in servicios_data:
            # Verificar si ya existe
            existe = db.query(Servicio).filter(
                Servicio.nombre == servicio_data["nombre"]
            ).first()
            
            if not existe:
                servicio = Servicio(**servicio_data)
                db.add(servicio)
        
        db.commit()
        print(f"✅ {len(servicios_data)} servicios creados")
        
        # ============================================
        # CREAR PACIENTES DE EJEMPLO
        # ============================================
        print("👤 Creando pacientes de ejemplo...")
        
        pacientes_data = [
            {
                "cedula": "12345678",
                "nombre": "Juan",
                "apellido": "Pérez",
                "fecha_nacimiento": datetime(1985, 5, 15),
                "telefono": "0414-1234567",
                "email": "juan.perez@email.com",
                "direccion": "Calle Principal, Barquisimeto"
            },
            {
                "cedula": "23456789",
                "nombre": "María",
                "apellido": "González",
                "fecha_nacimiento": datetime(1990, 8, 22),
                "telefono": "0424-2345678",
                "email": "maria.gonzalez@email.com",
                "direccion": "Av. Libertador, Barquisimeto"
            },
            {
                "cedula": "34567890",
                "nombre": "Carlos",
                "apellido": "Rodríguez",
                "fecha_nacimiento": datetime(1978, 12, 10),
                "telefono": "0416-3456789",
                "email": "carlos.rodriguez@email.com",
                "direccion": "Carrera 19, Barquisimeto"
            }
        ]
        
        for paciente_data in pacientes_data:
            # Verificar si ya existe
            existe = db.query(Paciente).filter(
                Paciente.cedula == paciente_data["cedula"]
            ).first()
            
            if not existe:
                paciente = Paciente(**paciente_data)
                db.add(paciente)
        
        db.commit()
        print(f"✅ {len(pacientes_data)} pacientes creados")
        
        # ============================================
        # CREAR CITAS DE EJEMPLO
        # ============================================
        print("📅 Creando citas de ejemplo...")
        
        # Obtener IDs de servicios y pacientes
        servicio_consulta = db.query(Servicio).filter(
            Servicio.nombre == "Consulta General"
        ).first()
        
        servicio_analisis = db.query(Servicio).filter(
            Servicio.nombre == "Análisis de Sangre"
        ).first()
        
        paciente1 = db.query(Paciente).filter(
            Paciente.cedula == "12345678"
        ).first()
        
        paciente2 = db.query(Paciente).filter(
            Paciente.cedula == "23456789"
        ).first()
        
        if servicio_consulta and servicio_analisis and paciente1 and paciente2:
            hoy = datetime.now()
            
            citas_data = [
                {
                    "paciente_id": paciente1.id,
                    "servicio_id": servicio_consulta.id,
                    "fecha_hora": hoy + timedelta(days=1, hours=9),
                    "estado": "programada",
                    "observaciones": "Primera consulta"
                },
                {
                    "paciente_id": paciente2.id,
                    "servicio_id": servicio_analisis.id,
                    "fecha_hora": hoy + timedelta(days=2, hours=10),
                    "estado": "programada",
                    "observaciones": "Análisis de rutina"
                },
                {
                    "paciente_id": paciente1.id,
                    "servicio_id": servicio_analisis.id,
                    "fecha_hora": hoy - timedelta(days=5),
                    "estado": "completada",
                    "observaciones": "Cita completada exitosamente"
                }
            ]
            
            for cita_data in citas_data:
                cita = Cita(**cita_data)
                db.add(cita)
            
            db.commit()
            print(f"✅ {len(citas_data)} citas creadas")
        
        # ============================================
        # RESUMEN
        # ============================================
        print("\n" + "="*50)
        print("✅ Base de datos inicializada correctamente")
        print("="*50)
        print(f"📊 Servicios: {db.query(Servicio).count()}")
        print(f"👥 Pacientes: {db.query(Paciente).count()}")
        print(f"📅 Citas: {db.query(Cita).count()}")
        print("="*50)
        print("\n🚀 Ya puedes iniciar la API con: python main.py")
        print("📚 Documentación en: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
