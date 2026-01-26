"""
Modelo base con campos de auditoría comunes
Todos los modelos heredan de esta clase
"""
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base


class BaseModel(Base):
    """Clase base abstracta con campos de auditoría"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }