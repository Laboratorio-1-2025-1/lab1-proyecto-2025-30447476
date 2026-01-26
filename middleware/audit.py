"""
Middleware de Auditoría
Registra todas las peticiones en BitacoraAcceso
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.orm import Session
from database import SessionLocal
from models.auditoria import BitacoraAcceso, TipoAccionEnum
import time
import json


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra todas las peticiones HTTP
    en la tabla de auditoría
    """
    
    async def dispatch(self, request: Request, call_next):
        # Obtener datos de la petición
        start_time = time.time()
        ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        metodo = request.method
        path = request.url.path
        
        # Obtener usuario si está autenticado
        usuario_id = None
        if hasattr(request.state, "usuario_id"):
            usuario_id = request.state.usuario_id
        
        # Ejecutar petición
        response = await call_next(request)
        
        # Calcular tiempo de procesamiento
        process_time = time.time() - start_time
        
        # Determinar acción según método HTTP
        accion_map = {
            "GET": TipoAccionEnum.READ,
            "POST": TipoAccionEnum.CREATE,
            "PUT": TipoAccionEnum.UPDATE,
            "PATCH": TipoAccionEnum.UPDATE,
            "DELETE": TipoAccionEnum.DELETE
        }
        accion = accion_map.get(metodo, TipoAccionEnum.READ)
        
        # Determinar resultado
        if response.status_code < 300:
            resultado = "success"
        elif response.status_code < 500:
            resultado = "error"
        else:
            resultado = "server_error"
        
        # Registrar en base de datos (async para no bloquear)
        try:
            self._registrar_auditoria(
                usuario_id=usuario_id,
                recurso=path,
                accion=accion,
                metodo_http=metodo,
                ip=ip,
                user_agent=user_agent,
                resultado=resultado,
                codigo_http=response.status_code,
                tiempo_procesamiento=process_time
            )
        except Exception as e:
            # No fallar la petición si falla el logging
            print(f"Error en auditoría: {e}")
        
        return response
    
    def _registrar_auditoria(
        self,
        usuario_id,
        recurso,
        accion,
        metodo_http,
        ip,
        user_agent,
        resultado,
        codigo_http,
        tiempo_procesamiento
    ):
        """Registra en base de datos de forma síncrona"""
        db = SessionLocal()
        try:
            bitacora = BitacoraAcceso(
                usuario_id=usuario_id,
                recurso=recurso,
                accion=accion,
                metodo_http=metodo_http,
                ip=ip,
                user_agent=user_agent[:500],  # Limitar longitud
                resultado=resultado,
                codigo_http=codigo_http
            )
            db.add(bitacora)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error guardando auditoría: {e}")
        finally:
            db.close()


class SensitiveDataFilter:
    """
    Filtro para ofuscar datos sensibles en logs
    """
    
    SENSITIVE_FIELDS = [
        "password", "password_hash", "token", "token_refresh",
        "numero_documento", "telefono", "correo"
    ]
    
    @staticmethod
    def filter_dict(data: dict) -> dict:
        """Ofusca campos sensibles en diccionario"""
        filtered = data.copy()
        for key in filtered:
            if key.lower() in SensitiveDataFilter.SENSITIVE_FIELDS:
                filtered[key] = "***"
            elif isinstance(filtered[key], dict):
                filtered[key] = SensitiveDataFilter.filter_dict(filtered[key])
        return filtered
    
    @staticmethod
    def filter_json(json_str: str) -> str:
        """Ofusca campos sensibles en JSON string"""
        try:
            data = json.loads(json_str)
            filtered = SensitiveDataFilter.filter_dict(data)
            return json.dumps(filtered)
        except:
            return json_str