"""
Router: Personas Atendidas (Pacientes) - Módulo 2.1
CRUD completo con filtros, paginación y búsqueda
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import date, datetime
from database import get_db
from models.identidades import PersonaAtendida, TipoDocumentoEnum, SexoEnum, EstadoGeneralEnum
from schemas.base import ResponseSchema, PaginatedResponse

router = APIRouter(prefix="/personas", tags=["Personas Atendidas"])


# CREATE
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_persona(
    tipo_documento: TipoDocumentoEnum,
    numero_documento: str,
    nombres: str,
    apellidos: str,
    fecha_nacimiento: date,
    sexo: SexoEnum,
    correo: str,
    telefono: str,
    direccion: str,
    contacto_emergencia: str,
    alergias: Optional[List[str]] = None,
    antecedentes_resumen: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Crea una nueva persona atendida (paciente)"""
    
    # Validar documento único
    existe = db.query(PersonaAtendida).filter(
        PersonaAtendida.numero_documento == numero_documento
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una persona con documento {numero_documento}"
        )
    
    # Validar correo único
    existe_correo = db.query(PersonaAtendida).filter(
        PersonaAtendida.correo == correo
    ).first()
    
    if existe_correo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El correo {correo} ya está registrado"
        )
    
    persona = PersonaAtendida(
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombres=nombres,
        apellidos=apellidos,
        fecha_nacimiento=fecha_nacimiento,
        sexo=sexo,
        correo=correo,
        telefono=telefono,
        direccion=direccion,
        contacto_emergencia=contacto_emergencia,
        alergias=alergias or [],
        antecedentes_resumen=antecedentes_resumen,
        estado=EstadoGeneralEnum.ACTIVO
    )
    
    db.add(persona)
    db.commit()
    db.refresh(persona)
    
    return ResponseSchema(
        success=True,
        message="Persona creada exitosamente",
        data=persona.to_dict()
    )


# READ - LIST con filtros
@router.get("/")
def listar_personas(
    documento: Optional[str] = None,
    nombres: Optional[str] = None,
    apellidos: Optional[str] = None,
    edad_min: Optional[int] = None,
    edad_max: Optional[int] = None,
    sexo: Optional[SexoEnum] = None,
    estado: Optional[EstadoGeneralEnum] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lista personas con filtros múltiples y paginación"""
    
    query = db.query(PersonaAtendida)
    
    # Filtros específicos
    if documento:
        query = query.filter(PersonaAtendida.numero_documento.contains(documento))
    
    if nombres:
        query = query.filter(PersonaAtendida.nombres.ilike(f"%{nombres}%"))
    
    if apellidos:
        query = query.filter(PersonaAtendida.apellidos.ilike(f"%{apellidos}%"))
    
    if sexo:
        query = query.filter(PersonaAtendida.sexo == sexo)
    
    if estado:
        query = query.filter(PersonaAtendida.estado == estado)
    
    # Filtro por edad
    if edad_min or edad_max:
        hoy = date.today()
        if edad_max:
            fecha_max = date(hoy.year - edad_max, hoy.month, hoy.day)
            query = query.filter(PersonaAtendida.fecha_nacimiento >= fecha_max)
        if edad_min:
            fecha_min = date(hoy.year - edad_min, hoy.month, hoy.day)
            query = query.filter(PersonaAtendida.fecha_nacimiento <= fecha_min)
    
    # Búsqueda global
    if search:
        query = query.filter(
            or_(
                PersonaAtendida.nombres.ilike(f"%{search}%"),
                PersonaAtendida.apellidos.ilike(f"%{search}%"),
                PersonaAtendida.numero_documento.contains(search),
                PersonaAtendida.correo.ilike(f"%{search}%")
            )
        )
    
    # Paginación
    total = query.count()
    personas = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        success=True,
        data=[p.to_dict() for p in personas],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# READ - GET por ID
@router.get("/{persona_id}")
def obtener_persona(
    persona_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene una persona por ID con toda su información"""
    
    persona = db.query(PersonaAtendida).filter(PersonaAtendida.id == persona_id).first()
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona con ID {persona_id} no encontrada"
        )
    
    data = persona.to_dict()
    
    # Agregar información adicional
    data['edad'] = (date.today() - persona.fecha_nacimiento).days // 365
    data['total_citas'] = len(persona.citas)
    data['total_episodios'] = len(persona.episodios)
    
    return ResponseSchema(
        success=True,
        message="Persona encontrada",
        data=data
    )


# UPDATE - PATCH
@router.patch("/{persona_id}")
def actualizar_persona(
    persona_id: int,
    nombres: Optional[str] = None,
    apellidos: Optional[str] = None,
    correo: Optional[str] = None,
    telefono: Optional[str] = None,
    direccion: Optional[str] = None,
    contacto_emergencia: Optional[str] = None,
    alergias: Optional[List[str]] = None,
    antecedentes_resumen: Optional[str] = None,
    estado: Optional[EstadoGeneralEnum] = None,
    db: Session = Depends(get_db)
):
    """Actualiza datos de una persona (actualización parcial)"""
    
    persona = db.query(PersonaAtendida).filter(PersonaAtendida.id == persona_id).first()
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona con ID {persona_id} no encontrada"
        )
    
    # Actualizar solo campos proporcionados
    if nombres:
        persona.nombres = nombres
    if apellidos:
        persona.apellidos = apellidos
    if correo:
        # Validar que el correo no esté en uso
        existe = db.query(PersonaAtendida).filter(
            PersonaAtendida.correo == correo,
            PersonaAtendida.id != persona_id
        ).first()
        if existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El correo {correo} ya está en uso"
            )
        persona.correo = correo
    if telefono:
        persona.telefono = telefono
    if direccion:
        persona.direccion = direccion
    if contacto_emergencia:
        persona.contacto_emergencia = contacto_emergencia
    if alergias is not None:
        persona.alergias = alergias
    if antecedentes_resumen is not None:
        persona.antecedentes_resumen = antecedentes_resumen
    if estado:
        persona.estado = estado
    
    db.commit()
    db.refresh(persona)
    
    return ResponseSchema(
        success=True,
        message="Persona actualizada exitosamente",
        data=persona.to_dict()
    )


# DELETE - Lógico
@router.delete("/{persona_id}")
def eliminar_persona(
    persona_id: int,
    db: Session = Depends(get_db)
):
    """Elimina lógicamente una persona (cambia estado a INACTIVO)"""
    
    persona = db.query(PersonaAtendida).filter(PersonaAtendida.id == persona_id).first()
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona con ID {persona_id} no encontrada"
        )
    
    persona.estado = EstadoGeneralEnum.INACTIVO
    persona.is_active = False
    
    db.commit()
    
    return ResponseSchema(
        success=True,
        message="Persona eliminada exitosamente (inactivada)"
    )


# ENDPOINTS ADICIONALES

@router.get("/{persona_id}/citas")
def obtener_citas_persona(
    persona_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene todas las citas de una persona"""
    
    persona = db.query(PersonaAtendida).filter(PersonaAtendida.id == persona_id).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    citas = [c.to_dict() for c in persona.citas]
    
    return ResponseSchema(
        success=True,
        data=citas
    )


@router.get("/{persona_id}/episodios")
def obtener_episodios_persona(
    persona_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene todos los episodios de atención de una persona"""
    
    persona = db.query(PersonaAtendida).filter(PersonaAtendida.id == persona_id).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    episodios = [e.to_dict() for e in persona.episodios]
    
    return ResponseSchema(
        success=True,
        data=episodios
    )