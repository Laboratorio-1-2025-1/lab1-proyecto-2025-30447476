from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

# Importar configuración de base de datos
from database import engine, Base, check_connection, create_tables

# Importar routers
from routers.servicios import router as servicios_router

# Cargar variables de entorno
load_dotenv()

# Crear instancia de FastAPI
app = FastAPI(
    title="API de Servicios Médicos",
    description="API REST para la gestión de servicios médicos, pacientes y citas",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicio: crear tablas y verificar conexión
@app.on_event("startup")
async def startup_event():
    print("🚀 Iniciando API de Servicios Médicos...")
    
    # Verificar conexión a la base de datos
    if check_connection():
        print("✅ Conexión a MySQL exitosa")
        
        # Crear tablas si no existen
        try:
            create_tables()
            print("✅ Tablas verificadas/creadas")
        except Exception as e:
            print(f"⚠️ Error al crear tablas: {e}")
    else:
        print("❌ No se pudo conectar a la base de datos")

# Evento de cierre
@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Cerrando API de Servicios Médicos...")

# ============================================
# RUTAS DE SALUD
# ============================================

@app.get("/", tags=["Health"])
def root():
    """Endpoint raíz - Información de la API"""
    return {
        "status": "ok",
        "service": "API Servicios Médicos",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check - Verificar estado del servicio"""
    db_status = "connected" if check_connection() else "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "service": "API Servicios Médicos"
    }

# ============================================
# REGISTRAR ROUTERS
# ============================================

app.include_router(
    servicios_router,
    prefix="/api/v1/servicios",
    tags=["Servicios Médicos"]
)

# app.include_router(pacientes_router, prefix="/api/v1/pacientes", tags=["Pacientes"])
# app.include_router(citas_router, prefix="/api/v1/citas", tags=["Citas"])

# ============================================
# PUNTO DE ENTRADA
# ============================================

if __name__ == "__main__":
    # Configuración del servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 2000))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    
    print(f"🌐 Servidor corriendo en http://{host}:{port}")
    print(f"📚 Documentación disponible en http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )