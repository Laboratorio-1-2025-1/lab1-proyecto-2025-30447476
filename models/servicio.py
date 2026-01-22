from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database import Base

class Servicio(Base):
    """Modelo para la tabla de servicios médicos"""
    __tablename__ = "servicios"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    duracion_minutos = Column(Integer, nullable=False, default=30)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Servicio(id={self.id}, nombre='{self.nombre}', precio={self.precio})>"


class Paciente(Base):
    """Modelo para la tabla de pacientes"""
    __tablename__ = "pacientes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cedula = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    fecha_nacimiento = Column(DateTime, nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True, index=True)
    direccion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Paciente(id={self.id}, cedula='{self.cedula}', nombre='{self.nombre} {self.apellido}')>"


class Cita(Base):
    """Modelo para la tabla de citas médicas"""
    __tablename__ = "citas"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paciente_id = Column(Integer, nullable=False, index=True)
    servicio_id = Column(Integer, nullable=False, index=True)
    fecha_hora = Column(DateTime, nullable=False, index=True)
    estado = Column(String(20), default="programada")  # programada, confirmada, cancelada, completada
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Cita(id={self.id}, paciente_id={self.paciente_id}, fecha={self.fecha_hora})>"
