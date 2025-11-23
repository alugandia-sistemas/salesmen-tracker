<template>
  <div class="min-h-screen bg-white">
    <!-- HEADER MINIMALISTA -->
    <header class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="px-3 sm:px-4 py-4 sm:py-5">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-10 h-10 bg-black rounded-lg flex items-center justify-center text-white text-xs font-bold">
              AD
            </div>
            <h1 class="text-lg sm:text-xl font-semibold text-black truncate">Alugandia</h1>
          </div>
          <div class="text-right text-xs sm:text-sm">
            <p class="text-black font-medium hidden sm:block">Admin</p>
            <p class="text-gray-500 text-xs">{{ currentTime }}</p>
          </div>
        </div>
      </div>
    </header>

    <div class="px-3 sm:px-4 py-4 sm:py-8 max-w-7xl mx-auto">
      <!-- TAB NAVIGATION MINIMALISTA -->
      <div class="flex gap-2 sm:gap-4 mb-8 border-b border-gray-200">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'pb-3 sm:pb-4 font-medium text-sm sm:text-base transition-all border-b-2 whitespace-nowrap',
            activeTab === tab.id 
              ? 'text-black border-b-black' 
              : 'text-gray-400 border-b-transparent hover:text-gray-600'
          ]"
        >
          {{ tab.icon }} <span class="hidden xs:inline">{{ tab.name }}</span>
        </button>
      </div>

      <!-- 1️⃣ DASHBOARD MINIMALISTA -->
      <div v-if="activeTab === 'dashboard'" class="space-y-8">
        <h2 class="text-2xl sm:text-3xl font-semibold text-black">Resumen general</h2>
        
        <!-- MÉTRICAS GRID -->
        <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="border border-gray-200 rounded-lg p-4 sm:p-6 hover:border-gray-300 transition-colors">
            <p class="text-gray-600 text-xs sm:text-sm font-medium mb-3">Visitas hoy</p>
            <p class="text-3xl sm:text-4xl font-semibold text-black">{{ stats.total_visits_today }}</p>
          </div>

          <div class="border border-gray-200 rounded-lg p-4 sm:p-6 hover:border-gray-300 transition-colors">
            <p class="text-gray-600 text-xs sm:text-sm font-medium mb-3">Válidos</p>
            <p class="text-3xl sm:text-4xl font-semibold text-black">{{ stats.valid_checkins }}</p>
          </div>

          <div class="border border-gray-200 rounded-lg p-4 sm:p-6 hover:border-gray-300 transition-colors">
            <p class="text-gray-600 text-xs sm:text-sm font-medium mb-3">Inválidos</p>
            <p class="text-3xl sm:text-4xl font-semibold text-black">{{ stats.invalid_checkins }}</p>
          </div>

          <div class="border border-gray-200 rounded-lg p-4 sm:p-6 hover:border-gray-300 transition-colors">
            <p class="text-gray-600 text-xs sm:text-sm font-medium mb-3">Alertas</p>
            <p class="text-3xl sm:text-4xl font-semibold text-black">{{ stats.fraud_detections }}</p>
          </div>
        </div>

        <!-- INDICADOR DE CALIDAD -->
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 sm:p-8">
          <h3 class="text-sm font-medium text-gray-600 mb-6">Indicador de calidad</h3>
          <div class="flex flex-col sm:flex-row items-center gap-6 sm:gap-8">
            <div>
              <div class="text-5xl sm:text-6xl font-semibold text-black">{{ stats.quality_score }}</div>
            </div>
            <div class="flex-1 w-full sm:w-auto">
              <div class="bg-white rounded-full h-2 overflow-hidden border border-gray-200">
                <div 
                  class="h-full bg-black transition-all"
                  :style="{ width: stats.quality_score }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2️⃣ RUTAS MINIMALISTA -->
      <div v-if="activeTab === 'routes'" class="space-y-6">
        <div class="flex items-center justify-between gap-2">
          <h2 class="text-2xl sm:text-3xl font-semibold text-black">Rutas (5 días)</h2>
          <button 
            @click="loadRoutes"
            class="text-black hover:text-gray-600 p-2"
            title="Recargar"
          >
            ↻
          </button>
        </div>

        <div v-if="routes.length === 0" class="text-center py-12">
          <p class="text-gray-500">Cargando rutas...</p>
        </div>

        <!-- LISTA DE RUTAS -->
        <div class="space-y-3">
          <div 
            v-for="route in routes" 
            :key="route.id"
            class="border border-gray-200 rounded-lg hover:border-gray-300 transition-colors overflow-hidden"
          >
            <!-- HEADER -->
            <div 
              @click="toggleRouteExpanded(route.id)"
              class="px-4 sm:px-6 py-4 cursor-pointer hover:bg-gray-50 flex items-center justify-between gap-2 border-b border-gray-100"
            >
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <span class="text-gray-400 text-lg">{{ expandedRoutes[route.id] ? '−' : '+' }}</span>
                <div class="min-w-0">
                  <p class="font-medium text-black text-sm sm:text-base">{{ route.seller?.name }}</p>
                  <p class="text-xs sm:text-sm text-gray-500">{{ formatDate(route.planned_date) }} • {{ route.planned_time }}</p>
                </div>
              </div>
              <span class="text-xs font-medium text-gray-500 flex-shrink-0">
                {{ formatStatusShort(route.status) }}
              </span>
            </div>

            <!-- CONTENIDO EXPANDIDO -->
            <div v-if="expandedRoutes[route.id]" class="px-4 sm:px-6 py-4 space-y-4 bg-gray-50 border-t border-gray-100">
              <div class="space-y-3">
                <div>
                  <p class="text-xs font-medium text-gray-600 mb-1">Cliente</p>
                  <p class="font-semibold text-black">{{ route.client?.name }}</p>
                  <p class="text-sm text-gray-600 mt-1 break-words">{{ route.client?.address }}</p>
                </div>
                <div class="flex gap-3 text-xs sm:text-sm">
                  <span class="text-black font-medium">{{ route.client?.phone }}</span>
                  <span class="text-gray-500">{{ route.client?.client_type }}</span>
                </div>
              </div>

              <button 
                @click="openCheckInModal(route)"
                class="w-full bg-black text-white px-4 py-2 rounded font-medium text-sm hover:bg-gray-900 transition-colors"
              >
                Ver detalles
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 3️⃣ ALERTAS MINIMALISTA -->
      <div v-if="activeTab === 'alerts'" class="space-y-6">
        <h2 class="text-2xl sm:text-3xl font-semibold text-black">Alertas</h2>

        <!-- FILTROS -->
        <div class="flex gap-2 pb-4 border-b border-gray-200">
          <button 
            v-for="filter in ['all', 'type1', 'type2']"
            :key="filter"
            @click="anomalyFilter = filter"
            :class="[
              'px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium rounded transition-all',
              anomalyFilter === filter 
                ? 'bg-black text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            {{ getFilterLabel(filter) }}
          </button>
        </div>

        <!-- TABLA MINIMALISTA -->
        <div class="border border-gray-200 rounded-lg overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700">Hora</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 hidden sm:table-cell">Vendedor</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700">Cliente</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700">Tipo</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 hidden md:table-cell">Distancia</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="alert in filteredAnomalies" 
                  :key="alert.visit_id"
                  class="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  <td class="px-4 py-3 text-gray-900 font-mono text-xs">{{ formatTime(alert.timestamp) }}</td>
                  <td class="px-4 py-3 text-gray-900 text-xs hidden sm:table-cell">{{ alert.seller }}</td>
                  <td class="px-4 py-3 text-gray-700 text-xs">{{ alert.client?.substring(0, 12) }}</td>
                  <td class="px-4 py-3">
                    <span class="text-xs font-medium">
                      {{ getAnomalyType(alert) === 'type1' ? '⚠ Fraude' : '○ Técnica' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-gray-600 text-xs hidden md:table-cell">
                    {{ alert.distance_meters?.toFixed(0) }}m
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="filteredAnomalies.length === 0" class="px-4 py-8 text-center text-gray-500 text-sm">
            Sin alertas
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL -->
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
import CheckInModal from '../components/CheckInModal.vue'

const API_URL = 'http://localhost:8000'

const activeTab = ref('dashboard')
const currentTime = ref('')

const tabs = [
  { id: 'dashboard', name: 'Resumen', icon: '—' },
  { id: 'routes', name: 'Rutas', icon: '◆' },
  { id: 'alerts', name: 'Alertas', icon: '!' }
]

const stats = ref({
  total_visits_today: 0,
  valid_checkins: 0,
  invalid_checkins: 0,
  fraud_detections: 0,
  quality_score: '0%'
})

const routes = ref([])
const anomalies = ref([])
const expandedRoutes = ref({})
const showCheckInModal = ref(false)
const selectedRoute = ref(null)
const anomalyFilter = ref('all')

const filteredAnomalies = computed(() => {
  return anomalies.value.filter(alert => {
    if (anomalyFilter.value === 'type1') {
      return getAnomalyType(alert) === 'type1'
    } else if (anomalyFilter.value === 'type2') {
      return getAnomalyType(alert) === 'type2'
    }
    return true
  })
})

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

const formatStatusShort = (status) => {
  const statuses = {
    'pending': '○',
    'in_progress': '→',
    'completed': '✓',
    'cancelled': '✕'
  }
  return statuses[status] || status
}

const toggleRouteExpanded = (routeId) => {
  expandedRoutes.value[routeId] = !expandedRoutes.value[routeId]
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

const getFilterLabel = (filter) => {
  const labels = {
    'all': 'Todas',
    'type1': '⚠ Fraude',
    'type2': '○ Técnica'
  }
  return labels[filter] || filter
}

const openCheckInModal = (route) => {
  selectedRoute.value = route
  showCheckInModal.value = true
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const loadDashboard = async () => {
  try {
    const response = await fetch(`${API_URL}/dashboard/stats/`)
    const data = await response.json()
    stats.value = data
  } catch (error) {
    console.error('Error:', error)
  }
}

const loadRoutes = async () => {
  try {
    const response = await fetch(`${API_URL}/routes/`)
    const data = await response.json()
    
    const now = new Date()
    const fiveDaysLater = new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000)
    
    routes.value = data.filter(route => {
      const routeDate = new Date(route.planned_date)
      return routeDate >= now && routeDate <= fiveDaysLater
    }).sort((a, b) => new Date(a.planned_date) - new Date(b.planned_date))
  } catch (error) {
    console.error('Error:', error)
  }
}

const loadAnomalies = async () => {
  try {
    const response = await fetch(`${API_URL}/dashboard/fraud-alerts/?hours=72`)
    const data = await response.json()
    anomalies.value = data.alerts || []
  } catch (error) {
    console.error('Error:', error)
  }
}

const onCheckInSuccess = () => {
  showCheckInModal.value = false
  loadDashboard()
  loadAnomalies()
  loadRoutes()
}

onMounted(() => {
  updateTime()
  setInterval(updateTime, 1000)
  
  loadDashboard()
  loadRoutes()
  loadAnomalies()
  
  setInterval(() => {
    loadDashboard()
    loadAnomalies()
  }, 30000)
})
</script>

<style scoped>
* {
  transition: color 0.2s, border-color 0.2s, background-color 0.2s;
}
</style>
