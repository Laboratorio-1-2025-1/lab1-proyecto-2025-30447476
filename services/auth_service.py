"""
Servicio de Autenticación JWT
Maneja login, registro, tokens y permisos RBAC
"""
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from config import settings
from models.auditoria import Usuario, Rol, Permiso

# Contexto de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Servicio de autenticación y autorización"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica contraseña contra hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera hash de contraseña"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea token JWT de acceso
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Crea token JWT de refresco"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decodifica y valida token JWT"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[Usuario]:
        """
        Autentica usuario por username y password
        Maneja intentos fallidos y bloqueo temporal
        """
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        
        if not usuario:
            return None
        
        # Verificar si está bloqueado
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Usuario bloqueado hasta {usuario.bloqueado_hasta}"
            )
        
        # Verificar contraseña
        if not AuthService.verify_password(password, usuario.password_hash):
            # Incrementar intentos fallidos
            usuario.intentos_fallidos += 1
            
            # Bloquear después de 5 intentos
            if usuario.intentos_fallidos >= 5:
                usuario.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=30)
            
            db.commit()
            return None
        
        # Login exitoso: resetear intentos
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario.ultimo_acceso = datetime.utcnow()
        db.commit()
        
        return usuario
    
    @staticmethod
    def get_user_permissions(db: Session, usuario_id: int) -> List[str]:
        """Obtiene lista de permisos del usuario"""
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            return []
        
        permisos = set()
        for rol in usuario.roles:
            for permiso in rol.permisos:
                permisos.add(permiso.clave)
        
        return list(permisos)
    
    @staticmethod
    def check_permission(db: Session, usuario_id: int, permiso_clave: str) -> bool:
        """Verifica si el usuario tiene un permiso específico"""
        permisos = AuthService.get_user_permissions(db, usuario_id)
        return permiso_clave in permisos
    
    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        roles: Optional[List[str]] = None
    ) -> Usuario:
        """Crea nuevo usuario con roles"""
        # Verificar duplicados
        if db.query(Usuario).filter(Usuario.username == username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username ya existe"
            )
        
        if db.query(Usuario).filter(Usuario.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya existe"
            )
        
        # Crear usuario
        usuario = Usuario(
            username=username,
            email=email,
            password_hash=AuthService.get_password_hash(password),
            estado=True
        )
        
        # Asignar roles
        if roles:
            for rol_nombre in roles:
                rol = db.query(Rol).filter(Rol.nombre == rol_nombre).first()
                if rol:
                    usuario.roles.append(rol)
        
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        
        return usuario