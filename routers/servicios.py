from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.servicio import Servicio
from schemas.servicio import ServicioCreate, ServicioUpdate, ServicioResponse, MessageResponse

router = APIRouter()

# ============================================
# ENDPOINTS CRUD PARA SERVICIOS
# ============================================

@router.get("/", response_model=List[ServicioResponse])
def listar_servicios(
    skip: int = 0,
    limit: int = 100,
    activo: bool = None,
    db: Session = Depends(get_db)
):
    """
    Listar todos los servicios médicos
    - **skip**: número de registros a saltar
    - **limit**: número máximo de registros a retornar
    - **activo**: filtrar por servicios activos/inactivos
    """
    query = db.query(Servicio)
    
    if activo is not None:
        query = query.filter(Servicio.activo == activo)
    
    servicios = query.offset(skip).limit(limit).all()
    return servicios


@router.get("/{servicio_id}", response_model=ServicioResponse)
def obtener_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """
    Obtener un servicio por su ID
    """
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {servicio_id} no encontrado"
        )
    
    return servicio


@router.post("/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_servicio(servicio: ServicioCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo servicio médico
    """
    # Verificar si ya existe un servicio con el mismo nombre
    servicio_existente = db.query(Servicio).filter(
        Servicio.nombre == servicio.nombre
    ).first()
    
    if servicio_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un servicio con el nombre '{servicio.nombre}'"
        )
    
    # Crear nuevo servicio
    nuevo_servicio = Servicio(**servicio.model_dump())
    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)
    
    return nuevo_servicio


@router.put("/{servicio_id}", response_model=ServicioResponse)
def actualizar_servicio(
    servicio_id: int,
    servicio_update: ServicioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un servicio existente
    """
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {servicio_id} no encontrado"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = servicio_update.model_dump(exclude_unset=True)
    
    for campo, valor in update_data.items():
        setattr(servicio, campo, valor)
    
    db.commit()
    db.refresh(servicio)
    
    return servicio


@router.delete("/{servicio_id}", response_model=MessageResponse)
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un servicio (eliminación lógica)
    """
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {servicio_id} no encontrado"
        )
    
    # Eliminación lógica (marcar como inactivo)
    servicio.activo = False
    db.commit()
    
    return {
        "message": f"Servicio '{servicio.nombre}' desactivado exitosamente",
        "status": "success"
    }


@router.delete("/{servicio_id}/permanente", response_model=MessageResponse)
def eliminar_servicio_permanente(servicio_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un servicio permanentemente de la base de datos
    """
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {servicio_id} no encontrado"
        )
    
    nombre_servicio = servicio.nombre
    db.delete(servicio)
    db.commit()
    
    return {
        "message": f"Servicio '{nombre_servicio}' eliminado permanentemente",
        "status": "success"
    }


@router.patch("/{servicio_id}/activar", response_model=ServicioResponse)
def activar_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """
    Activar un servicio desactivado
    """
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {servicio_id} no encontrado"
        )
    
    servicio.activo = True
    db.commit()
    db.refresh(servicio)
    
    return servicio
