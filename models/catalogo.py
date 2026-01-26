"""
Módulo 2.6: Catálogo clínico y arancel
- Prestacion: catálogo de servicios
- Arancel: tarifas por plan
"""
from sqlalchemy import Column, String, Date, Integer, ForeignKey, Enum, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class GrupoPrestacionEnum(str, enum.Enum):
    """Grupos de prestaciones"""
    CONSULTA = "CONSULTA"
    PROCEDIMIENTO_QUIRURGICO = "PROCEDIMIENTO_QUIRURGICO"
    PROCEDIMIENTO_NO_QUIRURGICO = "PROCEDIMIENTO_NO_QUIRURGICO"
    LABORATORIO = "LABORATORIO"
    IMAGENOLOGIA = "IMAGENOLOGIA"
    TERAPIA = "TERAPIA"
    HOSPITALIZACION = "HOSPITALIZACION"
    URGENCIAS = "URGENCIAS"


class Prestacion(BaseModel):
    """
    Modelo 2.6.1: Prestaciones (Catálogo de Servicios)
    Servicios médicos disponibles
    """
    __tablename__ = "prestaciones"
    
    # Código único
    codigo = Column(String(50), primary_key=True, index=True)
    
    # Datos de la prestación
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    grupo = Column(Enum(GrupoPrestacionEnum), nullable=False, index=True)
    
    # Requisitos
    requisitos = Column(Text, nullable=True, comment="Requisitos previos para realizar la prestación")
    requiere_autorizacion = Column(Boolean, default=False, nullable=False)
    
    # Tiempo estimado (en minutos)
    tiempo_estimado = Column(Integer, nullable=True, comment="Duración estimada en minutos")
    
    # Estado
    vigente = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    arancel = relationship("Arancel", back_populates="prestacion", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Prestacion(codigo={self.codigo}, nombre={self.nombre})>"


class Arancel(BaseModel):
    """
    Modelo 2.6.2: Arancel (Tarifas)
    Precios de prestaciones por plan o general
    """
    __tablename__ = "arancel"
    
    # Relaciones
    prestacion_codigo = Column(String(50), ForeignKey("prestaciones.codigo", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("planes_cobertura.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Valores económicos
    valor_base = Column(Numeric(12, 2), nullable=False)
    impuestos = Column(Numeric(12, 2), default=0, nullable=False)
    
    # Vigencia
    vigente_desde = Column(Date, nullable=False)
    vigente_hasta = Column(Date, nullable=True)
    
    # Observaciones
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    prestacion = relationship("Prestacion", back_populates="arancel")
    plan = relationship("PlanCobertura", back_populates="arancel")
    
    def __repr__(self):
        plan_info = f"plan_id={self.plan_id}" if self.plan_id else "general"
        return f"<Arancel(id={self.id}, prestacion={self.prestacion_codigo}, {plan_info})>"