# ✅ Checklist Completa - Salesmen Tracker

## 📁 Estructura y Progreso

```
salesmen-tracker/
├── [ ] docker-compose.yml
├── [ ] init.sql
│
├── backend/
│   ├── [ ] main.py                 ⭐ GRANDE (~400 líneas)
│   ├── [ ] seed_data.py
│   ├── [ ] requirements.txt
│   ├── [ ] Dockerfile
│   ├── [ ] .env
│   └── [ ] .gitignore
│
└── frontend/
    ├── [ ] package.json
    ├── [ ] vite.config.js
    ├── [ ] index.html
    ├── [ ] Dockerfile
    ├── [ ] .env
    ├── [ ] .gitignore
    ├── [ ] tailwind.config.js
    ├── [ ] postcss.config.js
    └── src/
        ├── [ ] main.js
        ├── [ ] App.vue             ⭐ GRANDE (~600 líneas)
        └── assets/
            └── [ ] main.css
```

**Total: 20 archivos**

---

## 🚀 PASO 0: Preparación

```bash
cd ~
mkdir -p salesmen-tracker/backend
mkdir -p salesmen-tracker/frontend/src/assets
cd salesmen-tracker
```

- [ ] Carpetas creadas
- [ ] Estás en `~/salesmen-tracker`

---

## 📄 ARCHIVOS RAÍZ (2 archivos)

### ☑️ Archivo 1/20: `docker-compose.yml`

**Ubicación:** `/salesmen-tracker/docker-compose.yml`

```bash
nano docker-compose.yml
```

**Contenido:**
```yaml
version: '3.8'

services:
  db:
    image: postgis/postgis:15-3.3
    container_name: salesmen_tracker_db
    environment:
      POSTGRES_DB: salesmen_tracker
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    container_name: salesmen_tracker_backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/salesmen_tracker
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    container_name: salesmen_tracker_frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev -- --host

volumes:
  postgres_data:
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `docker-compose.yml` creado

---

### ☑️ Archivo 2/20: `init.sql`

**Ubicación:** `/salesmen-tracker/init.sql`

```bash
nano init.sql
```

**Contenido:**
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
SELECT PostGIS_version();
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `init.sql` creado

---

## 🐍 BACKEND (6 archivos)

```bash
cd backend
```

### ☑️ Archivo 3/20: `backend/requirements.txt`

```bash
nano requirements.txt
```

**Contenido:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
geoalchemy2==0.14.2
pydantic==2.5.0
python-dotenv==1.0.0
shapely==2.0.2
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `requirements.txt` creado

---

### ☑️ Archivo 4/20: `backend/.env`

```bash
nano .env
```

**Contenido:**
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/salesmen_tracker
PORT=8000
CORS_ORIGINS=http://localhost:5173
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `.env` creado

---

### ☑️ Archivo 5/20: `backend/Dockerfile`

```bash
nano Dockerfile
```

**Contenido:**
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev gdal-bin libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `Dockerfile` creado

---

### ☑️ Archivo 6/20: `backend/.gitignore`

```bash
nano .gitignore
```

**Contenido:**
```
__pycache__/
*.py[cod]
venv/
.env
*.egg-info/
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `.gitignore` creado

---

### ☑️ Archivo 7/20: `backend/seed_data.py`

```bash
nano seed_data.py
```

**Contenido:**
```python
from main import SessionLocal, Seller, Client

def seed_database():
    db = SessionLocal()
    
    try:
        existing = db.query(Seller).first()
        if existing:
            print("⚠️  La base de datos ya tiene datos")
            return
        
        sellers = [
            Seller(name="José Almiñana", email="jose@alugandia.es", phone="962873543", active=1),
            Seller(name="Ernesto Arocas", email="ernesto@alugandia.es", phone="962873543", active=1),
            Seller(name="Jose Manuel Gómez", email="jm@alugandia.es", phone="962873543", active=1)
        ]
        
        clients = [
            Client(
                name="Carpintería Valencia",
                address="Av. del Puerto 245, Valencia",
                phone="963123456",
                email="info@carpivalencia.com",
                location='POINT(-0.3763 39.4699)',
                status="active"
            ),
            Client(
                name="Aluminis Gandia",
                address="Calle Mayor 89, Gandia",
                phone="962456789",
                email="contacto@aluminisgandia.com",
                location='POINT(-0.1828 38.9672)',
                status="active"
            ),
            Client(
                name="Perfiles Alzira",
                address="Industrial Nord, Alzira",
                phone="962789012",
                email="alzira@perfiles.com",
                location='POINT(-0.4351 39.1521)',
                status="active"
            ),
        ]
        
        db.add_all(sellers)
        db.add_all(clients)
        db.commit()
        
        print(f"✅ Insertados {len(sellers)} vendedores y {len(clients)} clientes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `seed_data.py` creado

---

### ⭐ Archivo 8/20: `backend/main.py` (ARCHIVO GRANDE)

**Ubicación:** `/salesmen-tracker/backend/main.py`

**MÉTODO 1: Desde WSL**
```bash
nano main.py
```

**MÉTODO 2: Desde Windows (RECOMENDADO)**
1. Abrir Explorador de Windows
2. Ir a: `\\wsl$\Ubuntu\home\TU-USUARIO\salesmen-tracker\backend`
3. Crear archivo: `main.py`
4. Abrir con VS Code o Notepad++
5. Copiar contenido del artefacto **"Backend - FastAPI + PostgreSQL/PostGIS"**
6. Guardar

**¿Dónde está el código?**
- En esta conversación de Claude
- Busca el artefacto: **"Backend - FastAPI + PostgreSQL/PostGIS"**
- Click en "Copy"
- Pegar en el archivo

- [ ] ✅ `main.py` creado (~400 líneas)

---

## ⚛️ FRONTEND (11 archivos)

```bash
cd ~/salesmen-tracker/frontend
```

### ☑️ Archivo 9/20: `frontend/package.json`

```bash
nano package.json
```

**Contenido:**
```json
{
  "name": "salesmen-tracker-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.8"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.5.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "vite": "^5.0.5"
  }
}
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `package.json` creado

---

### ☑️ Archivo 10/20: `frontend/vite.config.js`

```bash
nano vite.config.js
```

**Contenido:**
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: true
  }
})
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `vite.config.js` creado

---

### ☑️ Archivo 11/20: `frontend/index.html`

```bash
nano index.html
```

**Contenido:**
```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Salesmen Tracker - Alugandia</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `index.html` creado

---

### ☑️ Archivo 12/20: `frontend/.env`

```bash
nano .env
```

**Contenido:**
```
VITE_API_URL=http://localhost:8000
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `.env` creado

---

### ☑️ Archivo 13/20: `frontend/.gitignore`

```bash
nano .gitignore
```

**Contenido:**
```
node_modules/
dist/
.env
*.local
.DS_Store
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `.gitignore` creado

---

### ☑️ Archivo 14/20: `frontend/Dockerfile`

```bash
nano Dockerfile
```

**Contenido:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

- [ ] ✅ `Dockerfile` creado

---

### ☑️ Archivo 15/20: `frontend/tailwind.config.js`

```bash
nano tailwind.config.js
```

**Contenido:**
```javascri