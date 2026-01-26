"""
Router: Episodios de Atención - Módulo 2.3
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from database import get_db
from models.registro_clinico import EpisodioAtencion, TipoEpisodioEnum, EstadoEpisodioEnum
from models.ordenes import EstadoOrdenEnum
from schemas.base import ResponseSchema

router_episodios = APIRouter(prefix="/episodios", tags=["Episodios de Atención"])

@router_episodios.post("/", status_code=status.HTTP_201_CREATED)
def crear_episodio(
    persona_id: int,
    motivo: str,
    tipo: TipoEpisodioEnum,
    db: Session = Depends(get_db)
):
    episodio = EpisodioAtencion(
        persona_id=persona_id,
        fecha_apertura=datetime.utcnow(),
        motivo=motivo,
        tipo=tipo,
        estado=EstadoEpisodioEnum.ABIERTO
    )
    db.add(episodio)
    db.commit()
    db.refresh(episodio)
    return ResponseSchema(success=True, message="Episodio creado", data=episodio.to_dict())

@router_episodios.get("/")
def listar_episodios(
    persona_id: Optional[int] = None,
    tipo: Optional[TipoEpisodioEnum] = None,
    estado: Optional[EstadoEpisodioEnum] = None,
    db: Session = Depends(get_db)
):
    query = db.query(EpisodioAtencion)
    if persona_id:
        query = query.filter(EpisodioAtencion.persona_id == persona_id)
    if tipo:
        query = query.filter(EpisodioAtencion.tipo == tipo)
    if estado:
        query = query.filter(EpisodioAtencion.estado == estado)
    
    episodios = query.all()
    return ResponseSchema(success=True, data=[e.to_dict() for e in episodios])

@router_episodios.get("/{episodio_id}")
def obtener_episodio(episodio_id: int, db: Session = Depends(get_db)):
    episodio = db.query(EpisodioAtencion).filter(EpisodioAtencion.id == episodio_id).first()
    if not episodio:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    
    data = episodio.to_dict()
    data['total_notas'] = len(episodio.notas_clinicas)
    data['total_diagnosticos'] = len(episodio.diagnosticos)
    data['total_ordenes'] = len(episodio.ordenes)
    return ResponseSchema(success=True, data=data)

@router_episodios.patch("/{episodio_id}/cerrar")
def cerrar_episodio(
    episodio_id: int,
    resumen_final: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """REGLA DE NEGOCIO: Solo cierra si no hay órdenes en curso"""
    episodio = db.query(EpisodioAtencion).filter(EpisodioAtencion.id == episodio_id).first()
    if not episodio:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    
    # Verificar órdenes en curso
    ordenes_pendientes = [o for o in episodio.ordenes if o.estado == EstadoOrdenEnum.EN_CURSO]
    if ordenes_pendientes:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede cerrar. Hay {len(ordenes_pendientes)} órdenes en curso"
        )
    
    episodio.estado = EstadoEpisodioEnum.CERRADO
    episodio.fecha_cierre = datetime.utcnow()
    episodio.resumen_final = resumen_final
    db.commit()
    return ResponseSchema(success=True, message="Episodio cerrado")


### ARCHIVO: routers/notas.py
"""
Router: Notas Clínicas - Módulo 2.3
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from database import get_db
from models.registro_clinico import NotaClinica
from schemas.base import ResponseSchema

router_notas = APIRouter(prefix="/notas", tags=["Notas Clínicas"])

@router_notas.post("/", status_code=status.HTTP_201_CREATED)
def crear_nota(
    episodio_id: int,
    profesional_id: int,
    subjetivo: Optional[str] = None,
    objetivo: Optional[str] = None,
    analisis: Optional[str] = None,
    plan: Optional[str] = None,
    adjuntos: Optional[list] = None,
    db: Session = Depends(get_db)
):
    """Crea nota clínica con formato SOAP"""
    nota = NotaClinica(
        episodio_id=episodio_id,
        profesional_id=profesional_id,
        fecha=datetime.utcnow(),
        subjetivo=subjetivo,
        objetivo=objetivo,
        analisis=analisis,
        plan=plan,
        adjuntos=adjuntos,
        version=1
    )
    db.add(nota)
    db.commit()
    db.refresh(nota)
    return ResponseSchema(success=True, message="Nota creada", data=nota.to_dict())

@router_notas.post("/{nota_id}/version")
def crear_version_nota(
    nota_id: int,
    subjetivo: Optional[str] = None,
    objetivo: Optional[str] = None,
    analisis: Optional[str] = None,
    plan: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """REGLA DE NEGOCIO: No sobrescribir, crear nueva versión"""
    nota_original = db.query(NotaClinica).filter(NotaClinica.id == nota_id).first()
    if not nota_original:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    
    nueva_version = NotaClinica(
        episodio_id=nota_original.episodio_id,
        profesional_id=nota_original.profesional_id,
        fecha=datetime.utcnow(),
        subjetivo=subjetivo or nota_original.subjetivo,
        objetivo=objetivo or nota_original.objetivo,
        analisis=analisis or nota_original.analisis,
        plan=plan or nota_original.plan,
        version=nota_original.version + 1,
        nota_padre_id=nota_original.id
    )
    db.add(nueva_version)
    db.commit()
    db.refresh(nueva_version)
    return ResponseSchema(success=True, message="Nueva versión creada", data=nueva_version.to_dict())

@router_notas.get("/episodio/{episodio_id}")
def listar_notas_episodio(episodio_id: int, db: Session = Depends(get_db)):
    notas = db.query(NotaClinica).filter(NotaClinica.episodio_id == episodio_id).all()
    return ResponseSchema(success=True, data=[n.to_dict() for n in notas])
