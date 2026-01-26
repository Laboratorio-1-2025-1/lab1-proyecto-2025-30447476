"""Router: Auditoría - Módulo 2.9"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from database import get_db
from models.auditoria import BitacoraAcceso, TipoAccionEnum, Usuario, Rol, Permiso
from schemas.base import ResponseSchema, PaginatedResponse

router_auditoria = APIRouter(prefix="/auditoria", tags=["Auditoría"])

@router_auditoria.get("/bitacora")
def consultar_bitacora(
    usuario_id: Optional[int] = None,
    recurso: Optional[str] = None,
    accion: Optional[TipoAccionEnum] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Consulta bitácora de accesos con filtros"""
    query = db.query(BitacoraAcceso)
    
    if usuario_id:
        query = query.filter(BitacoraAcceso.usuario_id == usuario_id)
    if recurso:
        query = query.filter(BitacoraAcceso.recurso.contains(recurso))
    if accion:
        query = query.filter(BitacoraAcceso.accion == accion)
    if fecha_desde:
        query = query.filter(BitacoraAcceso.created_at >= fecha_desde)
    if fecha_hasta:
        query = query.filter(BitacoraAcceso.created_at <= fecha_hasta)
    
    query = query.order_by(BitacoraAcceso.created_at.desc())
    
    total = query.count()
    registros = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        success=True,
        data=[r.to_dict() for r in registros],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router_auditoria.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return ResponseSchema(
        success=True,
        data=[
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "estado": u.estado,
                "roles": [r.nombre for r in u.roles]
            }
            for u in usuarios
        ]
    )

@router_auditoria.get("/roles")
def listar_roles(db: Session = Depends(get_db)):
    roles = db.query(Rol).all()
    return ResponseSchema(
        success=True,
        data=[
            {
                "id": r.id,
                "nombre": r.nombre,
                "descripcion": r.descripcion,
                "permisos": [p.clave for p in r.permisos]
            }
            for r in roles
        ]
    )

@router_auditoria.get("/permisos")
def listar_permisos(db: Session = Depends(get_db)):
    permisos = db.query(Permiso).all()
    return ResponseSchema(success=True, data=[p.to_dict() for p in permisos])


### ARCHIVO: routers/auth.py
"""Router: Autenticación"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models.auditoria import Usuario
from services.auth_service import AuthService
from schemas.base import ResponseSchema

router_auth = APIRouter(prefix="/auth", tags=["Autenticación"])
security = HTTPBearer()

@router_auth.post("/login")
def login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Autenticación con JWT"""
    usuario = AuthService.authenticate_user(db, username, password)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Generar tokens
    access_token = AuthService.create_access_token(
        data={"sub": usuario.username, "usuario_id": usuario.id}
    )
    refresh_token = AuthService.create_refresh_token(
        data={"sub": usuario.username, "usuario_id": usuario.id}
    )
    
    # Guardar refresh token
    usuario.token_refresh = refresh_token
    db.commit()
    
    return ResponseSchema(
        success=True,
        message="Login exitoso",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "roles": [r.nombre for r in usuario.roles]
            }
        }
    )

@router_auth.post("/refresh")
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresca el access token usando refresh token"""
    try:
        payload = AuthService.decode_token(refresh_token)
        username = payload.get("sub")
        
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        if not usuario or usuario.token_refresh != refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token inválido")
        
        # Generar nuevo access token
        new_access_token = AuthService.create_access_token(
            data={"sub": usuario.username, "usuario_id": usuario.id}
        )
        
        return ResponseSchema(
            success=True,
            data={
                "access_token": new_access_token,
                "token_type": "bearer"
            }
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

@router_auth.post("/register")
def register(
    username: str,
    email: str,
    password: str,
    roles: list[str] = ["profesional"],
    db: Session = Depends(get_db)
):
    """Registra nuevo usuario"""
    usuario = AuthService.create_user(db, username, email, password, roles)
    return ResponseSchema(
        success=True,
        message="Usuario registrado",
        data={"id": usuario.id, "username": usuario.username}
    )

@router_auth.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout (invalida refresh token)"""
    try:
        token = credentials.credentials
        payload = AuthService.decode_token(token)
        username = payload.get("sub")
        
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        if usuario:
            usuario.token_refresh = None
            db.commit()
        
        return ResponseSchema(success=True, message="Logout exitoso")
    except:
        return ResponseSchema(success=True, message="Logout exitoso")

@router_auth.get("/me")
def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Obtiene información del usuario autenticado"""
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    username = payload.get("sub")
    
    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return ResponseSchema(
        success=True,
        data={
            "id": usuario.id,
            "username": usuario.username,
            "email": usuario.email,
            "estado": usuario.estado,
            "roles": [r.nombre for r in usuario.roles],
            "permisos": AuthService.get_user_permissions(db, usuario.id)
        }
    )