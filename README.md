# 🚀 Salesmen Tracker

> Sistema completo de seguimiento de vendedores en ruta con geolocalización GPS en tiempo real

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.3-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.3-4169E1)](https://postgis.net/)

---

## 📖 Descripción

**Salesmen Tracker** es una aplicación web moderna diseñada para **Alugandia** (empresa de distribución de perfiles de aluminio en Gandia, Valencia) que permite gestionar y hacer seguimiento en tiempo real de los vendedores en ruta.

El sistema resuelve problemas críticos de gestión comercial:
- ✅ Seguimiento de visitas a clientes
- ✅ Validación de ubicación en check-in/check-out
- ✅ Planificación y asignación de rutas
- ✅ Cálculo automático de distancias con PostGIS
- ✅ Dashboard de métricas en tiempo real
- ✅ Gestión de oportunidades de negocio

---

## ✨ Características Principales

### 🗺️ Geolocalización de visitas
- **Check-in/Check-out con GPS**: Captura automática de ubicación precisa
- **Validación de distancia**: Calcula distancia entre ubicación del vendedor y cliente
- **Consultas geoespaciales**: Encuentra clientes cercanos usando PostGIS
- **Historial de ubicaciones**: Registro completo de cada visita

### 📊 Dashboard Interactivo
- **Métricas en tiempo real**: Vendedores activos, visitas del día, rutas pendientes
- **Estadísticas por vendedor**: Visitas completadas, distancia promedio, puntualidad
- **Visualización de datos**: Gráficos y tarjetas informativas

### 📍 Gestión de Rutas
- **Planificación de visitas**: Asignar rutas a vendedores por fecha y hora
- **Estados de ruta**: Pendiente → En Progreso → Completada
- **Optimización**: Identificar clientes cercanos para planificar rutas eficientes

### 👥 Gestión de Clientes
- **Base de datos geolocalizada**: Cada cliente tiene coordenadas GPS precisas
- **Búsqueda por proximidad**: Encontrar clientes en un radio determinado
- **Segmentación**: Clasificación por tipo, estado, ubicación

### 💼 Oportunidades de Negocio
- **Pipeline de ventas**: Seguimiento de oportunidades abiertas
- **Valor estimado**: Proyección de ingresos por oportunidad
- **Estados**: Abierta → En Negociación → Ganada/Perdida

---

## 🏗️ Arquitectura Técnica

### Stack Tecnológico

**Frontend:**
- **Vue.js 3** (Composition API) - Framework reactivo
- **Vite** - Build tool ultrarrápido
- **Tailwind CSS** - Diseño responsive moderno
- **Geolocation API** - Acceso a GPS del navegador

**Backend:**
- **Python 3.11** - Lenguaje base
- **FastAPI** - Framework web asíncrono de alto rendimiento
- **SQLAlchemy** - ORM para gestión de base de datos
- **GeoAlchemy2** - Extensión para tipos geoespaciales
- **Pydantic** - Validación de datos y serialización

**Base de Datos:**
- **PostgreSQL 15** - Base de datos relacional
- **PostGIS 3.3** - Extensión geoespacial para consultas geográficas
- **Índices GIST** - Optimización de búsquedas espaciales

**Infraestructura:**
- **Docker** - Contenedorización
- **Docker Compose** - Orquestación de servicios
- **Nginx** (producción) - Reverse proxy y balanceador

---

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker 20.10+
- Docker Compose 2.0+

### Instalación (5 minutos)

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/salesmen-tracker.git
cd salesmen-tracker

# 2. Levantar servicios
docker-compose up -d

# 3. Insertar datos de prueba
docker exec -it salesmen_tracker_backend python seed_data.py
```

### Acceso a la Aplicación

- 🌐 **Frontend**: http://localhost:5173
- 🔌 **API Docs**: http://localhost:8000/docs
- 🗄️ **Base de Datos**: `localhost:5433` (usuario: `postgres`, contraseña: `postgres`)

---

## 📁 Estructura del Proyecto

```
salesmen-tracker/
├── backend/                    # API FastAPI
│   ├── main.py                # Aplicación principal y modelos
│   ├── seed_data.py           # Datos de prueba (Alugandia)
│   ├── requirements.txt       # Dependencias Python
│   ├── Dockerfile             # Imagen Docker backend
│   └── .env                   # Variables de entorno
│
├── frontend/                  # Aplicación Vue.js
│   ├── src/
│   │   ├── App.vue           # Componente principal
│   │   ├── main.js           # Entry point
│   │   └── assets/           # Estilos globales
│   ├── package.json          # Dependencias Node
│   ├── vite.config.js        # Configuración Vite
│   └── Dockerfile            # Imagen Docker frontend
│
├── docker-compose.yml        # Orquestación de servicios
├── init.sql                  # Inicialización de PostGIS
└── README.md                 # Este archivo
```

---

## 🗺️ Modelo de Datos

### Entidades Principales

**Sellers (Vendedores)**
- Información del vendedor (nombre, email, teléfono)
- Estado activo/inactivo
- Relaciones: rutas, visitas, oportunidades

**Clients (Clientes)**
- Datos del cliente
- **Ubicación geográfica (PostGIS POINT)**
- Estado: active, inactive, pending

**Routes (Rutas)**
- Asignación vendedor-cliente
- Fecha y hora programada
- Estado: pending, in_progress, completed, cancelled

**Visits (Visitas)**
- Check-in/check-out con timestamp
- **Ubicaciones GPS de entrada y salida**
- **Distancia calculada al cliente** (metros)
- Notas de la visita

**Opportunities (Oportunidades)**
- Título y descripción
- Valor estimado
- Estado del pipeline

### Relaciones

```
Seller ─┬─► Routes ──► Client
        └─► Visits ──► Client
        └─► Opportunities ──► Client
```

---

## 🔧 Desarrollo

### Configuración Local (Sin Docker)

**Backend:**
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
createdb salesmen_tracker
psql -d salesmen_tracker -c "CREATE EXTENSION postgis;"

# Configurar variables
cp .env.example .env

# Ejecutar
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables
cp .env.example .env

# Ejecutar
npm run dev
```

### Variables de Entorno

**Backend (`backend/.env`):**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/salesmen_tracker
PORT=8000
CORS_ORIGINS=http://localhost:5173
```

**Frontend (`frontend/.env`):**
```env
VITE_API_URL=http://localhost:8000
```

---

## 📡 API Endpoints

### Sellers
- `GET /sellers/` - Listar vendedores
- `POST /sellers/` - Crear vendedor
- `GET /sellers/{id}` - Obtener vendedor

### Clients
- `GET /clients/` - Listar clientes
- `POST /clients/` - Crear cliente (requiere lat/lng)
- `GET /clients/nearby/?latitude=X&longitude=Y&radius_km=5` - Clientes cercanos

### Routes
- `GET /routes/` - Listar rutas (filtros: seller_id, status, date)
- `POST /routes/` - Crear ruta
- `PUT /routes/{id}/status` - Actualizar estado

### Visits
- `POST /visits/checkin/` - Hacer check-in (captura GPS)
- `PUT /visits/checkout/` - Hacer check-out
- `GET /visits/` - Listar visitas (filtros: seller_id, client_id, date)

### Opportunities
- `GET /opportunities/` - Listar oportunidades
- `POST /opportunities/` - Crear oportunidad

### Dashboard
- `GET /dashboard/stats` - Estadísticas generales

**Documentación completa:** http://localhost:8000/docs

---

## 🌍 Funcionalidades Geoespaciales

### PostGIS - Análisis Geográfico

**Almacenamiento de coordenadas:**
```sql
-- Tipo de dato: POINT (longitud, latitud)
location POINT(SRID 4326)  -- WGS84 (GPS estándar)
```

**Consultas espaciales implementadas:**

1. **Calcular distancia** (metros):
```python
ST_Distance(
    client.location::geography,
    checkin_location::geography
)
```

2. **Buscar clientes cercanos**:
```python
ST_DWithin(
    client.location::geography,
    point::geography,
    radius_meters
)
```

3. **Validación de proximidad**:
- Al hacer check-in, se calcula la distancia al cliente
- Permite auditar si el vendedor realmente visitó el lugar

---

## 🎯 Caso de Uso Real: Alugandia

### Contexto
**Alugandia** es una empresa de distribución de perfiles de aluminio con 40 años de experiencia

### Problema a Resolver
- ❌ Falta de visibilidad de visitas a clientes
- ❌ Sin registro de ubicaciones de visita
- ❌ Dificultad para planificar rutas eficientes
- ❌ Pérdida de oportunidades de negocio

### Solución Implementada
- ✅ Seguimiento GPS de cada visita
- ✅ Validación automática de ubicación
- ✅ Dashboard con métricas
- ✅ Planificación de rutas optimizada por proximidad
- ✅ Registro completo de actividad comercial

### Datos de Prueba
El sistema incluye datos de prueba de la zona:
- **Vendedores**
- **Clientes**
- **Coordenadas GPS reales**

---

## 🔐 Seguridad y Privacidad

### Datos Sensibles
- Variables de entorno separadas (`.env`)
- Credenciales nunca en código fuente
- `.gitignore` configurado

### Producción
Para despliegue seguro:
```python
# CORS restrictivo
allow_origins=["https://tu-dominio.com"]

# Variables de entorno seguras
DATABASE_URL=postgresql://user:password@host:5432/db

# HTTPS obligatorio
```

---

## 🚀 Despliegue a Producción

### Railway (Recomendado)

```bash
# Instalar CLI
npm i -g @railway/cli

# Login
railway login

# Crear proyecto
railway init

# Desplegar
railway up
```

### Render

1. Conectar repositorio de GitHub
2. Crear PostgreSQL database (habilitar PostGIS)
3. Configurar servicios desde `render.yaml`

### DigitalOcean App Platform

1. Conectar repositorio
2. Configurar servicios (backend, frontend, database)
3. Habilitar PostGIS en managed database

**Ver guía completa:** [DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 🧪 Testing

```bash
# Backend
cd backend
pytest tests/

# Frontend
cd frontend
npm run test
```

---

## 📊 Monitoreo y Logs

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio
docker-compose logs -f backend
docker-compose logs -f frontend

# Ver estadísticas de recursos
docker stats
```

---

## 🛠️ Comandos Útiles

```bash
# Reiniciar un servicio
docker-compose restart backend

# Reconstruir imágenes
docker-compose build --no-cache

# Detener todo
docker-compose down

# Detener y eliminar volúmenes (⚠️ borra datos)
docker-compose down -v

# Acceder a PostgreSQL
docker exec -it salesmen_tracker_db psql -U postgres -d salesmen_tracker

# Ver clientes en BD
docker exec -it salesmen_tracker_db psql -U postgres -d salesmen_tracker -c "SELECT name, address FROM clients;"
```

---

## 🐛 Troubleshooting

### Puerto ocupado (5432)
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "5433:5432"  # En vez de "5432:5432"
```

### Error de NumPy
```bash
# Agregar a requirements.txt
numpy<2.0.0
```

### Frontend no carga datos
```bash
# Verificar CORS en backend
# Verificar URL en frontend/.env
VITE_API_URL=http://localhost:8000
```

### Problemas de permisos Docker
```bash
sudo usermod -aG docker $USER
# Cerrar y reabrir terminal
```

---

## 🤝 Contribuir

Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Add: nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📝 Roadmap

### Próximas Funcionalidades
- [ ] Autenticación JWT
- [ ] Notificaciones push
- [ ] Exportar reportes PDF/Excel
- [ ] Integración con Google Maps
- [ ] Optimización de rutas (algoritmo TSP)
- [ ] App móvil (React Native)
- [ ] Chat en tiempo real
- [ ] Sincronización offline

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

```
MIT License

Copyright (c) 2025 Alugandia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software...
```

---

## 👨‍💻 Autor

**Alugandia - Jose Manuel Gómez**
- 🌐 Empresa: [Alugandia SL](https://alugandia.es)
- 📧 Email: jmgomez@alugandia.es
- 📍 Ubicación: Real de Gandia, Valencia, España
- 💼 LinkedIn: [Jose Manuel Gómez](https://linkedin.com/in/jose-manuel-gomez)

---

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Excelente framework Python
- [PostGIS](https://postgis.net/) - Capacidades geoespaciales
- [Vue.js](https://vuejs.org/) - Framework reactivo
- [Tailwind CSS](https://tailwindcss.com/) - Sistema de diseño
- [Docker](https://www.docker.com/) - Contenedorización

---

## 📞 Soporte

Para preguntas o issues:
- 📧 Email: info@alugandia.es
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/salesmen-tracker/issues)
- 📖 Docs: [Documentación completa](docs/)

---

## ⭐ Si te gusta este proyecto

¡Dale una estrella en GitHub! ⭐

```bash
# Clonar y empezar
git clone https://github.com/tu-usuario/salesmen-tracker.git
cd salesmen-tracker
docker-compose up -d
```

---

**Hecho con ❤️ en Valencia, España 🇪🇸**