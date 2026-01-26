"""Router: Resultados de Órdenes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from database import get_db
from models.ordenes import Resultado
from schemas.base import ResponseSchema

router_resultados = APIRouter(prefix="/resultados", tags=["Resultados"])

@router_resultados.post("/")
def crear_resultado(
    orden_id: int,
    resumen: Optional[str] = None,
    archivo_id: Optional[str] = None,
    validado_por_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    resultado = Resultado(
        orden_id=orden_id,
        fecha=datetime.utcnow(),
        resumen=resumen,
        archivo_id=archivo_id,
        version=1,
        validado_por_id=validado_por_id,
        fecha_validacion=datetime.utcnow() if validado_por_id else None
    )
    db.add(resultado)
    db.commit()
    db.refresh(resultado)
    return ResponseSchema(success=True, message="Resultado creado", data=resultado.to_dict())

@router_resultados.post("/{resultado_id}/version")
def crear_version_resultado(
    resultado_id: int,
    resumen: Optional[str] = None,
    archivo_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Crea nueva versión del resultado"""
    resultado_original = db.query(Resultado).filter(Resultado.id == resultado_id).first()
    if not resultado_original:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")
    
    nueva_version = Resultado(
        orden_id=resultado_original.orden_id,
        fecha=datetime.utcnow(),
        resumen=resumen or resultado_original.resumen,
        archivo_id=archivo_id or resultado_original.archivo_id,
        version=resultado_original.version + 1,
        resultado_padre_id=resultado_original.id
    )
    db.add(nueva_version)
    db.commit()
    db.refresh(nueva_version)
    return ResponseSchema(success=True, message="Nueva versión creada", data=nueva_version.to_dict())


### ARCHIVO: routers/aseguradoras.py
"""Router: Aseguradoras - Módulo 2.5"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.aseguradoras import Aseguradora, EstadoAseguradoraEnum
from schemas.base import ResponseSchema

router_aseguradoras = APIRouter(prefix="/aseguradoras", tags=["Aseguradoras"])

@router_aseguradoras.post("/")
def crear_aseguradora(
    nombre: str,
    nit: str,
    contacto: Optional[str] = None,
    telefono: Optional[str] = None,
    correo: Optional[str] = None,
    direccion: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Validar NIT único
    existe = db.query(Aseguradora).filter(Aseguradora.nit == nit).first()
    if existe:
        raise HTTPException(status_code=400, detail="NIT ya existe")
    
    aseguradora = Aseguradora(
        nombre=nombre,
        nit=nit,
        contacto=contacto,
        telefono=telefono,
        correo=correo,
        direccion=direccion,
        estado=EstadoAseguradoraEnum.ACTIVA
    )
    db.add(aseguradora)
    db.commit()
    db.refresh(aseguradora)
    return ResponseSchema(success=True, message="Aseguradora creada", data=aseguradora.to_dict())

@router_aseguradoras.get("/")
def listar_aseguradoras(
    estado: Optional[EstadoAseguradoraEnum] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Aseguradora)
    if estado:
        query = query.filter(Aseguradora.estado == estado)
    
    aseguradoras = query.all()
    return ResponseSchema(success=True, data=[a.to_dict() for a in aseguradoras])

@router_aseguradoras.get("/{aseguradora_id}")
def obtener_aseguradora(aseguradora_id: int, db: Session = Depends(get_db)):
    aseguradora = db.query(Aseguradora).filter(Aseguradora.id == aseguradora_id).first()
    if not aseguradora:
        raise HTTPException(status_code=404, detail="Aseguradora no encontrada")
    return ResponseSchema(success=True, data=aseguradora.to_dict())
