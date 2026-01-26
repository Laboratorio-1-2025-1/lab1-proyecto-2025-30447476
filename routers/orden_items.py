"""Router: Items de Órdenes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.ordenes import OrdenItem
from schemas.base import ResponseSchema

router_orden_items = APIRouter(prefix="/orden-items", tags=["Items de Órdenes"])

@router_orden_items.post("/")
def crear_item_orden(
    orden_id: int,
    prestacion_codigo: str,
    descripcion: str,
    indicaciones: str = None,
    cantidad: int = 1,
    db: Session = Depends(get_db)
):
    item = OrdenItem(
        orden_id=orden_id,
        prestacion_codigo=prestacion_codigo,
        descripcion=descripcion,
        indicaciones=indicaciones,
        cantidad=cantidad
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return ResponseSchema(success=True, message="Item agregado", data=item.to_dict())

@router_orden_items.get("/orden/{orden_id}")
def listar_items_orden(orden_id: int, db: Session = Depends(get_db)):
    items = db.query(OrdenItem).filter(OrdenItem.orden_id == orden_id).all()
    return ResponseSchema(success=True, data=[i.to_dict() for i in items])