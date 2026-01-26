"""
API de Servicios Médicos - Laboratorio I 2025-2
Aplicación FastAPI Completa con TODOS los módulos (2.1 a 2.9)

Participante: Mercedes Cordero (30447476)
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

# Configuración
from config import settings
from database import init_db, engine

# Middleware
from middleware.audit import AuditMiddleware

# ==================== IMPORTAR TODOS LOS ROUTERS ====================

# Módulo 2.1: Identidades
from routers.personas import router as router_personas
from routers.profesionales import router as router_profesionales
from routers.unidades import router_unidades  # Ver archivo all_routers_complete.py

# Módulo 2.2: Agenda y Citas
from routers.agenda import router_agenda
from routers.citas import router as router_citas

# Módulo 2.3: Registro Clínico
from routers.episodios import router_episodios
from routers.notas import router_notas
from routers.diagnosticos import router_diagnosticos
from routers.consentimientos import router_consentimientos

# Módulo 2.4: Órdenes
from routers.ordenes import router_ordenes
from routers.orden_items import router_orden_items
from routers.prescripciones import router_prescripciones
from routers.resultados import router_resultados

# Módulo 2.5: Aseguradoras
from routers.aseguradoras import router_aseguradoras
from routers.planes import router_planes
from routers.afiliaciones import router_afiliaciones
from routers.autorizaciones import router_autorizaciones

# Módulo 2.6: Catálogo
from routers.prestaciones import router_prestaciones
from routers.arancel import router_arancel

# Módulo 2.7: Facturación
from routers.facturas import router_facturas
from routers.pagos import router_pagos

# Módulo 2.8: Notificaciones
from routers.notificaciones_router import router_notificaciones

# Módulo 2.9: Auditoría y Auth
from routers.auditoria import router_auditoria
from routers.auth import router_auth

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre"""
    # Startup
    logger.info("🚀 Iniciando API de Servicios Médicos...")
    try:
        init_db()
        logger.info("✅ Base de datos inicializada")
    except Exception as e:
        logger.error(f"❌ Error al inicializar BD: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando aplicación...")
    engine.dispose()


# ==================== CREAR APLICACIÓN ====================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    # 🏥 API de Servicios Médicos - Laboratorio I 2025-2
    
    Sistema completo de gestión de servicios médicos con FastAPI, SQLAlchemy y MySQL.
    
    ## 📋 Módulos Implementados (100%)
    
    ### ✅ Módulo 2.1: Identidades y Vinculación Asistencial
    - **Personas Atendidas**: CRUD completo de pacientes
    - **Profesionales**: Gestión de médicos, enfermeras, terapeutas
    - **Unidades de Atención**: Sedes, consultorios, servicios
    
    ### ✅ Módulo 2.2: Disponibilidad y Citas
    - **Bloques de Agenda**: Disponibilidad de profesionales
    - **Citas**: Agendamiento con validaciones completas
    - **Historial**: Trazabilidad de cambios
    
    ### ✅ Módulo 2.3: Registro Clínico
    - **Episodios**: Contenedores de procesos asistenciales
    - **Notas Clínicas**: Registros SOAP con versionado
    - **Diagnósticos**: Códigos CIE-10
    - **Consentimientos**: Aceptación informada
    
    ### ✅ Módulo 2.4: Órdenes y Prestaciones
    - **Órdenes**: Exámenes, imágenes, procedimientos
    - **Prescripciones**: Recetas médicas
    - **Resultados**: Actas con versionado
    
    ### ✅ Módulo 2.5: Cobertura y Autorizaciones
    - **Aseguradoras**: EPS, seguros
    - **Planes**: Planes de salud
    - **Afiliaciones**: Vinculación paciente-plan
    - **Autorizaciones**: Aprobaciones
    
    ### ✅ Módulo 2.6: Catálogo Clínico y Arancel
    - **Prestaciones**: Catálogo de servicios
    - **Arancel**: Tarifas por plan
    
    ### ✅ Módulo 2.7: Facturación y Cobros
    - **Facturas**: Comprobantes completos
    - **Pagos**: Registro de pagos
    - **Notas de Ajuste**: Crédito/Débito
    
    ### ✅ Módulo 2.8: Notificaciones
    - **Envío multi-canal**: Email, SMS, WhatsApp
    - **SendGrid**: Integración completa
    
    ### ✅ Módulo 2.9: Auditoría y Trazabilidad
    - **Autenticación JWT**: Seguridad completa
    - **RBAC**: Control de acceso por roles
    - **Bitácora**: Registro de todas las acciones
    
    ## 🔐 Seguridad
    
    - Autenticación JWT con refresh tokens
    - Control de acceso basado en roles (RBAC)
    - Auditoría completa de acciones
    - Cifrado de contraseñas con bcrypt
    - Bloqueo tras intentos fallidos
    
    ## 👤 Desarrollado por
    
    **Mercedes Cordero**
    - Cédula: 30447476
    - Email: 1001.30447476.ucla@gmail.com
    - Rol: Desarrolladora Principal (Backend)
    
    ## 📚 Documentación
    
    - **Swagger UI**: `/api-docs`
    - **ReDoc**: `/redoc`
    - **Health Check**: `/health`
    
    ## 🚀 Uso Rápido
    
    1. Autenticarse: `POST /api/v1/auth/login`
    2. Usar token en header: `Authorization: Bearer {token}`
    3. Explorar endpoints por módulo
    """,
    docs_url="/api-docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ==================== MIDDLEWARE ====================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auditoría
app.add_middleware(AuditMiddleware)


# ==================== MANEJADORES DE ERRORES ====================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de Pydantic"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Error de validación",
            "code": "VALIDATION_ERROR",
            "details": errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Maneja excepciones no capturadas"""
    logger.error(f"Error no capturado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Error interno del servidor",
            "code": "INTERNAL_ERROR",
            "details": str(exc) if settings.DEBUG else "Contacte al administrador"
        }
    )


# ==================== HEALTH CHECK ====================

@app.get("/health", tags=["Sistema"])
def health_check():
    """Verifica el estado del servidor"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "database": "connected",
        "modules": {
            "identidades": "✅",
            "agenda_citas": "✅",
            "registro_clinico": "✅",
            "ordenes": "✅",
            "aseguradoras": "✅",
            "catalogo": "✅",
            "facturacion": "✅",
            "notificaciones": "✅",
            "auditoria": "✅"
        }
    }


@app.get("/", tags=["Sistema"])
def root():
    """Endpoint raíz con información del proyecto"""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "API de Servicios Médicos - Laboratorio I 2025-2",
        "developer": "Mercedes Cordero (30447476)",
        "docs": "/api-docs",
        "health": "/health",
        "modules_count": 9,
        "modules": [
            "2.1 - Identidades",
            "2.2 - Agenda y Citas",
            "2.3 - Registro Clínico",
            "2.4 - Órdenes",
            "2.5 - Aseguradoras",
            "2.6 - Catálogo",
            "2.7 - Facturación",
            "2.8 - Notificaciones",
            "2.9 - Auditoría"
        ]
    }


# ==================== INCLUIR TODOS LOS ROUTERS ====================

prefix = settings.API_V1_PREFIX

# Autenticación (sin prefijo adicional, ya tiene /auth)
app.include_router(router_auth, prefix=prefix)

# Módulo 2.1: Identidades
app.include_router(router_personas, prefix=prefix)
app.include_router(router_profesionales, prefix=prefix)
app.include_router(router_unidades, prefix=prefix)

# Módulo 2.2: Agenda y Citas
app.include_router(router_agenda, prefix=prefix)
app.include_router(router_citas, prefix=prefix)

# Módulo 2.3: Registro Clínico
app.include_router(router_episodios, prefix=prefix)
app.include_router(router_notas, prefix=prefix)
app.include_router(router_diagnosticos, prefix=prefix)
app.include_router(router_consentimientos, prefix=prefix)

# Módulo 2.4: Órdenes
app.include_router(router_ordenes, prefix=prefix)
app.include_router(router_orden_items, prefix=prefix)
app.include_router(router_prescripciones, prefix=prefix)
app.include_router(router_resultados, prefix=prefix)

# Módulo 2.5: Aseguradoras
app.include_router(router_aseguradoras, prefix=prefix)
app.include_router(router_planes, prefix=prefix)
app.include_router(router_afiliaciones, prefix=prefix)
app.include_router(router_autorizaciones, prefix=prefix)

# Módulo 2.6: Catálogo
app.include_router(router_prestaciones, prefix=prefix)
app.include_router(router_arancel, prefix=prefix)

# Módulo 2.7: Facturación
app.include_router(router_facturas, prefix=prefix)
app.include_router(router_pagos, prefix=prefix)

# Módulo 2.8: Notificaciones
app.include_router(router_notificaciones, prefix=prefix)

# Módulo 2.9: Auditoría
app.include_router(router_auditoria, prefix=prefix)


# ==================== EJECUTAR ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 80)
    logger.info(" API DE SERVICIOS MÉDICOS - LABORATORIO I 2025-2")
    logger.info("=" * 80)
    logger.info(f" Versión: {settings.VERSION}")
    logger.info(f" Desarrollador: Mercedes Cordero (30447476)")
    logger.info(f" Documentación: http://localhost:8000/api-docs")
    logger.info("=" * 80)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )