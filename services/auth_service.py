"""Servicio de autenticación"""
from sqlalchemy.orm import Session
from models.usuario import Usuario
from models.rol import Rol
from models.usuario_rol import UsuarioRol
from schemas.auth import LoginRequest, UsuarioCreate
from utils.password_hasher import hash_password, verify_password
from utils.jwt_handler import create_access_token, create_refresh_token
from fastapi import HTTPException, status
from datetime import datetime

class AuthService:
    
    @staticmethod
    def login(db: Session, credentials: LoginRequest):
        """Autenticar usuario"""
        usuario = db.query(Usuario).filter(
            Usuario.username == credentials.username
        ).first()
        
        if not usuario or not verify_password(credentials.password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
        
        if usuario.estado != "activo":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo o bloqueado"
            )
        
        # Actualizar último acceso
        usuario.ultimo_acceso = datetime.utcnow()
        db.commit()
        
        # Obtener roles
        roles = [ur.rol.nombre for ur in usuario.roles]
        
        # Generar tokens
        token_data = {
            "sub": str(usuario.id),
            "username": usuario.username,
            "roles": roles
        }
        
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token({"sub": str(usuario.id)}),
            "token_type": "bearer"
        }
    
    @staticmethod
    def register(db: Session, usuario_data: UsuarioCreate):
        """Registrar nuevo usuario"""
        # Verificar si existe
        if db.query(Usuario).filter(Usuario.username == usuario_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username ya existe"
            )
        
        if db.query(Usuario).filter(Usuario.email == usuario_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya registrado"
            )
        
        # Crear usuario
        nuevo_usuario = Usuario(
            username=usuario_data.username,
            email=usuario_data.email,
            password_hash=hash_password(usuario_data.password)
        )
        db.add(nuevo_usuario)
        db.flush()
        
        # Asignar roles
        for rol_id in usuario_data.roles:
            usuario_rol = UsuarioRol(usuario_id=nuevo_usuario.id, rol_id=rol_id)
            db.add(usuario_rol)
        
        db.commit()
        db.refresh(nuevo_usuario)
        
        return nuevo_usuario