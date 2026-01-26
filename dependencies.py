"""
Dependencias compartidas para routers
Incluye autenticación, permisos y utilidades
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models.auditoria import Usuario
from services.auth_service import AuthService

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Obtiene el usuario actual desde el token JWT
    Retorna dict con información del usuario
    """
    try:
        token = credentials.credentials
        payload = AuthService.decode_token(token)
        
        username = payload.get("sub")
        usuario_id = payload.get("usuario_id")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        
        if not usuario or not usuario.estado:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo"
            )
        
        return {
            "usuario_id": usuario.id,
            "username": usuario.username,
            "email": usuario.email,
            "roles": [r.nombre for r in usuario.roles]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}"
        )


def check_permission(permission: str):
    """
    Decorator para verificar permisos específicos
    Uso: @router.get("/", dependencies=[Depends(check_permission("personas.read"))])
    """
    def _check(
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        permisos = AuthService.get_user_permissions(db, current_user["usuario_id"])
        
        if permission not in permisos and "admin.all" not in permisos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permiso: {permission}"
            )
        
        return True
    
    return _check


def require_role(role_name: str):
    """
    Decorator para requerir un rol específico
    Uso: @router.delete("/", dependencies=[Depends(require_role("administrador"))])
    """
    def _require(current_user: dict = Depends(get_current_user)):
        if role_name not in current_user["roles"] and "administrador" not in current_user["roles"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere rol: {role_name}"
            )
        return True
    
    return _require


# Dependencias opcionales para endpoints públicos
def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> dict | None:
    """
    Obtiene usuario si hay token, None si no
    Para endpoints que funcionan con o sin autenticación
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except:
        return None