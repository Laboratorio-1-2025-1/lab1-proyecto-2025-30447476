# 🏥 API de Servicios Médicos - Laboratorio I 2025-2

Sistema completo de gestión de servicios médicos desarrollado con FastAPI, SQLAlchemy y MySQL.

---

## 👥 Participante

**👤 Mercedes Cordero**
- **Cédula:** 30447476
- **Correo:** 1001.30447476.ucla@gmail.com
- **Rol:** Desarrolladora Principal (Fullstack Backend)

### Responsabilidades:
- Diseño y arquitectura del sistema completo
- Implementación de todos los módulos (2.1 a 2.9)
- Configuración de base de datos MySQL
- Implementación de autenticación JWT y RBAC
- Integración con SendGrid para notificaciones
- Sistema de auditoría completo
- Testing y documentación

---

## 📋 Descripción del Proyecto

API RESTful completa para gestión de servicios médicos que implementa:

### ✅ Módulos Implementados

#### 🔹 Módulo 2.1: Identidades y Vinculación Asistencial
- **PersonasAtendidas** (Pacientes): Gestión completa de pacientes con historial médico
- **Profesionales**: Médicos, enfermeras, terapeutas con registro profesional
- **UnidadesAtencion**: Sedes, consultorios, servicios médicos

#### 🔹 Módulo 2.2: Disponibilidad y Citas
- **BloqueAgenda**: Gestión de disponibilidad de profesionales
- **Citas**: Agendamiento con validación de capacidad y solapamiento
- **HistorialCita**: Trazabilidad completa de cambios de estado

#### 🔹 Módulo 2.3: Registro Clínico
- **EpisodiosAtencion**: Contenedor de procesos asistenciales
- **NotasClinicas**: Registros SOAP con versionado
- **Diagnosticos**: Códigos CIE-10 estandarizados
- **Consentimientos**: Aceptación informada de procedimientos

#### 🔹 Módulo 2.4: Órdenes y Prestaciones
- **Ordenes**: Solicitudes de exámenes, imágenes, procedimientos
- **OrdenItems**: Detalle de cada orden
- **Prescripciones**: Recetas médicas
- **Resultados**: Actas con versionado

#### 🔹 Módulo 2.5: Cobertura y Autorizaciones
- **Aseguradoras**: EPS, seguros, medicina prepagada
- **PlanesCobertura**: Planes de salud
- **Afiliaciones**: Vinculación paciente-plan
- **Autorizaciones**: Aprobaciones de prestaciones

#### 🔹 Módulo 2.6: Catálogo Clínico y Arancel
- **Prestaciones**: Catálogo de servicios médicos
- **Arancel**: Tarifas por plan y prestación

#### 🔹 Módulo 2.7: Facturación y Cobros
- **Facturas**: Comprobantes con validación de totales
- **FacturaItems**: Detalle línea por línea
- **Pagos**: Registro de pagos con múltiples medios
- **NotasAjuste**: Notas de crédito/débito

#### 🔹 Módulo 2.8: Notificaciones
- **Notificaciones**: Sistema multi-canal (Email/SMS/WhatsApp)
- **Integración SendGrid**: Envío de emails transaccionales

#### 🔹 Módulo 2.9: Auditoría y Trazabilidad
- **Usuarios**: Autenticación y autorización
- **Roles y Permisos**: RBAC completo
- **BitacoraAccesos**: Registro de todas las acciones

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python** 3.10+
- **FastAPI** 0.109.0 - Framework web moderno y rápido
- **SQLAlchemy** 2.0.25 - ORM para Python
- **Pydantic** 2.5.3 - Validación de datos
- **Uvicorn** - Servidor ASGI

### Base de Datos
- **MySQL** 8.0+ con InnoDB
- **PyMySQL** - Driver de conexión
- **Alembic** - Migraciones de BD

### Seguridad
- **JWT (python-jose)** - Tokens de autenticación
- **Passlib + Bcrypt** - Hash de contraseñas
- **RBAC** - Control de acceso basado en roles

### Servicios Externos
- **SendGrid** - Envío de emails

### Calidad de Código
- **Black** - Formateo automático
- **Flake8** - Linting
- **Pytest** - Testing

---

## 📂 Estructura del Proyecto

```
lab1-proyecto-2025-30447476/
│
├── config.py                    # Configuración central
├── database.py                  # Configuración de BD
├── main.py                      # Punto de entrada FastAPI
├── requirements.txt             # Dependencias
├── .env                         # Variables de entorno
├── .env.example                 # Ejemplo de configuración
│
├── models/                      # Modelos SQLAlchemy
│   ├── __init__.py
│   ├── base.py                 # Modelo base con auditoría
│   ├── identidades.py          # Personas, Profesionales, Unidades
│   ├── agenda_citas.py         # Agenda y Citas
│   ├── registro_clinico.py     # Episodios, Notas, Diagnósticos
│   ├── ordenes.py              # Órdenes, Prescripciones, Resultados
│   ├── aseguradoras.py         # Aseguradoras, Planes, Autorizaciones
│   ├── catalogo.py             # Prestaciones, Arancel
│   ├── facturacion.py          # Facturas, Pagos
│   ├── notificaciones.py       # Notificaciones
│   └── auditoria.py            # Usuarios, Roles, BitacoraAccesos
│
├── schemas/                     # Schemas Pydantic
│   ├── __init__.py
│   ├── base.py                 # Schemas base
│   ├── identidades.py          # DTOs de identidades
│   ├── citas.py                # DTOs de citas
│   └── ... (uno por módulo)
│
├── routers/                     # Endpoints FastAPI
│   ├── __init__.py
│   ├── auth.py                 # Login, registro
│   ├── personas.py             # CRUD personas
│   ├── profesionales.py        # CRUD profesionales
│   ├── citas.py                # Gestión de citas
│   ├── facturas.py             # Facturación
│   └── ... (uno por recurso)
│
├── services/                    # Lógica de negocio
│   ├── __init__.py
│   ├── auth_service.py         # Autenticación JWT
│   ├── notification_service.py # Notificaciones SendGrid
│   ├── cita_service.py         # Reglas de negocio citas
│   └── ... (servicios adicionales)
│
├── middleware/                  # Middleware personalizado
│   ├── __init__.py
│   └── audit.py                # Middleware de auditoría
│
├── dependencies.py              # Dependencias compartidas
├── exceptions.py                # Excepciones personalizadas
│
├── scripts/                     # Scripts de utilidad
│   ├── seed_data.py            # Datos iniciales
│   └── create_migration.py     # Crear migración Alembic
│
└── tests/                       # Pruebas automatizadas
    ├── __init__.py
    ├── test_auth.py
    ├── test_citas.py
    └── test_facturacion.py
```

---

## 🚀 Instalación y Ejecución

### 1️⃣ Prerequisitos

- Python 3.10 o superior
- MySQL 8.0+
- Git

### 2️⃣ Clonar el repositorio

```bash
git clone https://github.com/Mercedita09/lab1-proyecto-2025-30447476.git
cd lab1-proyecto-2025-30447476
```

### 3️⃣ Crear entorno virtual

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows CMD
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1
```

### 4️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5️⃣ Configurar variables de entorno

Copiar `.env.example` a `.env` y configurar:

```bash
cp .env.example .env
```

Editar `.env`:

```env
# Base de datos
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medical_services_db
DB_USER=root
DB_PASSWORD=tu_password

# JWT
SECRET_KEY=genera_una_clave_secreta_segura_aqui

# SendGrid (opcional)
SENDGRID_API_KEY=tu_api_key_aqui
```

### 6️⃣ Crear base de datos

```sql
CREATE DATABASE medical_services_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 7️⃣ Inicializar datos

```bash
python scripts/seed_data.py
```

Esto creará:
- Roles y permisos
- Usuarios iniciales
- Catálogo de prestaciones
- Datos de ejemplo

### 8️⃣ Ejecutar la aplicación

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 Documentación de la API

Una vez ejecutada la aplicación, acceder a:

- **Swagger UI:** http://localhost:8000/api-docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 🔐 Autenticación

### Login

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin123!"
}
```

Respuesta:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Usar token

Incluir en headers de peticiones:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 👤 Usuarios Iniciales

| Username | Password | Rol | Permisos |
|----------|----------|-----|----------|
| admin | Admin123! | Administrador | Acceso completo |
| medico1 | Medico123! | Profesional | Clínica, citas |
| cajero1 | Cajero123! | Cajero | Facturación |
| auditor1 | Auditor123! | Auditor | Solo lectura |

---

## 🔒 Reglas de Negocio Implementadas

### Citas
✅ Debe pertenecer a bloque abierto  
✅ No exceder capacidad del bloque  
✅ No solapar con otras citas  
✅ Transiciones de estado válidas  
✅ Registro de historial de cambios

### Episodios
✅ Solo cierre si no hay órdenes en curso  
✅ Diagnóstico principal único por episodio

### Facturación
✅ Solo emitida cuando items tienen precio vigente  
✅ Total = suma(items)  
✅ Pagos no exceden saldo pendiente

### Autorizaciones
✅ Requerida para prestaciones marcadas

### Notas Clínicas
✅ No sobrescribir contenido, crear nueva versión  
✅ Versionado completo

### Seguridad
✅ Acceso restringido por rol  
✅ Auditoría de acciones clínicas  
✅ Bloqueo tras 5 intentos fallidos

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Test específico
pytest tests/test_citas.py -v
```

---

## 📊 Base de Datos

### Diagrama ER

El proyecto incluye 25+ tablas relacionadas:

- **Identidades:** personas_atendidas, profesionales, unidades_atencion
- **Agenda:** bloques_agenda, citas, historial_citas
- **Clínica:** episodios_atencion, notas_clinicas, diagnosticos, consentimientos
- **Órdenes:** ordenes, orden_items, prescripciones, resultados
- **Cobertura:** aseguradoras, planes_cobertura, afiliaciones, autorizaciones
- **Catálogo:** prestaciones, arancel
- **Facturación:** facturas, factura_items, pagos, notas_ajuste
- **Notificaciones:** notificaciones
- **Seguridad:** usuarios, roles, permisos, usuario_rol, rol_permiso, bitacora_accesos

---

## 🐳 Docker (Opcional)

### Dockerfile

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: medical_services_db
    ports:
      - "3306:3306"
```

---

## 📝 Notas Técnicas

### Arquitectura en Capas

1. **Routers** - Endpoints HTTP
2. **Services** - Lógica de negocio
3. **Models** - ORM SQLAlchemy
4. **Schemas** - Validación Pydantic
5. **Database** - Sesiones y configuración

### Principios Aplicados

- **DRY** (Don't Repeat Yourself)
- **SOLID**
- **Separation of Concerns**
- **Dependency Injection**

---

## 🔧 Troubleshooting

### Error de conexión a MySQL

```bash
# Verificar que MySQL esté corriendo
sudo systemctl status mysql

# Verificar credenciales en .env
```

### Error de permisos

```bash
# Asegurar que el usuario tenga permisos
GRANT ALL PRIVILEGES ON medical_services_db.* TO 'tu_usuario'@'localhost';
FLUSH PRIVILEGES;
```

---

## 📄 Licencia

Proyecto académico - Laboratorio I 2025-2

---

## 📞 Contacto

**Mercedes Cordero**  
📧 1001.30447476.ucla@gmail.com  
🎓 Cédula: 30447476