<template>
  <div class="min-h-screen bg-white">
    <!-- HEADER MINIMALISTA -->
    <header class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="px-3 sm:px-4 py-4 sm:py-5">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-10 h-10 bg-black rounded-lg flex items-center justify-center text-white text-xs font-bold">
              SV
            </div>
            <h1 class="text-lg sm:text-xl font-semibold text-black truncate">Alugandia</h1>
          </div>
          <div class="text-right text-xs sm:text-sm">
            <p class="text-black font-medium">{{ currentUser?.name || 'Vendedor' }}</p>
            <p class="text-gray-500 text-xs hidden sm:block">{{ currentTime }}</p>
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
        <div>
          <h2 class="text-2xl sm:text-3xl font-semibold text-black mb-6">Resumen</h2>
          
          <!-- TARJETA DE USUARIO MINIMALISTA -->
          <div class="bg-black text-white rounded-lg p-6 sm:p-8 mb-8">
            <p class="text-gray-400 text-sm font-medium mb-2">Operador</p>
            <p class="text-2xl sm:text-3xl font-semibold">{{ currentUser?.name }}</p>
            <p class="text-gray-500 text-xs mt-3">ID: {{ currentUser?.id?.substring(0, 8) }}...</p>
          </div>

          <!-- MÉTRICAS MINIMALISTAS - GRID -->
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8">
            <div class="border border-gray-200 rounded-lg p-4 sm:p-6 hover:border-gray-300 transition-colors">
              <p class="text-gray-600 text-xs sm:text-sm font-medium mb-3">Visitas hoy</p>
              <p class="text-3xl sm:text-4xl font-semibold text-black">{{ myStats.visits_today }}</p>
            </div>

            <div class="border border-gray-200 rounded-lg p-4 sm:p-6 hover:border-gray-300 transition-colors">
              <p class="text-gray-600 text-xs sm:text-sm font-medium mb-3">Completadas</p>
              <p class="text-3xl sm:text-4xl font-semibold text-black">{{ myStats.completed_visits }}</p>
            </div>

            <div class="border border-gray-200 rounded-lg p-4 sm:p-6 hover:border-gray-300 transition-colors">
              <p class="text-gray-600 text-xs sm:text-sm font-medium mb-3">Pendientes</p>
              <p class="text-3xl sm:text-4xl font-semibold text-black">{{ myStats.pending_routes }}</p>
            </div>
          </div>

          <!-- PRÓXIMA RUTA MINIMALISTA -->
          <div v-if="nextRoute" class="bg-gray-50 rounded-lg p-6 sm:p-8 border border-gray-200">
            <h3 class="text-sm font-medium text-gray-600 mb-4">Próxima ruta</h3>
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <span class="text-gray-400">→</span>
                <div class="min-w-0">
                  <p class="text-xs text-gray-500">Hora</p>
                  <p class="font-semibold text-black">{{ nextRoute.planned_time }}</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-gray-400">◆</span>
                <div class="min-w-0">
                  <p class="text-xs text-gray-500">Cliente</p>
                  <p class="font-semibold text-black truncate">{{ nextRoute.client?.name }}</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-gray-400">◎</span>
                <div class="min-w-0">
                  <p class="text-xs text-gray-500">Dirección</p>
                  <p class="text-sm text-gray-700 break-words">{{ nextRoute.client?.address }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2️⃣ MIS RUTAS MINIMALISTA -->
      <div v-if="activeTab === 'routes'" class="space-y-6">
        <div class="flex items-center justify-between gap-2">
          <h2 class="text-2xl sm:text-3xl font-semibold text-black">Próximas rutas</h2>
          <button 
            @click="loadMyRoutes"
            class="text-black hover:text-gray-600 p-2"
            title="Recargar"
          >
            ↻
          </button>
        </div>

        <div v-if="myRoutes.length === 0" class="text-center py-12">
          <p class="text-gray-500">Sin rutas próximas</p>
        </div>

        <!-- LISTA DE RUTAS MINIMALISTA -->
        <div class="space-y-3">
          <div 
            v-for="route in myRoutes" 
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
                  <p class="font-medium text-black text-sm sm:text-base truncate">{{ formatDateShort(route.planned_date) }}</p>
                  <p class="text-xs sm:text-sm text-gray-500">{{ route.planned_time }}</p>
                </div>
              </div>
              <span :class="[
                'px-2 sm:px-3 py-1 rounded text-xs font-medium flex-shrink-0',
                getRouteVisit(route.id) 
                  ? 'bg-gray-100 text-gray-700' 
                  : 'bg-gray-100 text-gray-700'
              ]">
                {{ getRouteVisit(route.id) ? '✓' : '○' }}
              </span>
            </div>

            <!-- CONTENIDO EXPANDIDO -->
            <div v-if="expandedRoutes[route.id]" class="px-4 sm:px-6 py-4 space-y-4 bg-gray-50 border-t border-gray-100">
              <!-- INFO CLIENTE -->
              <div class="space-y-3">
                <div>
                  <p class="text-xs font-medium text-gray-600 mb-1">Cliente</p>
                  <p class="font-semibold text-black">{{ route.client?.name }}</p>
                  <p class="text-sm text-gray-600 mt-1 break-words">{{ route.client?.address }}</p>
                </div>
                <div class="flex gap-3 text-xs sm:text-sm">
                  <a 
                    :href="`tel:${route.client?.phone}`"
                    class="text-black hover:text-gray-600 underline"
                  >
                    {{ route.client?.phone }}
                  </a>
                  <span class="text-gray-500">{{ route.client?.client_type }}</span>
                </div>
              </div>

              <!-- ESTADO -->
              <div v-if="getRouteVisit(route.id)" class="bg-white border border-gray-200 rounded p-3 text-xs">
                <p class="text-gray-700"><span class="font-semibold">Check-in:</span> {{ formatTime(getRouteVisit(route.id).checkin_time) }}</p>
                <p v-if="getRouteVisit(route.id).checkin_distance_meters" class="text-gray-600 mt-1">
                  Distancia: {{ getRouteVisit(route.id).checkin_distance_meters.toFixed(0) }}m
                </p>
              </div>

              <!-- BOTONES -->
              <div v-if="!getRouteVisit(route.id)" class="pt-2">
                <button 
                  @click="openCheckInModal(route)"
                  class="w-full bg-black text-white px-4 py-2 rounded font-medium text-sm hover:bg-gray-900 transition-colors"
                >
                  Registrar llegada
                </button>
              </div>

              <div v-else class="pt-2">
                <button 
                  @click="completeRoute(route.id)"
                  class="w-full bg-gray-900 text-white px-4 py-2 rounded font-medium text-sm hover:bg-black transition-colors"
                >
                  Marcar completado
                </button>
              </div>
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

    <!-- NOTIFICACIÓN MINIMALISTA -->
    <div 
      v-if="showSuccessNotification"
      class="fixed bottom-4 left-4 right-4 sm:bottom-4 sm:right-4 sm:left-auto sm:w-80 bg-black text-white px-4 py-3 rounded text-sm z-50 flex items-center gap-2"
    >
      ✓ {{ successMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CheckInModal from '../components/CheckInModal.vue'

const API_URL = 'http://localhost:8000'

const activeTab = ref('dashboard')
const currentTime = ref('')
const currentUser = ref(null)

const tabs = [
  { id: 'dashboard', name: 'Resumen', icon: '—' },
  { id: 'routes', name: 'Rutas', icon: '◆' }
]

const myStats = ref({
  visits_today: 0,
  completed_visits: 0,
  pending_routes: 0
})

const myRoutes = ref([])
const allVisits = ref([])
const expandedRoutes = ref({})
const showCheckInModal = ref(false)
const selectedRoute = ref(null)
const showSuccessNotification = ref(false)
const successMessage = ref('')

const nextRoute = computed(() => {
  if (myRoutes.value.length === 0) return null
  return myRoutes.value[0]
})

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

const formatDateShort = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleDateString('es-ES', { weekday: 'short', month: 'short', day: 'numeric' })
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

const completeRoute = async (routeId) => {
  try {
    const response = await fetch(`${API_URL}/routes/${routeId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'completed' })
    })

    if (response.ok) {
      showSuccessNotification.value = true
      successMessage.value = 'Ruta marcada como completada'
      setTimeout(() => {
        showSuccessNotification.value = false
      }, 3000)
      
      await loadMyRoutes()
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const loadCurrentUser = async () => {
  try {
    const response = await fetch(`${API_URL}/sellers/`)
    const sellers = await response.json()
    if (sellers.length > 0) {
      currentUser.value = sellers[0]
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const loadMyRoutes = async () => {
  try {
    if (!currentUser.value?.id) return

    const response = await fetch(`${API_URL}/routes/?seller_id=${currentUser.value.id}`)
    const data = await response.json()
    
    const now = new Date()
    const fiveDaysLater = new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000)
    
    myRoutes.value = data.filter(route => {
      const routeDate = new Date(route.planned_date)
      return routeDate >= now && routeDate <= fiveDaysLater
    }).sort((a, b) => new Date(a.planned_date) - new Date(b.planned_date))

    await loadMyVisits()
  } catch (error) {
    console.error('Error:', error)
  }
}

const loadMyVisits = async () => {
  try {
    if (!currentUser.value?.id) return

    const response = await fetch(`${API_URL}/visits/?seller_id=${currentUser.value.id}`)
    const data = await response.json()
    allVisits.value = data || []

    const today = new Date().toDateString()
    const visitasHoy = allVisits.value.filter(v => 
      new Date(v.checkin_time).toDateString() === today
    )
    
    myStats.value = {
      visits_today: visitasHoy.length,
      completed_visits: visitasHoy.filter(v => v.checkin_is_valid).length,
      pending_routes: myRoutes.value.filter(r => !getRouteVisit(r.id)).length
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const onCheckInSuccess = () => {
  showCheckInModal.value = false
  showSuccessNotification.value = true
  successMessage.value = 'Check-in registrado'
  
  setTimeout(() => {
    showSuccessNotification.value = false
  }, 3000)
  
  loadMyRoutes()
}

onMounted(async () => {
  updateTime()
  setInterval(updateTime, 1000)
  
  await loadCurrentUser()
  await loadMyRoutes()
  
  setInterval(loadMyRoutes, 30000)
})
</script>

<style scoped>
* {
  transition: color 0.2s, border-color 0.2s, background-color 0.2s;
}

@media (max-width: 640px) {
  :deep(input), :deep(textarea), :deep(select) {
    font-size: 16px;
  }
}
</style>
