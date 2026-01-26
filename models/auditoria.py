"""
Módulo 2.9: Auditoría y trazabilidad
- BitacoraAcceso: registro de accesos al sistema
- Usuario: usuarios del sistema
- Rol: roles de acceso
- Permiso: permisos granulares
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Text, Table, Boolean
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class TipoAccionEnum(str, enum.Enum):
    """Tipos de acciones auditables"""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    EXPORT = "EXPORT"


# Tabla de asociación Usuario-Rol (muchos a muchos)
usuario_rol = Table(
    'usuario_rol',
    BaseModel.metadata,
    Column('usuario_id', Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), primary_key=True),
    Column('rol_id', Integer, ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True)
)

# Tabla de asociación Rol-Permiso (muchos a muchos)
rol_permiso = Table(
    'rol_permiso',
    BaseModel.metadata,
    Column('rol_id', Integer, ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('permisos.id', ondelete="CASCADE"), primary_key=True)
)


class Usuario(BaseModel):
    """
    Modelo 2.9.1: Usuarios del Sistema
    Autenticación y autorización
    """
    __tablename__ = "usuarios"
    
    # Credenciales
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Datos personales opcionales
    nombres = Column(String(100), nullable=True)
    apellidos = Column(String(100), nullable=True)
    
    # Control de acceso
    estado = Column(Boolean, default=True, nullable=False)
    ultimo_acceso = Column(DateTime(timezone=True), nullable=True)
    intentos_fallidos = Column(Integer, default=0, nullable=False)
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)
    
    # Tokens
    token_refresh = Column(String(500), nullable=True)
    
    # Relaciones
    roles = relationship("Rol", secondary=usuario_rol, back_populates="usuarios")
    bitacora_accesos = relationship("BitacoraAcceso", back_populates="usuario", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, username={self.username})>"


class Rol(BaseModel):
    """
    Modelo 2.9.2: Roles de Usuario
    Roles predefinidos: administrador, profesional, cajero, auditor
    """
    __tablename__ = "roles"
    
    # Datos del rol
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    
    # Relaciones
    usuarios = relationship("Usuario", secondary=usuario_rol, back_populates="roles")
    permisos = relationship("Permiso", secondary=rol_permiso, back_populates="roles")
    
    def __repr__(self):
        return f"<Rol(id={self.id}, nombre={self.nombre})>"


class Permiso(BaseModel):
    """
    Modelo 2.9.3: Permisos Granulares
    Control fino sobre recursos y acciones
    """
    __tablename__ = "permisos"
    
    # Identificador del permiso
    clave = Column(String(100), unique=True, nullable=False, index=True, comment="Ej: personas.read, citas.create")
    descripcion = Column(Text, nullable=True)
    
    # Agrupación
    recurso = Column(String(50), nullable=False, index=True, comment="Ej: personas, citas, facturas")
    accion = Column(String(50), nullable=False, comment="Ej: create, read, update, delete")
    
    # Relaciones
    roles = relationship("Rol", secondary=rol_permiso, back_populates="permisos")
    
    def __repr__(self):
        return f"<Permiso(id={self.id}, clave={self.clave})>"


class BitacoraAcceso(BaseModel):
    """
    Modelo 2.9.4: Bitácora de Accesos
    Registro completo de acciones en el sistema
    REGLA DE NEGOCIO: Registrar lectura/escritura de registros clínicos
    """
    __tablename__ = "bitacora_accesos"
    
    # Relación
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Datos de la acción
    recurso = Column(String(100), nullable=False, index=True, comment="Endpoint o recurso accedido")
    accion = Column(Enum(TipoAccionEnum), nullable=False)
    metodo_http = Column(String(10), nullable=True, comment="GET, POST, PUT, DELETE")
    
    # Detalles técnicos
    ip = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Datos adicionales
    parametros = Column(Text, nullable=True, comment="Query params, body snippet")
    resultado = Column(String(50), nullable=True, comment="success, error, unauthorized")
    codigo_http = Column(Integer, nullable=True)
    
    # Timestamp ya incluido en BaseModel (created_at)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="bitacora_accesos")
    
    def __repr__(self):
        return f"<BitacoraAcceso(id={self.id}, usuario_id={self.usuario_id}, recurso={self.recurso})>"