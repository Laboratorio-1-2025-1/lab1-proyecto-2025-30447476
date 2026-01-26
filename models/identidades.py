"""
Módulo 2.1: Identidades y vinculación asistencial
- PersonasAtendidas (pacientes)
- Profesionales (médicos, enfermería, terapias)
- UnidadesAtencion (sedes/consultorios/servicios)
"""
from sqlalchemy import Column, String, Date, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class TipoDocumentoEnum(str, enum.Enum):
    """Tipos de documento de identidad"""
    CEDULA = "CEDULA"
    PASAPORTE = "PASAPORTE"
    RUC = "RUC"
    CARNET_EXTRANJERIA = "CARNET_EXTRANJERIA"


class SexoEnum(str, enum.Enum):
    """Sexo biológico"""
    MASCULINO = "MASCULINO"
    FEMENINO = "FEMENINO"
    OTRO = "OTRO"


class EstadoGeneralEnum(str, enum.Enum):
    """Estados generales para entidades"""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"


class TipoUnidadEnum(str, enum.Enum):
    """Tipos de unidades de atención"""
    SEDE = "SEDE"
    CONSULTORIO = "CONSULTORIO"
    SERVICIO = "SERVICIO"
    LABORATORIO = "LABORATORIO"
    URGENCIAS = "URGENCIAS"


class PersonaAtendida(BaseModel):
    """
    Modelo 2.1.1: Personas Atendidas (Pacientes)
    Gestiona información de pacientes del sistema
    """
    __tablename__ = "personas_atendidas"
    
    # Identificación
    tipo_documento = Column(Enum(TipoDocumentoEnum), nullable=False)
    numero_documento = Column(String(50), unique=True, nullable=False, index=True)
    
    # Datos personales
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(Enum(SexoEnum), nullable=False)
    
    # Contacto
    correo = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20), nullable=False)
    direccion = Column(String(255), nullable=False)
    contacto_emergencia = Column(String(100), nullable=False)
    
    # Información clínica opcional
    alergias = Column(JSON, nullable=True, comment="Lista de alergias")
    antecedentes_resumen = Column(Text, nullable=True)
    
    # Estado
    estado = Column(Enum(EstadoGeneralEnum), default=EstadoGeneralEnum.ACTIVO, nullable=False)
    
    # Relaciones
    citas = relationship("Cita", back_populates="persona", cascade="all, delete-orphan")
    episodios = relationship("EpisodioAtencion", back_populates="persona", cascade="all, delete-orphan")
    consentimientos = relationship("Consentimiento", back_populates="persona", cascade="all, delete-orphan")
    afiliaciones = relationship("Afiliacion", back_populates="persona", cascade="all, delete-orphan")
    facturas = relationship("Factura", back_populates="persona", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PersonaAtendida(id={self.id}, documento={self.numero_documento}, nombre={self.nombres} {self.apellidos})>"


class Profesional(BaseModel):
    """
    Modelo 2.1.2: Profesionales de Salud
    Médicos, enfermería, terapeutas, etc.
    """
    __tablename__ = "profesionales"
    
    # Datos personales
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    
    # Datos profesionales
    registro_profesional = Column(String(50), unique=True, nullable=False, index=True)
    especialidad = Column(String(100), nullable=False)
    
    # Contacto
    correo = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20), nullable=False)
    
    # Configuración
    agenda_habilitada = Column(Boolean, default=True, nullable=False)
    estado = Column(Enum(EstadoGeneralEnum), default=EstadoGeneralEnum.ACTIVO, nullable=False)
    
    # Relaciones
    bloques_agenda = relationship("BloqueAgenda", back_populates="profesional", cascade="all, delete-orphan")
    citas = relationship("Cita", back_populates="profesional", cascade="all, delete-orphan")
    notas_clinicas = relationship("NotaClinica", back_populates="profesional", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Profesional(id={self.id}, registro={self.registro_profesional}, nombre={self.nombres} {self.apellidos})>"


class UnidadAtencion(BaseModel):
    """
    Modelo 2.1.3: Unidades de Atención
    Sedes, consultorios, servicios donde se brinda atención
    """
    __tablename__ = "unidades_atencion"
    
    # Datos de la unidad
    nombre = Column(String(150), nullable=False)
    tipo = Column(Enum(TipoUnidadEnum), nullable=False)
    
    # Ubicación y contacto
    direccion = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=False)
    
    # Configuración
    horario_referencia = Column(JSON, nullable=True, comment="Horarios de atención")
    estado = Column(Enum(EstadoGeneralEnum), default=EstadoGeneralEnum.ACTIVO, nullable=False)
    
    # Relaciones
    bloques_agenda = relationship("BloqueAgenda", back_populates="unidad", cascade="all, delete-orphan")
    citas = relationship("Cita", back_populates="unidad", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UnidadAtencion(id={self.id}, nombre={self.nombre}, tipo={self.tipo.value})>"