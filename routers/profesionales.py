"""
Router: Profesionales de Salud - Módulo 2.1
CRUD completo para médicos, enfermeras, terapeutas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from database import get_db
from models.identidades import Profesional, EstadoGeneralEnum
from schemas.base import ResponseSchema, PaginatedResponse

router = APIRouter(prefix="/profesionales", tags=["Profesionales"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_profesional(
    nombres: str,
    apellidos: str,
    registro_profesional: str,
    especialidad: str,
    correo: str,
    telefono: str,
    agenda_habilitada: bool = True,
    db: Session = Depends(get_db)
):
    """Crea un nuevo profesional de salud"""
    
    # Validar registro único
    existe = db.query(Profesional).filter(
        Profesional.registro_profesional == registro_profesional
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un profesional con registro {registro_profesional}"
        )
    
    # Validar correo único
    existe_correo = db.query(Profesional).filter(
        Profesional.correo == correo
    ).first()
    
    if existe_correo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El correo {correo} ya está registrado"
        )
    
    profesional = Profesional(
        nombres=nombres,
        apellidos=apellidos,
        registro_profesional=registro_profesional,
        especialidad=especialidad,
        correo=correo,
        telefono=telefono,
        agenda_habilitada=agenda_habilitada,
        estado=EstadoGeneralEnum.ACTIVO
    )
    
    db.add(profesional)
    db.commit()
    db.refresh(profesional)
    
    return ResponseSchema(
        success=True,
        message="Profesional creado exitosamente",
        data=profesional.to_dict()
    )


@router.get("/")
def listar_profesionales(
    nombres: Optional[str] = None,
    apellidos: Optional[str] = None,
    registro: Optional[str] = None,
    especialidad: Optional[str] = None,
    estado: Optional[EstadoGeneralEnum] = None,
    agenda_habilitada: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lista profesionales con filtros"""
    
    query = db.query(Profesional)
    
    if nombres:
        query = query.filter(Profesional.nombres.ilike(f"%{nombres}%"))
    
    if apellidos:
        query = query.filter(Profesional.apellidos.ilike(f"%{apellidos}%"))
    
    if registro:
        query = query.filter(Profesional.registro_profesional.contains(registro))
    
    if especialidad:
        query = query.filter(Profesional.especialidad.ilike(f"%{especialidad}%"))
    
    if estado:
        query = query.filter(Profesional.estado == estado)
    
    if agenda_habilitada is not None:
        query = query.filter(Profesional.agenda_habilitada == agenda_habilitada)
    
    if search:
        query = query.filter(
            or_(
                Profesional.nombres.ilike(f"%{search}%"),
                Profesional.apellidos.ilike(f"%{search}%"),
                Profesional.registro_profesional.contains(search),
                Profesional.especialidad.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    profesionales = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        success=True,
        data=[p.to_dict() for p in profesionales],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{profesional_id}")
def obtener_profesional(
    profesional_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene un profesional por ID"""
    
    profesional = db.query(Profesional).filter(Profesional.id == profesional_id).first()
    
    if not profesional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesional con ID {profesional_id} no encontrado"
        )
    
    data = profesional.to_dict()
    data['total_bloques_agenda'] = len(profesional.bloques_agenda)
    data['total_citas'] = len(profesional.citas)
    
    return ResponseSchema(
        success=True,
        message="Profesional encontrado",
        data=data
    )


@router.patch("/{profesional_id}")
def actualizar_profesional(
    profesional_id: int,
    nombres: Optional[str] = None,
    apellidos: Optional[str] = None,
    especialidad: Optional[str] = None,
    correo: Optional[str] = None,
    telefono: Optional[str] = None,
    agenda_habilitada: Optional[bool] = None,
    estado: Optional[EstadoGeneralEnum] = None,
    db: Session = Depends(get_db)
):
    """Actualiza datos de un profesional"""
    
    profesional = db.query(Profesional).filter(Profesional.id == profesional_id).first()
    
    if not profesional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesional con ID {profesional_id} no encontrado"
        )
    
    if nombres:
        profesional.nombres = nombres
    if apellidos:
        profesional.apellidos = apellidos
    if especialidad:
        profesional.especialidad = especialidad
    if correo:
        existe = db.query(Profesional).filter(
            Profesional.correo == correo,
            Profesional.id != profesional_id
        ).first()
        if existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El correo {correo} ya está en uso"
            )
        profesional.correo = correo
    if telefono:
        profesional.telefono = telefono
    if agenda_habilitada is not None:
        profesional.agenda_habilitada = agenda_habilitada
    if estado:
        profesional.estado = estado
    
    db.commit()
    db.refresh(profesional)
    
    return ResponseSchema(
        success=True,
        message="Profesional actualizado exitosamente",
        data=profesional.to_dict()
    )


@router.delete("/{profesional_id}")
def eliminar_profesional(
    profesional_id: int,
    db: Session = Depends(get_db)
):
    """Elimina lógicamente un profesional"""
    
    profesional = db.query(Profesional).filter(Profesional.id == profesional_id).first()
    
    if not profesional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesional con ID {profesional_id} no encontrado"
        )
    
    profesional.estado = EstadoGeneralEnum.INACTIVO
    profesional.is_active = False
    profesional.agenda_habilitada = False
    
    db.commit()
    
    return ResponseSchema(
        success=True,
        message="Profesional eliminado exitosamente"
    )


@router.get("/{profesional_id}/agenda")
def obtener_agenda_profesional(
    profesional_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene todos los bloques de agenda de un profesional"""
    
    profesional = db.query(Profesional).filter(Profesional.id == profesional_id).first()
    
    if not profesional:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    
    bloques = [b.to_dict() for b in profesional.bloques_agenda]
    
    return ResponseSchema(
        success=True,
        data=bloques
    )


@router.get("/{profesional_id}/citas")
def obtener_citas_profesional(
    profesional_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene todas las citas de un profesional"""
    
    profesional = db.query(Profesional).filter(Profesional.id == profesional_id).first()
    
    if not profesional:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    
    citas = [c.to_dict() for c in profesional.citas]
    
    return ResponseSchema(
        success=True,
        data=citas
    )