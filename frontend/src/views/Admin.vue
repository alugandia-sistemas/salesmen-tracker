<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
    <!-- HEADER -->
    <header class="bg-slate-950 shadow-xl border-b-4 border-indigo-600 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold text-lg">
            👨‍💼 ADMIN
          </div>
          <h1 class="text-2xl font-bold text-white">Alugandia - Salesmen Tracker</h1>
        </div>
        <div class="text-right">
          <p class="text-sm text-indigo-300 font-semibold">{{ currentTime }}</p>
          <p class="text-xs text-gray-400">Sistema de Gestión Comercial</p>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- TAB NAVIGATION -->
      <div class="flex gap-3 mb-8 flex-wrap">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-6 py-3 font-semibold rounded-lg transition-all flex items-center gap-2',
            activeTab === tab.id 
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/50' 
              : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
          ]"
        >
          {{ tab.icon }} {{ tab.name }}
        </button>
      </div>

      <!-- 1️⃣ DASHBOARD -->
      <div v-if="activeTab === 'dashboard'" class="space-y-6">
        <h2 class="text-3xl font-bold text-white">📊 Dashboard - Control Operativo</h2>
        
        <!-- TARJETAS DE MÉTRICAS -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-gradient-to-br from-blue-900 to-blue-800 rounded-lg shadow-lg p-6 border-l-4 border-blue-400">
            <p class="text-blue-200 text-sm font-semibold">Visitas Hoy</p>
            <p class="text-4xl font-bold text-white mt-2">{{ stats.total_visits_today }}</p>
            <p class="text-xs text-blue-300 mt-3">Total del día</p>
          </div>

          <div class="bg-gradient-to-br from-green-900 to-green-800 rounded-lg shadow-lg p-6 border-l-4 border-green-400">
            <p class="text-green-200 text-sm font-semibold">✅ Check-ins Válidos</p>
            <p class="text-4xl font-bold text-white mt-2">{{ stats.valid_checkins }}</p>
            <p class="text-xs text-green-300 mt-3">Ubicación correcta</p>
          </div>

          <div class="bg-gradient-to-br from-red-900 to-red-800 rounded-lg shadow-lg p-6 border-l-4 border-red-400">
            <p class="text-red-200 text-sm font-semibold">⚠️ Inválidos</p>
            <p class="text-4xl font-bold text-white mt-2">{{ stats.invalid_checkins }}</p>
            <p class="text-xs text-red-300 mt-3">Fuera de rango</p>
          </div>

          <div class="bg-gradient-to-br from-orange-900 to-orange-800 rounded-lg shadow-lg p-6 border-l-4 border-orange-400">
            <p class="text-orange-200 text-sm font-semibold">🚨 Anomalías Tipo 1</p>
            <p class="text-4xl font-bold text-white mt-2">{{ stats.fraud_detections }}</p>
            <p class="text-xs text-orange-300 mt-3">Fraudes detectados</p>
          </div>
        </div>

        <!-- INDICADOR DE CALIDAD -->
        <div class="bg-slate-800 rounded-lg shadow-lg p-8 border border-slate-700">
          <h3 class="text-xl font-bold text-white mb-6">🎯 Indicador de Calidad de Datos</h3>
          <div class="flex items-center gap-8">
            <div>
              <div class="text-6xl font-bold text-indigo-400">{{ stats.quality_score }}</div>
              <p class="text-gray-400 mt-2">Precisión operativa</p>
            </div>
            <div class="flex-1">
              <div class="bg-slate-700 rounded-full h-6 overflow-hidden">
                <div 
                  class="h-full bg-gradient-to-r from-green-500 via-indigo-500 to-blue-600 transition-all"
                  :style="{ width: stats.quality_score }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2️⃣ RUTAS (3-5 DÍAS) -->
      <div v-if="activeTab === 'routes'" class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-3xl font-bold text-white">🗓️ Rutas Próximos 5 Días</h2>
          <button 
            @click="loadRoutes"
            class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
          >
            🔄 Recargar
          </button>
        </div>

        <div v-if="routes.length === 0" class="bg-slate-800 rounded-lg p-8 text-center border border-slate-700">
          <p class="text-gray-400 text-lg">⏳ Cargando rutas...</p>
        </div>

        <!-- LISTA DE RUTAS -->
        <div class="space-y-4">
          <div 
            v-for="route in routes" 
            :key="route.id"
            class="bg-slate-800 rounded-lg shadow-lg border border-slate-700 overflow-hidden hover:border-indigo-500 transition-colors"
          >
            <!-- HEADER DE RUTA -->
            <div 
              @click="toggleRouteExpanded(route.id)"
              class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 cursor-pointer hover:from-slate-600 flex items-center justify-between"
            >
              <div class="flex items-center gap-4 flex-1">
                <span class="text-2xl">{{ expandedRoutes[route.id] ? '▼' : '▶' }}</span>
                <div>
                  <p class="text-white font-bold text-lg">{{ route.seller?.name || 'Vendedor desconocido' }}</p>
                  <p class="text-gray-400 text-sm">{{ formatDate(route.planned_date) }} • {{ route.planned_time }}</p>
                </div>
              </div>
              <div class="text-right">
                <span :class="[
                  'px-3 py-1 rounded-full text-sm font-semibold',
                  route.status === 'completed' ? 'bg-green-600 text-white' :
                  route.status === 'in_progress' ? 'bg-blue-600 text-white' :
                  route.status === 'cancelled' ? 'bg-red-600 text-white' :
                  'bg-gray-600 text-white'
                ]">
                  {{ formatStatus(route.status) }}
                </span>
              </div>
            </div>

            <!-- CONTENIDO EXPANDIDO: CLIENTES -->
            <div v-if="expandedRoutes[route.id]" class="px-6 py-4 space-y-3 border-t border-slate-700">
              <div class="bg-slate-900 rounded-lg p-4 border border-slate-600">
                <div class="flex items-start gap-4">
                  <div class="text-3xl">📍</div>
                  <div class="flex-1">
                    <p class="text-white font-bold">{{ route.client?.name }}</p>
                    <p class="text-gray-400 text-sm mt-1">{{ route.client?.address }}</p>
                    <div class="flex gap-4 mt-3 flex-wrap">
                      <span class="text-xs bg-indigo-900 text-indigo-300 px-2 py-1 rounded">📞 {{ route.client?.phone }}</span>
                      <span class="text-xs bg-purple-900 text-purple-300 px-2 py-1 rounded">{{ route.client?.client_type }}</span>
                    </div>
                    <div class="mt-4 flex gap-2">
                      <button 
                        @click="openVisitDetail(route)"
                        class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded text-sm font-semibold flex items-center gap-2"
                      >
                        📊 Ver Visitas
                      </button>
                      <button 
                        @click="openCheckInModal(route)"
                        class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm font-semibold flex items-center gap-2"
                      >
                        ✅ Registrar Check-in
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3️⃣ ALERTAS (ANOMALÍAS) -->
      <div v-if="activeTab === 'alerts'" class="space-y-6">
        <h2 class="text-3xl font-bold text-white">🚨 Alertas y Anomalías</h2>

        <!-- FILTROS DE ANOMALÍAS -->
        <div class="flex gap-3 flex-wrap">
          <button 
            @click="anomalyFilter = 'all'"
            :class="[
              'px-4 py-2 rounded-lg font-semibold transition-all',
              anomalyFilter === 'all' ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-gray-300'
            ]"
          >
            Todas
          </button>
          <button 
            @click="anomalyFilter = 'type1'"
            :class="[
              'px-4 py-2 rounded-lg font-semibold transition-all',
              anomalyFilter === 'type1' ? 'bg-red-600 text-white' : 'bg-slate-700 text-gray-300'
            ]"
          >
            🔴 Tipo 1 (Fraude)
          </button>
          <button 
            @click="anomalyFilter = 'type2'"
            :class="[
              'px-4 py-2 rounded-lg font-semibold transition-all',
              anomalyFilter === 'type2' ? 'bg-yellow-600 text-white' : 'bg-slate-700 text-gray-300'
            ]"
          >
            🟡 Tipo 2 (Técnica)
          </button>
          <button 
            @click="anomalyFilter = 'invalid'"
            :class="[
              'px-4 py-2 rounded-lg font-semibold transition-all',
              anomalyFilter === 'invalid' ? 'bg-orange-600 text-white' : 'bg-slate-700 text-gray-300'
            ]"
          >
            ⚠️ Check-ins Inválidos
          </button>
        </div>

        <!-- TABLA DE ALERTAS -->
        <div class="bg-slate-800 rounded-lg shadow-lg overflow-hidden border border-slate-700">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-slate-900 border-b-2 border-slate-700">
                <tr>
                  <th class="px-6 py-4 text-left text-indigo-300 font-bold">Timestamp</th>
                  <th class="px-6 py-4 text-left text-indigo-300 font-bold">Vendedor</th>
                  <th class="px-6 py-4 text-left text-indigo-300 font-bold">Cliente</th>
                  <th class="px-6 py-4 text-left text-indigo-300 font-bold">Tipo de Anomalía</th>
                  <th class="px-6 py-4 text-left text-indigo-300 font-bold">Distancia</th>
                  <th class="px-6 py-4 text-left text-indigo-300 font-bold">Detalles</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="alert in filteredAnomalies" 
                  :key="alert.visit_id"
                  class="border-b border-slate-700 hover:bg-slate-700 transition-colors"
                >
                  <td class="px-6 py-4 text-gray-300 font-mono text-sm">{{ formatTime(alert.timestamp) }}</td>
                  <td class="px-6 py-4 text-white font-semibold">{{ alert.seller }}</td>
                  <td class="px-6 py-4 text-gray-300">{{ alert.client }}</td>
                  <td class="px-6 py-4">
                    <span v-if="getAnomalyType(alert) === 'type1'" class="bg-red-900 text-red-200 px-3 py-1 rounded-full text-sm font-semibold">
                      🔴 Fraude
                    </span>
                    <span v-else-if="getAnomalyType(alert) === 'type2'" class="bg-yellow-900 text-yellow-200 px-3 py-1 rounded-full text-sm font-semibold">
                      🟡 Técnica
                    </span>
                    <span v-else class="bg-orange-900 text-orange-200 px-3 py-1 rounded-full text-sm font-semibold">
                      ⚠️ Inválido
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <span class="bg-slate-700 text-gray-300 px-3 py-1 rounded font-mono text-sm">
                      {{ alert.distance_meters?.toFixed(0) || '-' }}m
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex flex-wrap gap-1">
                      <span 
                        v-for="flag in alert.fraud_flags" 
                        :key="flag"
                        class="bg-slate-700 text-gray-300 px-2 py-1 rounded text-xs"
                      >
                        {{ flag }}
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="filteredAnomalies.length === 0" class="px-6 py-8 text-center text-gray-400">
            ✅ Sin anomalías detectadas en este filtro
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL CHECK-IN -->
    <CheckInModal 
      v-if="showCheckInModal"
      :route="selectedRoute"
      @close="showCheckInModal = false"
      @success="onCheckInSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CheckInModal from './components/CheckInModal.vue'

const API_URL = 'http://localhost:8000'

// ============================================================================
// ESTADO REACTIVO
// ============================================================================

const activeTab = ref('dashboard')
const currentTime = ref('')

const tabs = [
  { id: 'dashboard', name: 'Dashboard', icon: '📊' },
  { id: 'routes', name: 'Rutas', icon: '🗓️' },
  { id: 'alerts', name: 'Alertas', icon: '🚨' }
]

const stats = ref({
  total_visits_today: 0,
  valid_checkins: 0,
  invalid_checkins: 0,
  fraud_detections: 0,
  quality_score: '0%',
  average_distance_meters: 0
})

const routes = ref([])
const anomalies = ref([])
const expandedRoutes = ref({})
const showCheckInModal = ref(false)
const selectedRoute = ref(null)
const anomalyFilter = ref('all')

// ============================================================================
// FUNCIONES
// ============================================================================

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleDateString('es-ES', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const formatStatus = (status) => {
  const statuses = {
    'pending': '⏳ Pendiente',
    'in_progress': '▶️ En progreso',
    'completed': '✅ Completado',
    'cancelled': '❌ Cancelado'
  }
  return statuses[status] || status
}

const toggleRouteExpanded = (routeId) => {
  expandedRoutes.value[routeId] = !expandedRoutes.value[routeId]
}

const openCheckInModal = (route) => {
  selectedRoute.value = route
  showCheckInModal.value = true
}

const openVisitDetail = (route) => {
  // TODO: Implementar vista detallada de visitas
  console.log('Ver visitas de:', route.id)
}

const getAnomalyType = (alert) => {
  const flags = alert.fraud_flags || []
  if (flags.some(f => f.includes('OUT_OF_RANGE') || f.includes('DUPLICATE') || f.includes('MULTIPLE'))) {
    return 'type1'
  } else if (flags.some(f => f.includes('OUT_OF_HOURS') || f.includes('CLIENT_NOT_FOUND'))) {
    return 'type2'
  }
  return 'invalid'
}

const filteredAnomalies = computed(() => {
  return anomalies.value.filter(alert => {
    if (anomalyFilter.value === 'type1') {
      return getAnomalyType(alert) === 'type1'
    } else if (anomalyFilter.value === 'type2') {
      return getAnomalyType(alert) === 'type2'
    } else if (anomalyFilter.value === 'invalid') {
      return !alert.fraud_flags || alert.fraud_flags.length === 0
    }
    return true
  })
})

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

// ============================================================================
// CARGAR DATOS
// ============================================================================

const loadDashboard = async () => {
  try {
    const response = await fetch(`${API_URL}/dashboard/stats/`)
    const data = await response.json()
    stats.value = data
  } catch (error) {
    console.error('Error cargando dashboard:', error)
  }
}

const loadRoutes = async () => {
  try {
    const response = await fetch(`${API_URL}/routes/`)
    const data = await response.json()
    
    // Filtrar rutas de los próximos 5 días
    const now = new Date()
    const fiveDaysLater = new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000)
    
    routes.value = data.filter(route => {
      const routeDate = new Date(route.planned_date)
      return routeDate >= now && routeDate <= fiveDaysLater
    }).sort((a, b) => new Date(a.planned_date) - new Date(b.planned_date))
  } catch (error) {
    console.error('Error cargando rutas:', error)
  }
}

const loadAnomalies = async () => {
  try {
    const response = await fetch(`${API_URL}/dashboard/fraud-alerts/?hours=72`)
    const data = await response.json()
    anomalies.value = data.alerts || []
  } catch (error) {
    console.error('Error cargando anomalías:', error)
  }
}

const onCheckInSuccess = () => {
  showCheckInModal.value = false
  loadDashboard()
  loadAnomalies()
  loadRoutes()
}

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(() => {
  updateTime()
  setInterval(updateTime, 1000)
  
  loadDashboard()
  loadRoutes()
  loadAnomalies()
  
  // Recargar cada 30 segundos
  setInterval(() => {
    loadDashboard()
    loadAnomalies()
  }, 30000)
})
</script>

<style scoped>
* {
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
}
</style>
