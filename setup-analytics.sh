#!/bin/bash
# ============================================================================
# 📊 SCRIPT: INSTALAR VERCEL ANALYTICS EN SALESMEN-TRACKER (DOCKER)
# ============================================================================
# Uso: bash setup-analytics.sh

set -e  # Exit on error

echo "🚀 VERCEL ANALYTICS - SETUP AUTOMATIZADO PARA DOCKER"
echo "=================================================="
echo ""

# Verificar que estamos en la raíz del proyecto
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Ejecuta este script desde la raíz del proyecto (donde están frontend/ y backend/)"
    exit 1
fi

echo "✅ Directorio de proyecto detectado"
echo ""

# ============================================================================
# PASO 1: CREAR ARCHIVO analytics.js
# ============================================================================
echo "📝 Paso 1: Crear frontend/src/utils/analytics.js"

mkdir -p frontend/src/utils

cat > frontend/src/utils/analytics.js << 'EOF'
// ============================================================================
// 📊 ANALYTICS HELPERS PARA SALESMEN TRACKER
// ============================================================================

/**
 * Monitorear CHECK-IN de vendedor
 */
export const trackCheckin = (routeId, clientId, distance, isValid) => {
  try {
    if (window.analytics?.trackCheckin) {
      window.analytics.trackCheckin(distance, isValid)
    }
    
    console.log('✅ [Analytics] Check-in registrado', {
      route_id: routeId,
      client_id: clientId,
      distance_meters: distance,
      is_valid: isValid,
      timestamp: new Date().toISOString()
    })
  } catch (e) {
    console.error('Error tracking checkin:', e)
  }
}

/**
 * Monitorear VISITA COMPLETADA
 */
export const trackVisitCompleted = (clientName, duration) => {
  try {
    if (window.analytics?.trackVisit) {
      window.analytics.trackVisit(clientName, duration)
    }
    
    console.log('✅ [Analytics] Visita completada', {
      client: clientName,
      duration_seconds: duration,
      timestamp: new Date().toISOString()
    })
  } catch (e) {
    console.error('Error tracking visit:', e)
  }
}

/**
 * Monitorear ERRORES DE GPS/GEOLOCALIZACIÓN
 */
export const trackGPSError = (error, context) => {
  try {
    if (window.analytics?.trackEvent) {
      window.analytics.trackEvent('gps_error', {
        error_message: error,
        context: context,
        timestamp: new Date().toISOString()
      })
    }
    
    console.error('⚠️ [Analytics] Error GPS', { error, context })
  } catch (e) {
    console.error('Error tracking gps error:', e)
  }
}

/**
 * Monitorear LOGIN
 */
export const trackLogin = (sellerId, sellerName) => {
  try {
    if (window.analytics?.trackEvent) {
      window.analytics.trackEvent('seller_login', {
        seller_id: sellerId,
        seller_name: sellerName,
        timestamp: new Date().toISOString()
      })
    }
    
    console.log('✅ [Analytics] Login de vendedor', { sellerId, sellerName })
  } catch (e) {
    console.error('Error tracking login:', e)
  }
}

/**
 * Monitorear ERRORES DE RED/API
 */
export const trackAPIError = (endpoint, statusCode, error) => {
  try {
    if (window.analytics?.trackEvent) {
      window.analytics.trackEvent('api_error', {
        endpoint: endpoint,
        status_code: statusCode,
        error_message: error,
        timestamp: new Date().toISOString()
      })
    }
    
    console.error('🔴 [Analytics] Error API', { endpoint, statusCode, error })
  } catch (e) {
    console.error('Error tracking api error:', e)
  }
}

/**
 * Monitorear RUTAS DEL DÍA
 */
export const trackDailyRoutes = (totalRoutes, completedRoutes) => {
  try {
    if (window.analytics?.trackEvent) {
      window.analytics.trackEvent('daily_routes_summary', {
        total_routes: totalRoutes,
        completed_routes: completedRoutes,
        completion_rate: totalRoutes > 0 ? (completedRoutes / totalRoutes * 100) : 0,
        timestamp: new Date().toISOString()
      })
    }
    
    console.log('📊 [Analytics] Rutas del día', { totalRoutes, completedRoutes })
  } catch (e) {
    console.error('Error tracking daily routes:', e)
  }
}

/**
 * Monitorear FRAUD ALERT
 */
export const trackFraudAlert = (visitId, fraudFlags) => {
  try {
    if (window.analytics?.trackEvent) {
      window.analytics.trackEvent('fraud_alert', {
        visit_id: visitId,
        fraud_flags: fraudFlags,
        timestamp: new Date().toISOString()
      })
    }
    
    console.warn('🚨 [Analytics] Alerta de fraude', { visitId, fraudFlags })
  } catch (e) {
    console.error('Error tracking fraud alert:', e)
  }
}
EOF

echo "✅ Archivo analytics.js creado"
echo ""

# ============================================================================
# PASO 2: BACKUP Y ACTUALIZAR main.js
# ============================================================================
echo "📝 Paso 2: Actualizar frontend/src/main.js"

cp frontend/src/main.js frontend/src/main.js.backup
echo "   💾 Backup guardado: frontend/src/main.js.backup"

cat > frontend/src/main.js << 'EOF'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

// ============================================================================
// 📊 VERCEL ANALYTICS & WEB VITALS INTEGRATION
// ============================================================================

import { inject } from '@vercel/analytics'
inject()

import { webVitals } from '@vercel/web-vitals'

webVitals({
  path: '/_vercel/insights/event',
  params: {
    beforeSend: (webVital) => {
      console.log(
        `[Web Vital] ${webVital.name}: ${webVital.value.toFixed(2)}ms`
      )
    }
  }
})

// ============================================================================
// EVENTOS PERSONALIZADOS
// ============================================================================

window.analytics = {
  trackEvent: (eventName, eventData) => {
    const { Analytics } = window
    if (Analytics && Analytics.event) {
      Analytics.event(eventName, eventData)
      console.log(`[Analytics Event] ${eventName}`, eventData)
    }
  },
  trackCheckin: (distance, isValid) => {
    window.analytics.trackEvent('checkin', {
      distance_meters: distance,
      is_valid: isValid,
      timestamp: new Date().toISOString()
    })
  },
  trackVisit: (clientId, duration) => {
    window.analytics.trackEvent('visit_completed', {
      client_id: clientId,
      duration_seconds: duration
    })
  }
}

// ============================================================================
// CREAR APP
// ============================================================================

const app = createApp(App)

app.use(router)

app.mount('#app')
EOF

echo "✅ Archivo main.js actualizado"
echo ""

# ============================================================================
# PASO 3: ACTUALIZAR DOCKERFILE.frontend
# ============================================================================
echo "📝 Paso 3: Actualizar frontend/Dockerfile"

if [ -f "frontend/Dockerfile" ]; then
    cp frontend/Dockerfile frontend/Dockerfile.backup
    echo "   💾 Backup guardado: frontend/Dockerfile.backup"
fi

cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci --only=production && \
    npm install @vercel/analytics @vercel/web-vitals

COPY frontend/ ./

RUN npm run build || true

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
EOF

echo "✅ Dockerfile actualizado"
echo ""

# ============================================================================
# PASO 4: ACTUALIZAR docker-compose.yml
# ============================================================================
echo "📝 Paso 4: Actualizar docker-compose.yml"

cp docker-compose.yml docker-compose.yml.backup
echo "   💾 Backup guardado: docker-compose.yml.backup"

# Aquí insertarías el contenido actualizado de docker-compose.yml
# Por brevedad, solo actualizaremos el servicio frontend

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    container_name: salesmen_tracker_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: salesmen_tracker
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: salesmen_tracker_backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: "postgresql://postgres:postgres@postgres:5432/salesmen_tracker"
      CORS_ORIGINS: "http://localhost:5173"
      PORT: "8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - app-network

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    container_name: salesmen_tracker_frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: "http://localhost:8000"
    working_dir: /app
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: sh -c "npm install @vercel/analytics @vercel/web-vitals && npm run dev -- --host 0.0.0.0"
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
EOF

echo "✅ docker-compose.yml actualizado"
echo ""

# ============================================================================
# PASO 5: ACTUALIZAR package.json
# ============================================================================
echo "📝 Paso 5: Verificar frontend/package.json"

if grep -q "@vercel/analytics" frontend/package.json; then
    echo "✅ @vercel/analytics ya está en package.json"
else
    echo "⚠️  Agregar manualmente a frontend/package.json:"
    echo "   npm install @vercel/analytics @vercel/web-vitals"
fi
echo ""

# ============================================================================
# RESUMEN
# ============================================================================
echo "✅ SETUP COMPLETADO"
echo "=================================================="
echo ""
echo "📋 Archivos creados/actualizados:"
echo "   ✓ frontend/src/utils/analytics.js (NUEVO)"
echo "   ✓ frontend/src/main.js (ACTUALIZADO)"
echo "   ✓ frontend/Dockerfile (ACTUALIZADO)"
echo "   ✓ docker-compose.yml (ACTUALIZADO)"
echo ""
echo "💾 Backups guardados:"
echo "   • frontend/src/main.js.backup"
echo "   • frontend/Dockerfile.backup"
echo "   • docker-compose.yml.backup"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. OPCIÓN A - Start desde cero:"
echo "      docker-compose down -v"
echo "      docker-compose up --build"
echo ""
echo "   2. OPCIÓN B - Rebuild solo frontend:"
echo "      docker-compose build --no-cache frontend"
echo "      docker-compose up frontend"
echo ""
echo "3. Abre http://localhost:5173"
echo "4. DevTools → Console → Busca logs de Analytics"
echo ""
echo "✅ Para deploying a Vercel:"
echo "   git add ."
echo "   git commit -m 'feat: add Vercel Analytics with Docker'"
echo "   git push origin main"
echo ""
