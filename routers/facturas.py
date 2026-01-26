"""Router: Facturas - Módulo 2.7"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from database import get_db
from models.facturacion import Factura, EstadoFacturaEnum
from models.catalogo import Arancel
from schemas.base import ResponseSchema

router_facturas = APIRouter(prefix="/facturas", tags=["Facturas"])

@router_facturas.post("/", status_code=status.HTTP_201_CREATED)
def crear_factura(
    numero: str,
    persona_id: Optional[int] = None,
    aseguradora_id: Optional[int] = None,
    moneda: str = "USD",
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    REGLA DE NEGOCIO: Factura a persona O aseguradora
    """
    if not persona_id and not aseguradora_id:
        raise HTTPException(
            status_code=400,
            detail="Debe especificar persona_id o aseguradora_id"
        )
    
    if persona_id and aseguradora_id:
        raise HTTPException(
            status_code=400,
            detail="Solo puede facturar a persona O aseguradora, no ambos"
        )
    
    # Validar número único
    existe = db.query(Factura).filter(Factura.numero == numero).first()
    if existe:
        raise HTTPException(status_code=400, detail="Número de factura ya existe")
    
    factura = Factura(
        numero=numero,
        fecha_emision=date.today(),
        persona_id=persona_id,
        aseguradora_id=aseguradora_id,
        moneda=moneda,
        subtotal=0,
        impuestos_total=0,
        total=0,
        estado=EstadoFacturaEnum.PENDIENTE,
        observaciones=observaciones
    )
    db.add(factura)
    db.commit()
    db.refresh(factura)
    return ResponseSchema(success=True, message="Factura creada", data=factura.to_dict())

@router_facturas.post("/{factura_id}/items")
def agregar_item_factura(
    factura_id: int,
    prestacion_codigo: str,
    descripcion: str,
    cantidad: int = 1,
    fecha_prestacion: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    REGLA DE NEGOCIO: Solo emitida con precios vigentes
    """
    from models.facturacion import FacturaItem
    
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Buscar precio vigente
    hoy = date.today()
    arancel = db.query(Arancel).filter(
        Arancel.prestacion_codigo == prestacion_codigo,
        Arancel.vigente_desde <= hoy
    ).filter(
        (Arancel.vigente_hasta == None) | (Arancel.vigente_hasta >= hoy)
    ).first()
    
    if not arancel:
        raise HTTPException(
            status_code=400,
            detail=f"No hay precio vigente para {prestacion_codigo}"
        )
    
    valor_unitario = float(arancel.valor_base)
    impuestos = float(arancel.impuestos) * cantidad
    total = (valor_unitario * cantidad) + impuestos
    
    item = FacturaItem(
        factura_id=factura_id,
        prestacion_codigo=prestacion_codigo,
        descripcion=descripcion,
        cantidad=cantidad,
        valor_unitario=valor_unitario,
        impuestos=impuestos,
        total=total,
        fecha_prestacion=fecha_prestacion
    )
    db.add(item)
    
    # Actualizar totales de factura
    factura.subtotal = float(factura.subtotal) + (valor_unitario * cantidad)
    factura.impuestos_total = float(factura.impuestos_total) + impuestos
    factura.total = float(factura.total) + total
    
    db.commit()
    db.refresh(item)
    return ResponseSchema(success=True, message="Item agregado", data=item.to_dict())

@router_facturas.patch("/{factura_id}/emitir")
def emitir_factura(factura_id: int, db: Session = Depends(get_db)):
    """
    REGLA DE NEGOCIO: Solo emitida cuando items tienen precio vigente
    REGLA DE NEGOCIO: Total = suma(items)
    """
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    if len(factura.items) == 0:
        raise HTTPException(status_code=400, detail="Factura sin items")
    
    # Verificar que total coincida
    total_calculado = sum(float(item.total) for item in factura.items)
    if abs(float(factura.total) - total_calculado) > 0.01:
        raise HTTPException(
            status_code=400,
            detail="Total de factura no coincide con suma de items"
        )
    
    factura.estado = EstadoFacturaEnum.EMITIDA
    db.commit()
    return ResponseSchema(success=True, message="Factura emitida")

@router_facturas.get("/")
def listar_facturas(
    persona_id: Optional[int] = None,
    aseguradora_id: Optional[int] = None,
    estado: Optional[EstadoFacturaEnum] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Factura)
    if persona_id:
        query = query.filter(Factura.persona_id == persona_id)
    if aseguradora_id:
        query = query.filter(Factura.aseguradora_id == aseguradora_id)
    if estado:
        query = query.filter(Factura.estado == estado)
    
    facturas = query.all()
    return ResponseSchema(success=True, data=[f.to_dict() for f in facturas])

@router_facturas.get("/{factura_id}")
def obtener_factura(factura_id: int, db: Session = Depends(get_db)):
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    data = factura.to_dict()
    data['items'] = [i.to_dict() for i in factura.items]
    data['pagos'] = [p.to_dict() for p in factura.pagos]
    data['saldo_pendiente'] = float(factura.total) - sum(float(p.monto) for p in factura.pagos if p.estado == "APROBADO")
    return ResponseSchema(success=True, data=data)


### ARCHIVO: routers/pagos.py
"""Router: Pagos"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from database import get_db
from models.facturacion import Pago, Factura, MedioPagoEnum, EstadoPagoEnum, EstadoFacturaEnum
from schemas.base import ResponseSchema

router_pagos = APIRouter(prefix="/pagos", tags=["Pagos"])

@router_pagos.post("/")
def registrar_pago(
    factura_id: int,
    monto: float,
    medio: MedioPagoEnum,
    referencia: Optional[str] = None,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    REGLA DE NEGOCIO: Pagos no exceden saldo pendiente
    """
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Calcular saldo pendiente
    total_pagado = sum(
        float(p.monto) for p in factura.pagos 
        if p.estado == EstadoPagoEnum.APROBADO
    )
    saldo_pendiente = float(factura.total) - total_pagado
    
    if monto > saldo_pendiente:
        raise HTTPException(
            status_code=400,
            detail=f"Monto excede saldo pendiente. Saldo: {saldo_pendiente}"
        )
    
    pago = Pago(
        factura_id=factura_id,
        fecha=date.today(),
        monto=monto,
        medio=medio,
        referencia=referencia,
        estado=EstadoPagoEnum.APROBADO,
        observaciones=observaciones
    )
    db.add(pago)
    
    # Actualizar estado de factura
    nuevo_saldo = saldo_pendiente - monto
    if nuevo_saldo <= 0.01:  # Considerar pagada
        factura.estado = EstadoFacturaEnum.PAGADA
    
    db.commit()
    db.refresh(pago)
    return ResponseSchema(success=True, message="Pago registrado", data=pago.to_dict())

@router_pagos.get("/factura/{factura_id}")
def listar_pagos_factura(factura_id: int, db: Session = Depends(get_db)):
    pagos = db.query(Pago).filter(Pago.factura_id == factura_id).all()
    return ResponseSchema(success=True, data=[p.to_dict() for p in pagos])


### ARCHIVO: routers/notificaciones_router.py
"""Router: Notificaciones - Módulo 2.8"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.notificaciones import Notificacion, TipoNotificacionEnum, PlantillaNotificacionEnum
from services.notification_service import notification_service
from schemas.base import ResponseSchema

router_notificaciones = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

@router_notificaciones.post("/enviar")
def enviar_notificacion(
    tipo: TipoNotificacionEnum,
    destinatario: str,
    asunto: str,
    mensaje: str,
    plantilla: Optional[PlantillaNotificacionEnum] = None,
    payload: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Envía notificación por el canal especificado"""
    if tipo == TipoNotificacionEnum.EMAIL:
        notif = notification_service.send_email(
            db=db,
            destinatario=destinatario,
            asunto=asunto,
            mensaje=mensaje,
            plantilla=plantilla,
            payload=payload
        )
    else:
        # SMS, WhatsApp simulado
        notif = Notificacion(
            tipo=tipo,
            destinatario=destinatario,
            asunto=asunto,
            mensaje=mensaje,
            plantilla=plantilla,
            payload=payload,
            estado="ENVIADO"
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
    
    return ResponseSchema(success=True, message="Notificación enviada", data=notif.to_dict())

@router_notificaciones.get("/")
def listar_notificaciones(
    tipo: Optional[TipoNotificacionEnum] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Notificacion)
    if tipo:
        query = query.filter(Notificacion.tipo == tipo)
    if estado:
        query = query.filter(Notificacion.estado == estado)
    
    notificaciones = query.order_by(Notificacion.created_at.desc()).limit(100).all()
    return ResponseSchema(success=True, data=[n.to_dict() for n in notificaciones])

@router_notificaciones.post("/reintentar-fallidas")
def reintentar_fallidas(db: Session = Depends(get_db)):
    """Reintenta notificaciones fallidas"""
    notification_service.retry_failed_notifications(db, max_retries=3)
    return ResponseSchema(success=True, message="Reintentos procesados")
