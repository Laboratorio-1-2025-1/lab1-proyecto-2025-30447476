"""Punto de entrada de la API"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import os

# Importar todos los modelos
from models import usuario, rol, usuario_rol, persona_atendida
# Importar routers
from routers import auth, personas_atendidas

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Servicios Médicos",
    description="Plataforma para gestión de servicios de salud",
    version="1.0.0",
    docs_url="/api-docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth.router)
app.include_router(personas_atendidas.router)

@app.get("/health")
def health_check():
    """Health check"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )