# 🐧 Salesmen Tracker - Instalación en WSL Ubuntu (Windows 11)

## 📋 LISTA COMPLETA DE ARCHIVOS

```
salesmen-tracker/
├── docker-compose.yml          ← 1 archivo raíz
├── init.sql                     ← 1 archivo raíz
│
├── backend/                     ← 6 archivos
│   ├── main.py                 ⭐ ARCHIVO GRANDE (copiar de artefacto)
│   ├── seed_data.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env
│   └── .gitignore
│
└── frontend/                    ← 11 archivos
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── Dockerfile
    ├── .env
    ├── .gitignore
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── src/
    │   ├── main.js
    │   ├── App.vue             ⭐ ARCHIVO GRANDE (copiar de artefacto)
    │   └── assets/
    │       └── main.css

TOTAL: 20 archivos (18 pequeños + 2 grandes)
```

---

## 🚀 PASO A PASO - WSL UBUNTU

### PASO 0: Preparar WSL Ubuntu

```bash
# Abrir WSL Ubuntu (desde Windows: Win + R, escribir "wsl")

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar herramientas necesarias
sudo apt install -y git curl nano docker.io docker-compose

# Iniciar Docker
sudo service docker start

# Agregar tu usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER

# IMPORTANTE: Cerrar y reabrir WSL para que tome efecto
exit
# Volver a abrir WSL
```

---

### PASO 1: Crear la Estructura de Carpetas

```bash
# Ir a tu home
cd ~

# Crear estructura completa
mkdir -p salesmen-tracker/backend
mkdir -p salesmen-tracker/frontend/src/assets

# Verificar
cd salesmen-tracker
pwd
# Debería mostrar: /home/tu-usuario/salesmen-tracker
```

---

### PASO 2: Crear Archivos RAÍZ (2 archivos)

#### 📄 Archivo 1: `docker-compose.yml`

```bash
# Crear archivo
nano docker-compose.yml
```

**Copiar este contenido** (Ctrl+Shift+V en WSL para pegar):

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

**Guardar y salir**: `Ctrl+O` (Enter), `Ctrl+X`

#### 📄 Archivo 2: `init.sql`

```bash
# Crear archivo
nano init.sql
```

**Copiar este contenido**:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
SELECT PostGIS_version();
```

**Guardar y salir**: `Ctrl+O` (Enter), `Ctrl+X`

---

### PASO 3: Crear Archivos de BACKEND (6 archivos)

```bash
# Ir a carpeta backend
cd backend
```

#### 📄 Backend 1: `requirements.txt`

```bash
nano requirements.txt
```

**Copiar**:
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

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Backend 2: `.env`

```bash
nano .env
```

**Copiar**:
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/salesmen_tracker
PORT=8000
CORS_ORIGINS=http://localhost:5173
```

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Backend 3: `Dockerfile`

```bash
nano Dockerfile
```

**Copiar**:
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

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Backend 4: `.gitignore`

```bash
nano .gitignore
```

**Copiar**:
```
__pycache__/
*.py[cod]
venv/
.env
*.egg-info/
```

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Backend 5: `seed_data.py`

```bash
nano seed_data.py
```

**Copiar**:
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

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### ⭐ Backend 6: `main.py` (ARCHIVO GRANDE)

**ESTE archivo es MUY grande (~400 líneas). Opciones:**

**Opción A: Copiar desde el artefacto de Claude**
1. En esta conversación, busca el artefacto: **"Backend - FastAPI + PostgreSQL/PostGIS"**
2. Click en "Copy"
3. En WSL:
```bash
nano main.py
```
4. Pegar con `Ctrl+Shift+V`
5. Guardar: `Ctrl+O`, `Ctrl+X`

**Opción B: Usar Windows y copiar**
1. En Windows, abre el Explorador de archivos
2. En la barra de dirección escribe: `\\wsl$\Ubuntu\home\TU-USUARIO\salesmen-tracker\backend`
3. Click derecho → Nuevo → Archivo de texto → Renombrar a `main.py`
4. Abrir con VS Code o Notepad++
5. Copiar el contenido del artefacto "Backend - FastAPI"
6. Guardar

**Opción C: Descargar desde un gist (te lo puedo crear)**

---

### PASO 4: Crear Archivos de FRONTEND (11 archivos)

```bash
# Volver a raíz y entrar a frontend
cd ~/salesmen-tracker/frontend
```

#### 📄 Frontend 1: `package.json`

```bash
nano package.json
```

**Copiar**:
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

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Frontend 2: `vite.config.js`

```bash
nano vite.config.js
```

**Copiar**:
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

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Frontend 3: `index.html`

```bash
nano index.html
```

**Copiar**:
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

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Frontend 4: `.env`

```bash
nano .env
```

**Copiar**:
```
VITE_API_URL=http://localhost:8000
```

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Frontend 5: `.gitignore`

```bash
nano .gitignore
```

**Copiar**:
```
node_modules/
dist/
.env
*.local
.DS_Store
```

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Frontend 6: `Dockerfile`

```bash
nano Dockerfile
```

**Copiar**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
```

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Frontend 7: `tailwind.config.js`

```bash
nano tailwind.config.js
```

**Copiar**:
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Frontend 8: `postcss.config.js`

```bash
nano postcss.config.js
```

**Copiar**:
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Frontend 9: `src/main.js`

```bash
# Crear carpeta src si no existe
mkdir -p src/assets
cd src

nano main.js
```

**Copiar**:
```javascript
import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'

createApp(App).mount('#app')
```

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### 📄 Frontend 10: `src/assets/main.css`

```bash
cd assets
nano main.css
```

**Copiar**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
}
```

**Guardar**: `Ctrl+O`, `Ctrl+X`

#### ⭐ Frontend 11: `src/App.vue` (ARCHIVO GRANDE)

```bash
cd ~/salesmen-tracker/frontend/src
```

**ESTE archivo es MUY grande (~600 líneas). Opciones:**

**Opción A: Copiar desde artefacto**
1. Busca el artefacto: **"Frontend - Vue.js 3 Application"**
2. Click "Copy"
3. En WSL:
```bash
nano App.vue
```
4. Pegar: `Ctrl+Shift+V`
5. Guardar: `Ctrl+O`, `Ctrl+X`

**Opción B: Desde Windows**
1. Explorador: `\\wsl$\Ubuntu\home\TU-USUARIO\salesmen-tracker\frontend\src`
2. Crear `App.vue`
3. Abrir con VS Code
4. Copiar contenido del artefacto
5. Guardar

---

### PASO 5: Verificar que TODO está creado

```bash
cd ~/salesmen-tracker

# Ver estructura
tree -L 3
# O si no tienes tree:
find . -type f | sort
```

**Deberías ver 20 archivos.**

---

### PASO 6: EJECUTAR el Proyecto 🚀

```bash
cd ~/salesmen-tracker

# Verificar que Docker está corriendo
sudo service docker status
# Si no está: sudo service docker start

# Levantar todos los servicios
docker-compose up -d

# Ver logs (opcional)
docker-compose logs -f

# Esperar 30-60 segundos para que arranque todo

# Insertar datos de prueba
docker exec -it salesmen_tracker_backend python seed_data.py
```

---

### PASO 7: Abrir en el Navegador (Windows)

**En tu navegador de Windows (Chrome/Edge):**

1. Frontend: http://localhost:5173
2. API Docs: http://localhost:8000/docs

**¡Debería funcionar! 🎉**

---

## 🛠️ Comandos Útiles WSL

```bash
# Ver contenedores corriendo
docker ps

# Ver logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Reiniciar un servicio
docker-compose restart backend

# Detener todo
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Entrar a un contenedor
docker exec -it salesmen_tracker_backend bash
docker exec -it salesmen_tracker_frontend sh

# Ver IP de WSL (si necesitas acceder desde otra máquina)
ip addr show eth0 | grep inet
```

---

## 🎯 Acceso desde Windows

### Opción 1: Editor de Código (VS Code)

```bash
# Instalar VS Code en Windows
# Abrir WSL en VS Code:
code ~/salesmen-tracker
```

### Opción 2: Explorador de Windows

```
\\wsl$\Ubuntu\home\TU-USUARIO\salesmen-tracker
```

Puedes editar archivos directamente desde Windows.

---

## ✅ CHECKLIST FINAL

- [ ] WSL Ubuntu instalado y actualizado
- [ ] Docker instalado y corriendo
- [ ] 20 archivos creados
- [ ] `main.py` copiado (backend)
- [ ] `App.vue` copiado (frontend)
- [ ] `docker-compose up -d` ejecutado sin errores
- [ ] http://localhost:5173 funciona
- [ ] http://localhost:8000/docs funciona
- [ ] Datos de prueba insertados

---

## 🆘 Solución de Problemas

### Error: "docker: command not found"
```bash
sudo apt install docker.io docker-compose
sudo service docker start
```

### Error: "permission denied"
```bash
sudo usermod -aG docker $USER
# Cerrar y reabrir WSL
```

### Error: "port already in use"
```bash
# Ver qué usa el puerto
sudo lsof -i :8000
sudo lsof -i :5173

# Matar proceso
sudo kill -9 $(sudo lsof -t -i:8000)
```

### Frontend no carga
```bash
# Ver logs
docker-compose logs frontend

# Reconstruir
docker-compose down
docker-compose up -d --build
```

---

## 🎉 ¡LISTO!

Tu proyecto debería estar funcionando en:
- 🌐 http://localhost:5173
- 🔌 http://localhost:8000/docs

**¿Algún problema? Dime en qué paso te atascaste.**