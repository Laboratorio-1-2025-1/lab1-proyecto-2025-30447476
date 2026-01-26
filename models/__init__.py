"""
Modelos consolidados del sistema médico
Importa todos los modelos para facilitar su uso
"""

# Base
from models.base import BaseModel

# Módulo 2.1: Identidades
from models.identidades import (
    PersonaAtendida,
    Profesional,
    UnidadAtencion,
    TipoDocumentoEnum,
    SexoEnum,
    EstadoGeneralEnum,
    TipoUnidadEnum
)

# Módulo 2.2: Agenda y Citas
from models.agenda_citas import (
    BloqueAgenda,
    Cita,
    HistorialCita,
    EstadoBloqueEnum,
    EstadoCitaEnum,
    CanalCitaEnum
)

# Módulo 2.3: Registro Clínico
from models.registro_clinico import (
    EpisodioAtencion,
    NotaClinica,
    Diagnostico,
    Consentimiento,
    TipoEpisodioEnum,
    EstadoEpisodioEnum,
    TipoDiagnosticoEnum,
    MetodoConsentimientoEnum
)

# Módulo 2.4: Órdenes
from models.ordenes import (
    Orden,
    OrdenItem,
    Prescripcion,
    Resultado,
    TipoOrdenEnum,
    PrioridadOrdenEnum,
    EstadoOrdenEnum
)

# Módulo 2.5: Aseguradoras
from models.aseguradoras import (
    Aseguradora,
    PlanCobertura,
    Afiliacion,
    Autorizacion,
    EstadoAseguradoraEnum,
    EstadoAutorizacionEnum
)

# Módulo 2.6: Catálogo
from models.catalogo import (
    Prestacion,
    Arancel,
    GrupoPrestacionEnum
)

# Módulo 2.7: Facturación
from models.facturacion import (
    Factura,
    FacturaItem,
    Pago,
    NotaAjuste,
    EstadoFacturaEnum,
    MedioPagoEnum,
    EstadoPagoEnum,
    TipoNotaEnum
)

# Módulo 2.8: Notificaciones
from models.notificaciones import (
    Notificacion,
    TipoNotificacionEnum,
    EstadoNotificacionEnum,
    PlantillaNotificacionEnum
)

# Módulo 2.9: Auditoría
from models.auditoria import (
    Usuario,
    Rol,
    Permiso,
    BitacoraAcceso,
    TipoAccionEnum,
    usuario_rol,
    rol_permiso
)

__all__ = [
    # Base
    "BaseModel",
    
    # Identidades
    "PersonaAtendida", "Profesional", "UnidadAtencion",
    "TipoDocumentoEnum", "SexoEnum", "EstadoGeneralEnum", "TipoUnidadEnum",
    
    # Agenda
    "BloqueAgenda", "Cita", "HistorialCita",
    "EstadoBloqueEnum", "EstadoCitaEnum", "CanalCitaEnum",
    
    # Registro Clínico
    "EpisodioAtencion", "NotaClinica", "Diagnostico", "Consentimiento",
    "TipoEpisodioEnum", "EstadoEpisodioEnum", "TipoDiagnosticoEnum", "MetodoConsentimientoEnum",
    
    # Órdenes
    "Orden", "OrdenItem", "Prescripcion", "Resultado",
    "TipoOrdenEnum", "PrioridadOrdenEnum", "EstadoOrdenEnum",
    
    # Aseguradoras
    "Aseguradora", "PlanCobertura", "Afiliacion", "Autorizacion",
    "EstadoAseguradoraEnum", "EstadoAutorizacionEnum",
    
    # Catálogo
    "Prestacion", "Arancel", "GrupoPrestacionEnum",
    
    # Facturación
    "Factura", "FacturaItem", "Pago", "NotaAjuste",
    "EstadoFacturaEnum", "MedioPagoEnum", "EstadoPagoEnum", "TipoNotaEnum",
    
    # Notificaciones
    "Notificacion",
    "TipoNotificacionEnum", "EstadoNotificacionEnum", "PlantillaNotificacionEnum",
    
    # Auditoría
    "Usuario", "Rol", "Permiso", "BitacoraAcceso",
    "TipoAccionEnum", "usuario_rol", "rol_permiso"
]