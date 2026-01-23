"""Schemas de autenticación"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    roles: List[int] = []  # IDs de roles

class UsuarioResponse(BaseModel):
    id: int
    username: str
    email: str
    estado: str
    roles: List[str] = []
    
    class Config:
        from_attributes = True