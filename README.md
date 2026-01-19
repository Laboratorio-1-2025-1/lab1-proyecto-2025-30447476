🧬 API de Servicios Médicos
Proyecto desarrollado en Python para la gestión de servicios médicos, siguiendo una arquitectura modular que separa modelos, esquemas, rutas, lógica interna y pruebas automatizadas.Código
lab1-proyecto-2025-30447476


👥 Participante:
👤 Mercedes Cordero
Cédula: 30447476

Correo: 1001.30447476.ucla@gmail.com

Rol: Desarrolladora principal (Backend)

Responsabilidades:

Configuración inicial del proyecto y estructura de carpetas.

Implementación de módulos internos (operaciones.py, modelos, esquemas y rutas).

Configuración de la base de datos (database.py, conexion.py, .env).

Organización del repositorio según las reglas del laboratorio.

Preparación de documentación y soporte para pruebas.

📌 Descripción general
Este proyecto implementa una API para gestionar información relacionada con servicios médicos.
La arquitectura está organizada en módulos independientes que facilitan:

Mantenimiento

Escalabilidad

Reutilización de componentes

Pruebas automatizadas

El repositorio incluye:

Módulos para modelos, esquemas y rutas

Archivos de conexión y configuración de base de datos

Archivo principal para ejecutar la API

Directorio de pruebas

Variables de entorno mediante .env

📂 Estructura del proyecto
Código
lab1-proyecto-2025-30447476/
│── models/           # Modelos de datos
│── routers/          # Rutas / Endpoints
│── schemas/          # Validación y serialización
│── tests/            # Pruebas automatizadas
│── __pycache__/      # Archivos generados por Python
│── .env              # Variables de entorno
│── conexion.py       # Configuración de conexión
│── database.py       # Manejo de base de datos
│── main.py           # Punto de entrada de la API
│── operaciones.py    # Lógica adicional
🛠️ Requisitos
Python 3.10 o superior

pip

(Opcional) Entorno virtual con venv

🚀 Instalación y ejecución
1️⃣ Clonar el repositorio
bash
git clone https://github.com/Laboratorio-1-2025-1/lab1-proyecto-2025-30447476.git
cd lab1-proyecto-2025-30447476
2️⃣ Crear entorno virtual (opcional)
bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
3️⃣ Instalar dependencias
Si ya existe un requirements.txt:

bash
pip install -r requirements.txt
Si aún no existe, puedes generarlo con:

bash
pip freeze > requirements.txt
4️⃣ Configurar variables de entorno
Editar el archivo .env:

Código
DB_HOST=...
DB_USER=...
DB_PASSWORD=...
DB_NAME=...
5️⃣ Ejecutar la API
bash
python main.py
🧪 Ejecución de pruebas
Si el proyecto ya tiene pruebas configuradas:

bash
pytest
📘 Estado del proyecto
El proyecto se encuentra en desarrollo.
La estructura base ya está creada y lista para expandirse con nuevos modelos, rutas y funcionalidades.

🎓 Proyecto académico
Este proyecto forma parte del curso Laboratorio 1 – 2025-1.
