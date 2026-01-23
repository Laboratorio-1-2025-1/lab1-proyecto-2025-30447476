"""Endpoints de autenticación"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import LoginRequest, TokenResponse, UsuarioCreate, RefreshTokenRequest
from services.auth_service import AuthService
from utils.jwt_handler import decode_token, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión"""
    return AuthService.login(db, credentials)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    usuario = AuthService.register(db, usuario_data)
    return {"message": "Usuario creado exitosamente", "id": usuario.id}

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest):
    """Refrescar token de acceso"""
    payload = decode_token(request.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido"
        )
    
    new_access_token = create_access_token({"sub": payload["sub"]})
    
    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer"
    }