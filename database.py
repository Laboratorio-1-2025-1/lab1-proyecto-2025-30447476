"""
Configuración de base de datos MySQL con SQLAlchemy
Incluye sesión, base declarativa y utilidades
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from config import settings
import logging

logger = logging.getLogger(__name__)

# Motor de base de datos con pool de conexiones
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_recycle=3600,   # Recicla conexiones cada hora
    echo=settings.DEBUG,  # Muestra SQL en modo debug
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos declarativos
Base = declarative_base()


# Event listeners para MySQL
@event.listens_for(engine, "connect")
def set_mysql_pragma(dbapi_conn, connection_record):
    """Configura parámetros de MySQL al conectar"""
    cursor = dbapi_conn.cursor()
    cursor.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'")
    cursor.execute("SET SESSION time_zone='+00:00'")
    cursor.close()


def get_db() -> Session:
    """
    Dependency para obtener sesión de base de datos
    Uso en FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        raise


def drop_all_tables():
    """PELIGRO: Elimina todas las tablas - Solo para desarrollo"""
    if not settings.DEBUG:
        raise Exception("No se puede eliminar tablas en producción")
    Base.metadata.drop_all(bind=engine)
    logger.warning("Todas las tablas eliminadas")