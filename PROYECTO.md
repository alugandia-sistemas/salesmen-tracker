# Salesmen Tracker - Resumen del Proyecto

## Descripcion General

Sistema de seguimiento de vendedores en ruta con geolocalizacion GPS para **Alugandia** (distribucion de aluminio, Gandia, Valencia). Permite gestionar visitas a clientes, validar ubicacion por GPS (check-in/check-out), planificar rutas y visualizar metricas en tiempo real.

---

## Stack Tecnologico

| Capa       | Tecnologia                        | Version |
|------------|-----------------------------------|---------|
| Frontend   | Vue.js 3 (Composition API)        | 3.3.8   |
| Build Tool | Vite                              | 5.0.5   |
| CSS        | Tailwind CSS                      | 3.3.6   |
| Mapas      | Leaflet + Leaflet Draw (CDN)      | 1.9.4   |
| Backend    | FastAPI                           | 0.104.1 |
| ORM        | SQLAlchemy + GeoAlchemy2          | 2.0.23  |
| BD         | PostgreSQL + PostGIS              | 15-3.3  |
| Server     | Uvicorn                           | 0.24.0  |
| Auth       | Bcrypt (password hashing)         | 4.0.1   |
| Deploy     | Railway (backend) + Vercel (frontend) | -   |

---

## Estructura del Proyecto

```
salesmen-tracker/
├── .env                          # Variables de entorno raiz (desarrollo)
├── docker-compose.yml            # Orquestacion de servicios (3 containers)
├── Dockerfile.backend            # Imagen Docker del backend
├── Dockerfile.frontend           # Imagen Docker del frontend (raiz)
├── README.md                     # Documentacion extensa del proyecto
│
├── backend/                      # ── API FastAPI ──
│   ├── .env                      # Variables de entorno backend
│   ├── main.py                   # App monolitica (~3000 lineas)
│   │                             #   - Modelos SQLAlchemy (8)
│   │                             #   - Schemas Pydantic (20+)
│   │                             #   - Endpoints API (40+)
│   │                             #   - Logica de negocio
│   ├── requirements.txt          # Dependencias Python
│   ├── Dockerfile                # Imagen Docker alternativa
│   ├── data/                     # Scripts SQL de seed y datos reales
│   │   ├── import_clients_3.sql
│   │   ├── seed_clientes_reales_odoo_2.sql
│   │   ├── seed_data_1.py
│   │   ├── seed_visitas.sql
│   │   └── seed_visitas_semana.py
│   ├── migrations/               # Migraciones manuales
│   │   └── migrate_client_types.py
│   ├── models/                   # (vacio - modelos en main.py)
│   ├── routers/                  # (vacio - rutas en main.py)
│   └── tests/                    # Tests Pytest
│       ├── conftest.py           # Fixtures: TestClient, DB con rollback
│       ├── test_gps_checkin.py
│       ├── test_sales_routes.py
│       └── test_zones.py
│
├── frontend/                     # ── App Vue.js 3 ──
│   ├── .env                      # VITE_API_URL (desarrollo)
│   ├── .env.production           # VITE_API_URL (produccion)
│   ├── package.json              # Dependencias npm
│   ├── vite.config.js            # Config Vite (SPA fallback)
│   ├── tailwind.config.js        # Config Tailwind
│   ├── postcss.config.js         # PostCSS + Autoprefixer
│   ├── vercel.json               # Config deploy Vercel (rewrites)
│   ├── index.html                # Entry HTML (incluye Leaflet CDN)
│   ├── Dockerfile                # Imagen Docker del frontend
│   └── src/
│       ├── main.js               # Entry point (createApp, router)
│       ├── App.vue               # Componente raiz
│       ├── router/
│       │   └── index.js          # Definicion de rutas
│       ├── components/
│       │   └── CheckInModal.vue  # Modal de check-in GPS
│       ├── views/
│       │   ├── Login.vue         # Login
│       │   ├── Registro.vue      # Registro simple
│       │   ├── RegistroConToken.vue  # Registro con invitacion
│       │   ├── ComercialV2.vue   # Dashboard comercial (activo)
│       │   ├── Comercial.vue     # Dashboard comercial (legacy)
│       │   ├── SellerDashboard.vue   # Dashboard vendedor
│       │   ├── AdminGestion.vue  # Gestion admin
│       │   ├── AdminInvitaciones.vue # Invitaciones
│       │   ├── AdminZones.vue    # Gestion de zonas (mapa)
│       │   ├── DirectorioClientes.vue # Directorio clientes
│       │   └── MyRoute.vue       # Vista de ruta del vendedor
│       ├── utils/
│       │   └── analytics.js      # Vercel Analytics + Web Vitals
│       └── assets/
│           └── main.css          # Estilos globales + Tailwind
│
├── docker-entrypoint-initdb.d/
│   └── 01-init-postgis.sql       # Inicializacion PostGIS
│
└── scripts de test (raiz)
    ├── test_gps_checkin.sh       # Test integracion GPS (curl)
    ├── test_gps_quick.sh         # Test rapido GPS
    └── test_performance.sh       # Benchmarks
```

---

## Modelos de Base de Datos

| Modelo       | Descripcion                     | Campos clave                                    |
|--------------|---------------------------------|-------------------------------------------------|
| Seller       | Vendedores                      | name, email, phone, password_hash, is_active    |
| Client       | Clientes                        | name, address, **location** (POINT GPS), client_type, sales_route_id |
| Route        | Rutas diarias planificadas      | seller_id, client_id, planned_date, status, visit_order |
| Visit        | Visitas con tracking GPS        | **checkin_location**, **checkout_location**, checkin_distance_meters, fraud_flags |
| Zone         | Zonas geograficas               | name, **geometry** (POLYGON)                    |
| SalesRoute   | Rutas comerciales (territorios) | name, zone_id, seller_id                        |
| Invitation   | Invitaciones de registro        | token, email, seller_name, is_used, expires_at  |
| Opportunity  | Oportunidades de negocio        | seller_id, client_id, title, estimated_value, status |

Tipos geoespaciales (PostGIS): `Geography(POINT, 4326)` y `Geometry(POLYGON, 4326)`

---

## Endpoints API Principales

```
Auth:      POST /auth/login/  |  POST /auth/register-with-token/
Sellers:   GET/POST /sellers/  |  GET /sellers/{id}/stats  |  GET /sellers/{id}/tracking/today
Clients:   GET/POST /clients/  |  GET /clients/nearby/  |  GET /clients/search/  |  GET /clients/sync/
Routes:    GET/POST /routes/  |  PUT /routes/reorder/  |  POST /routes/{id}/postpone/
Visits:    POST /visits/checkin/  |  POST /visits/checkin/v2/  |  POST /visits/checkout/
Zones:     GET/POST /zones/  |  PUT/DELETE /zones/{id}
SalesRoutes: GET/POST /sales-routes/
Dashboard: GET /dashboard/stats/  |  GET /dashboard/fraud-alerts/
Admin:     POST/GET /admin/invitations/
Health:    GET /health/
Docs:      GET /docs  (Swagger UI auto-generado)
```

---

## Variables de Entorno

| Variable        | Donde          | Valor desarrollo                                          |
|-----------------|----------------|-----------------------------------------------------------|
| DATABASE_URL    | backend/.env   | `postgresql://postgres:postgres@localhost:5433/salesmen_tracker` |
| PORT            | backend/.env   | `8000`                                                    |
| CORS_ORIGINS    | backend/.env   | `http://localhost:5173`                                   |
| VITE_API_URL    | frontend/.env  | `http://localhost:8000`                                   |

> **Nota:** En Docker, DATABASE_URL usa `@postgres:5432` (nombre del servicio). En local sin Docker usa `@localhost:5433`.

---

## Arranque para Desarrollo Local

### Opcion 1: Docker Compose (recomendado)

Levanta los 3 servicios (PostgreSQL+PostGIS, Backend, Frontend) con un solo comando:

```bash
# Desde la raiz del proyecto
docker compose up --build

# O en segundo plano
docker compose up --build -d
```

Servicios disponibles:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **PostgreSQL:** localhost:5433

Para ver logs:
```bash
docker compose logs -f backend    # Solo backend
docker compose logs -f frontend   # Solo frontend
docker compose logs -f            # Todos
```

Para parar:
```bash
docker compose down               # Para contenedores
docker compose down -v            # Para contenedores Y borra datos de BD
```

---

### Opcion 2: Sin Docker (servicios por separado)

#### Requisitos previos
- **Python 3.11+**
- **Node.js 18+** (con npm)
- **PostgreSQL 15** con extension **PostGIS 3.3** instalada

#### 1. Base de datos

```bash
# Crear base de datos con PostGIS
psql -U postgres -c "CREATE DATABASE salesmen_tracker;"
psql -U postgres -d salesmen_tracker -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

#### 2. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (backend/.env)
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/salesmen_tracker
# PORT=8000
# CORS_ORIGINS=http://localhost:5173

# Arrancar servidor con hot-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> Las tablas se crean automaticamente al arrancar (SQLAlchemy `create_all`).

#### 3. Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Verificar que frontend/.env tiene:
# VITE_API_URL=http://localhost:8000

# Arrancar dev server con HMR
npm run dev
```

#### 4. Seed de datos (opcional)

```bash
# Desde la raiz, con el backend corriendo
cd backend

# Seed de datos iniciales
python data/seed_data_1.py

# Importar clientes reales de Odoo
psql -U postgres -d salesmen_tracker -f data/seed_clientes_reales_odoo_2.sql
```

---

### Opcion 3: Mixta (BD en Docker, codigo local)

Util para tener PostGIS sin instalarlo localmente:

```bash
# Solo levantar PostgreSQL+PostGIS
docker compose up postgres -d

# Backend local (usar DATABASE_URL con localhost:5433)
cd backend
source .venv/bin/activate
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/salesmen_tracker uvicorn main:app --reload --port 8000

# Frontend local
cd frontend
npm run dev
```

---

## Tests

```bash
# Backend (requiere BD activa)
cd backend
source .venv/bin/activate
pytest tests/ -v

# Tests de integracion GPS (requiere backend corriendo)
bash test_gps_quick.sh
bash test_gps_checkin.sh
```

---

## Rutas del Frontend

| Ruta                | Vista                 | Acceso    |
|---------------------|-----------------------|-----------|
| `/login`            | Login.vue             | Publico   |
| `/registro`         | RegistroConToken.vue  | Publico   |
| `/registro-simple`  | Registro.vue          | Publico   |
| `/comercial`        | ComercialV2.vue       | Vendedor  |
| `/seller-dashboard` | SellerDashboard.vue   | Vendedor  |
| `/my-route`         | MyRoute.vue           | Vendedor  |
| `/admin/gestion`    | AdminGestion.vue      | Admin     |
| `/admin/invitaciones` | AdminInvitaciones.vue | Admin   |
| `/admin/clientes`   | DirectorioClientes.vue | Admin    |
| `/admin/zones`      | AdminZones.vue        | Admin     |

---

## Produccion

- **Frontend:** Vercel (auto-deploy desde GitHub)
- **Backend:** Railway
- **BD:** PostgreSQL gestionada en Railway
