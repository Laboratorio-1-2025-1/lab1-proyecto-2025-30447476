"""
Router de Citas (Módulo 2.2)
Implementa TODAS las reglas de negocio del enunciado
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
from models.agenda_citas import Cita, BloqueAgenda, HistorialCita, EstadoCitaEnum, EstadoBloqueEnum
from models.identidades import PersonaAtendida, Profesional, UnidadAtencion
from services.auth_service import AuthService
from services.notification_service import notification_service
from schemas.base import ResponseSchema, PaginatedResponse
from dependencies import get_current_user, check_permission

router = APIRouter(prefix="/citas", tags=["Citas"])


class CitaService:
    """Servicio con lógica de negocio de citas"""
    
    @staticmethod
    def validar_bloque_disponible(db: Session, bloque_id: int, inicio: datetime, fin: datetime) -> BloqueAgenda:
        """
        REGLA DE NEGOCIO: Cita debe pertenecer a bloque abierto y no exceder capacidad
        """
        bloque = db.query(BloqueAgenda).filter(BloqueAgenda.id == bloque_id).first()
        
        if not bloque:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bloque de agenda no encontrado"
            )
        
        # Verificar estado
        if bloque.estado != EstadoBloqueEnum.ABIERTO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bloque no está abierto (estado: {bloque.estado.value})"
            )
        
        # Verificar que la cita está dentro del bloque
        if inicio < bloque.inicio or fin > bloque.fin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cita debe estar dentro del horario del bloque"
            )
        
        # Verificar capacidad
        citas_existentes = db.query(Cita).filter(
            Cita.bloque_agenda_id == bloque_id,
            Cita.estado.in_([EstadoCitaEnum.CONFIRMADA, EstadoCitaEnum.SOLICITADA]),
            Cita.inicio < fin,
            Cita.fin > inicio
        ).count()
        
        if citas_existentes >= bloque.capacidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bloque sin capacidad disponible ({citas_existentes}/{bloque.capacidad})"
            )
        
        return bloque
    
    @staticmethod
    def validar_transicion_estado(estado_actual: EstadoCitaEnum, estado_nuevo: EstadoCitaEnum):
        """
        REGLA DE NEGOCIO: Transiciones de estado válidas
        """
        transiciones_validas = {
            EstadoCitaEnum.SOLICITADA: [EstadoCitaEnum.CONFIRMADA, EstadoCitaEnum.CANCELADA],
            EstadoCitaEnum.CONFIRMADA: [EstadoCitaEnum.CUMPLIDA, EstadoCitaEnum.NO_ASISTIDA, EstadoCitaEnum.CANCELADA, EstadoCitaEnum.REPROGRAMADA],
            EstadoCitaEnum.CUMPLIDA: [],  # Estado final
            EstadoCitaEnum.CANCELADA: [],  # Estado final
            EstadoCitaEnum.NO_ASISTIDA: [],  # Estado final
            EstadoCitaEnum.REPROGRAMADA: []  # Estado final
        }
        
        if estado_nuevo not in transiciones_validas.get(estado_actual, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transición inválida de {estado_actual.value} a {estado_nuevo.value}"
            )
    
    @staticmethod
    def registrar_historial(
        db: Session,
        cita_id: int,
        estado_anterior: Optional[EstadoCitaEnum],
        estado_nuevo: EstadoCitaEnum,
        accion: str,
        motivo: Optional[str],
        usuario_id: Optional[int]
    ):
        """REGLA DE NEGOCIO: Registrar historial de cambios"""
        historial = HistorialCita(
            cita_id=cita_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            accion=accion,
            motivo_cambio=motivo,
            usuario_id=usuario_id
        )
        db.add(historial)


@router.post("/", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
def crear_cita(
    persona_id: int,
    profesional_id: int,
    unidad_id: int,
    bloque_agenda_id: int,
    inicio: datetime,
    fin: datetime,
    motivo: str,
    canal: str = "PRESENCIAL",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crea nueva cita
    REGLAS DE NEGOCIO:
    - Debe pertenecer a bloque abierto
    - No exceder capacidad
    - No solapar con agenda
    - Registrar historial
    """
    # Validar existencia de entidades
    persona = db.query(PersonaAtendida).filter(PersonaAtendida.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    
    profesional = db.query(Profesional).filter(Profesional.id == profesional_id).first()
    if not profesional:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    
    unidad = db.query(UnidadAtencion).filter(UnidadAtencion.id == unidad_id).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    
    # Validar bloque disponible
    bloque = CitaService.validar_bloque_disponible(db, bloque_agenda_id, inicio, fin)
    
    # Crear cita
    cita = Cita(
        persona_id=persona_id,
        profesional_id=profesional_id,
        unidad_id=unidad_id,
        bloque_agenda_id=bloque_agenda_id,
        inicio=inicio,
        fin=fin,
        motivo=motivo,
        canal=canal,
        estado=EstadoCitaEnum.SOLICITADA
    )
    db.add(cita)
    db.flush()
    
    # Registrar historial
    CitaService.registrar_historial(
        db=db,
        cita_id=cita.id,
        estado_anterior=None,
        estado_nuevo=EstadoCitaEnum.SOLICITADA,
        accion="crear",
        motivo=None,
        usuario_id=current_user.get("usuario_id")
    )
    
    db.commit()
    db.refresh(cita)
    
    return ResponseSchema(
        success=True,
        message="Cita creada exitosamente",
        data={"cita_id": cita.id}
    )


@router.patch("/{cita_id}/confirmar", response_model=ResponseSchema)
def confirmar_cita(
    cita_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Confirma una cita solicitada
    Envía notificación al paciente
    """
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    # Validar transición
    CitaService.validar_transicion_estado(cita.estado, EstadoCitaEnum.CONFIRMADA)
    
    estado_anterior = cita.estado
    cita.estado = EstadoCitaEnum.CONFIRMADA
    
    # Registrar historial
    CitaService.registrar_historial(
        db=db,
        cita_id=cita.id,
        estado_anterior=estado_anterior,
        estado_nuevo=EstadoCitaEnum.CONFIRMADA,
        accion="confirmar",
        motivo=None,
        usuario_id=current_user.get("usuario_id")
    )
    
    db.commit()
    
    # Enviar notificación
    try:
        notification_service.send_cita_confirmacion(
            db=db,
            email_paciente=cita.persona.correo,
            nombre_paciente=f"{cita.persona.nombres} {cita.persona.apellidos}",
            fecha_cita=cita.inicio,
            profesional=f"{cita.profesional.nombres} {cita.profesional.apellidos}",
            unidad=cita.unidad.nombre
        )
    except Exception as e:
        # No fallar si falla la notificación
        print(f"Error enviando notificación: {e}")
    
    return ResponseSchema(
        success=True,
        message="Cita confirmada exitosamente"
    )


@router.patch("/{cita_id}/cancelar", response_model=ResponseSchema)
def cancelar_cita(
    cita_id: int,
    motivo: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cancela una cita"""
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    CitaService.validar_transicion_estado(cita.estado, EstadoCitaEnum.CANCELADA)
    
    estado_anterior = cita.estado
    cita.estado = EstadoCitaEnum.CANCELADA
    
    CitaService.registrar_historial(
        db=db,
        cita_id=cita.id,
        estado_anterior=estado_anterior,
        estado_nuevo=EstadoCitaEnum.CANCELADA,
        accion="cancelar",
        motivo=motivo,
        usuario_id=current_user.get("usuario_id")
    )
    
    db.commit()
    
    return ResponseSchema(success=True, message="Cita cancelada")


@router.get("/", response_model=PaginatedResponse)
def listar_citas(
    persona_id: Optional[int] = None,
    profesional_id: Optional[int] = None,
    estado: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista citas con filtros y paginación"""
    query = db.query(Cita)
    
    if persona_id:
        query = query.filter(Cita.persona_id == persona_id)
    if profesional_id:
        query = query.filter(Cita.profesional_id == profesional_id)
    if estado:
        query = query.filter(Cita.estado == estado)
    if fecha_desde:
        query = query.filter(Cita.inicio >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Cita.inicio <= fecha_hasta)
    
    total = query.count()
    citas = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        success=True,
        data=[c.to_dict() for c in citas],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )