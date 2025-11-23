<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- HEADER -->
    <header class="bg-white shadow-lg border-b-4 border-indigo-600 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold text-lg">
            👤 AGENTE
          </div>
          <h1 class="text-2xl font-bold text-gray-800">Alugandia - Mi Panel</h1>
        </div>
        <div class="text-right">
          <p class="text-sm text-indigo-600 font-semibold">{{ currentUser?.name || 'Vendedor' }}</p>
          <p class="text-xs text-gray-500">{{ currentTime }}</p>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- TAB NAVIGATION -->
      <div class="flex gap-3 mb-8">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-6 py-3 font-semibold rounded-lg transition-all flex items-center gap-2',
            activeTab === tab.id 
              ? 'bg-indigo-600 text-white shadow-lg' 
              : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-indigo-600'
          ]"
        >
          {{ tab.icon }} {{ tab.name }}
        </button>
      </div>

      <!-- 1️⃣ DASHBOARD -->
      <div v-if="activeTab === 'dashboard'" class="space-y-6">
        <h2 class="text-3xl font-bold text-gray-800">📊 Mi Dashboard</h2>
        
        <!-- TARJETA DE USUARIO -->
        <div class="bg-gradient-to-r from-indigo-600 to-indigo-700 rounded-lg shadow-lg p-8 text-white">
          <p class="text-indigo-100 text-sm">Operador Activo</p>
          <p class="text-4xl font-bold mt-2">{{ currentUser?.name }}</p>
          <p class="text-indigo-200 mt-2">ID: {{ currentUser?.id?.substring(0, 8) }}...</p>
        </div>

        <!-- MÉTRICAS DE HOY -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <p class="text-gray-600 text-sm font-semibold">Visitas Realizadas</p>
            <p class="text-4xl font-bold text-blue-600 mt-2">{{ myStats.visits_today }}</p>
            <p class="text-xs text-gray-500 mt-2">Hoy</p>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <p class="text-gray-600 text-sm font-semibold">✅ Check-ins Válidos</p>
            <p class="text-4xl font-bold text-green-600 mt-2">{{ myStats.valid_checkins }}</p>
            <p class="text-xs text-gray-500 mt-2">Dentro de rango</p>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
            <p class="text-gray-600 text-sm font-semibold">⚠️ Pendientes</p>
            <p class="text-4xl font-bold text-orange-600 mt-2">{{ myStats.pending_routes }}</p>
            <p class="text-xs text-gray-500 mt-2">Rutas sin completar</p>
          </div>
        </div>

        <!-- PRÓXIMA RUTA IMPORTANTE -->
        <div v-if="nextRoute" class="bg-white rounded-lg shadow-lg p-8 border-l-4 border-indigo-600">
          <h3 class="text-lg font-bold text-gray-800 mb-4">📍 Próxima Ruta</h3>
          <div class="space-y-3">
            <div class="flex items-center gap-3">
              <span class="text-2xl">🕐</span>
              <div>
                <p class="text-gray-600 text-sm">Hora</p>
                <p class="text-lg font-bold text-gray-800">{{ nextRoute.planned_time }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-2xl">👤</span>
              <div>
                <p class="text-gray-600 text-sm">Cliente</p>
                <p class="text-lg font-bold text-gray-800">{{ nextRoute.client?.name }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-2xl">📍</span>
              <div>
                <p class="text-gray-600 text-sm">Dirección</p>
                <p class="text-sm text-gray-700">{{ nextRoute.client?.address }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2️⃣ MIS RUTAS -->
      <div v-if="activeTab === 'routes'" class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-3xl font-bold text-gray-800">🗓️ Mis Rutas - Próximos 5 Días</h2>
          <button 
            @click="loadMyRoutes"
            class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-semibold"
          >
            🔄 Recargar
          </button>
        </div>

        <div v-if="myRoutes.length === 0" class="bg-white rounded-lg p-12 text-center shadow-md">
          <p class="text-gray-500 text-xl">⏳ Sin rutas para los próximos 5 días</p>
        </div>

        <!-- LISTA DE RUTAS -->
        <div class="space-y-4">
          <div 
            v-for="route in myRoutes" 
            :key="route.id"
            class="bg-white rounded-lg shadow-md border-l-4 border-indigo-600 overflow-hidden hover:shadow-lg transition-shadow"
          >
            <!-- HEADER DE RUTA -->
            <div 
              @click="toggleRouteExpanded(route.id)"
              class="bg-gray-50 px-6 py-4 cursor-pointer hover:bg-gray-100 flex items-center justify-between border-b border-gray-200"
            >
              <div class="flex items-center gap-4 flex-1">
                <span class="text-2xl">{{ expandedRoutes[route.id] ? '▼' : '▶' }}</span>
                <div>
                  <p class="text-gray-900 font-bold text-lg">📅 {{ formatDateShort(route.planned_date) }}</p>
                  <p class="text-gray-600 text-sm">🕐 {{ route.planned_time }}</p>
                </div>
              </div>
              <div class="text-right">
                <span :class="[
                  'px-3 py-1 rounded-full text-sm font-semibold',
                  route.status === 'completed' ? 'bg-green-100 text-green-800' :
                  route.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                  route.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                ]">
                  {{ formatStatus(route.status) }}
                </span>
              </div>
            </div>

            <!-- CONTENIDO EXPANDIDO: CLIENTE -->
            <div v-if="expandedRoutes[route.id]" class="px-6 py-6 space-y-4 bg-gray-50 border-t border-gray-200">
              <!-- INFO DEL CLIENTE -->
              <div class="bg-white rounded-lg p-6 border-2 border-indigo-200">
                <div class="flex items-start gap-4">
                  <div class="text-4xl">📍</div>
                  <div class="flex-1">
                    <p class="text-gray-900 font-bold text-lg">{{ route.client?.name }}</p>
                    <p class="text-gray-600 mt-2">{{ route.client?.address }}</p>
                    <div class="flex gap-3 mt-4 flex-wrap">
                      <a 
                        :href="`tel:${route.client?.phone}`"
                        class="flex items-center gap-2 text-indigo-600 hover:text-indigo-800 font-semibold"
                      >
                        📞 {{ route.client?.phone }}
                      </a>
                      <span class="text-sm bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full">
                        {{ route.client?.client_type }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ESTADO DEL CHECK-IN -->
              <div v-if="getRouteVisit(route.id)" class="bg-green-50 rounded-lg p-4 border border-green-300">
                <p class="text-green-800 font-semibold">✅ Check-in ya registrado</p>
                <p class="text-green-700 text-sm mt-1">{{ formatTime(getRouteVisit(route.id).checkin_time) }}</p>
              </div>

              <!-- BOTÓN CHECK-IN -->
              <button 
                v-if="!getRouteVisit(route.id)"
                @click="openCheckInModal(route)"
                class="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white px-6 py-4 rounded-lg font-bold text-lg flex items-center justify-center gap-2 shadow-md"
              >
                ✅ Registrar Check-in Ahora
              </button>
              <button 
                v-else
                @click="openCheckOutModal(route)"
                class="w-full bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 text-white px-6 py-4 rounded-lg font-bold text-lg flex items-center justify-center gap-2 shadow-md"
              >
                🚪 Registrar Check-out
              </button>
            </div>
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

    <!-- MODAL CHECK-OUT -->
    <CheckOutModal 
      v-if="showCheckOutModal"
      :visit="selectedVisit"
      @close="showCheckOutModal = false"
      @success="onCheckOutSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CheckInModal from './components/CheckInModal.vue'
import CheckOutModal from './components/CheckOutModal.vue'

const API_URL = 'http://localhost:8000'

// ============================================================================
// ESTADO REACTIVO
// ============================================================================

const activeTab = ref('dashboard')
const currentTime = ref('')
const currentUser = ref(null)

const tabs = [
  { id: 'dashboard', name: 'Mi Dashboard', icon: '📊' },
  { id: 'routes', name: 'Mis Rutas', icon: '🗓️' }
]

const myStats = ref({
  visits_today: 0,
  valid_checkins: 0,
  pending_routes: 0
})

const myRoutes = ref([])
const allVisits = ref([])
const expandedRoutes = ref({})
const showCheckInModal = ref(false)
const showCheckOutModal = ref(false)
const selectedRoute = ref(null)
const selectedVisit = ref(null)

// ============================================================================
// COMPUTED
// ============================================================================

const nextRoute = computed(() => {
  if (myRoutes.value.length === 0) return null
  return myRoutes.value[0]
})

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

const formatDateShort = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleDateString('es-ES', { weekday: 'short', month: 'short', day: 'numeric' })
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

const getRouteVisit = (routeId) => {
  return allVisits.value.find(v => v.route_id === routeId && v.checkin_time)
}

const openCheckInModal = (route) => {
  selectedRoute.value = route
  showCheckInModal.value = true
}

const openCheckOutModal = (route) => {
  const visit = getRouteVisit(route.id)
  selectedVisit.value = visit
  selectedRoute.value = route
  showCheckOutModal.value = true
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

// ============================================================================
// CARGAR DATOS
// ============================================================================

const loadCurrentUser = async () => {
  try {
    const response = await fetch(`${API_URL}/sellers/`)
    const sellers = await response.json()
    
    if (sellers.length > 0) {
      currentUser.value = sellers[0]
    }
  } catch (error) {
    console.error('Error cargando usuario:', error)
  }
}

const loadMyRoutes = async () => {
  try {
    if (!currentUser.value?.id) {
      console.warn('Sin usuario actual')
      return
    }

    const response = await fetch(`${API_URL}/routes/?seller_id=${currentUser.value.id}`)
    const data = await response.json()
    
    // Filtrar rutas de los próximos 5 días
    const now = new Date()
    const fiveDaysLater = new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000)
    
    myRoutes.value = data.filter(route => {
      const routeDate = new Date(route.planned_date)
      return routeDate >= now && routeDate <= fiveDaysLater
    }).sort((a, b) => new Date(a.planned_date) - new Date(b.planned_date))

    // Cargar visitas de estas rutas
    await loadMyVisits()
  } catch (error) {
    console.error('Error cargando rutas:', error)
  }
}

const loadMyVisits = async () => {
  try {
    if (!currentUser.value?.id) return

    const response = await fetch(`${API_URL}/visits/?seller_id=${currentUser.value.id}`)
    const data = await response.json()
    allVisits.value = data || []

    // Calcular estadísticas
    const today = new Date().toDateString()
    const visitasHoy = allVisits.value.filter(v => 
      new Date(v.checkin_time).toDateString() === today
    )
    
    myStats.value = {
      visits_today: visitasHoy.length,
      valid_checkins: visitasHoy.filter(v => v.checkin_is_valid).length,
      pending_routes: myRoutes.value.filter(r => r.status === 'pending').length
    }
  } catch (error) {
    console.error('Error cargando visitas:', error)
  }
}

const onCheckInSuccess = () => {
  showCheckInModal.value = false
  loadMyRoutes()
}

const onCheckOutSuccess = () => {
  showCheckOutModal.value = false
  loadMyRoutes()
}

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(async () => {
  updateTime()
  setInterval(updateTime, 1000)
  
  await loadCurrentUser()
  await loadMyRoutes()
  
  // Recargar cada 30 segundos
  setInterval(loadMyRoutes, 30000)
})
</script>

<style scoped>
* {
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
}
</style>
