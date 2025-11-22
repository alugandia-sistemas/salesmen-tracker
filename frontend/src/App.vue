<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- HEADER -->
    <header class="bg-white shadow-md border-b-4 border-indigo-600">
      <div class="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold">
            📍 ALUGANDIA
          </div>
          <h1 class="text-2xl font-bold text-gray-800">Salesmen Tracker</h1>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-600">{{ currentUser?.name || 'Vendedor' }}</p>
          <p class="text-xs text-gray-500">{{ currentTime }}</p>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- TAB NAVIGATION -->
      <div class="flex gap-2 mb-8 border-b-2 border-gray-200">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-6 py-3 font-semibold border-b-4 transition-all',
            activeTab === tab.id 
              ? 'border-indigo-600 text-indigo-600' 
              : 'border-transparent text-gray-600 hover:text-indigo-600'
          ]"
        >
          {{ tab.icon }} {{ tab.name }}
        </button>
      </div>

      <!-- 1️⃣ TAB: DASHBOARD (VISIÓN GENERAL) -->
      <div v-if="activeTab === 'dashboard'" class="space-y-6">
        <h2 class="text-2xl font-bold text-gray-800">Dashboard de Control</h2>
        
        <!-- TARJETAS DE MÉTRICAS -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <p class="text-gray-600 text-sm">Visitas Hoy</p>
            <p class="text-3xl font-bold text-blue-600">{{ stats.total_visits_today }}</p>
            <p class="text-xs text-gray-500 mt-2">Total del día</p>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <p class="text-gray-600 text-sm">✅ Check-ins Válidos</p>
            <p class="text-3xl font-bold text-green-600">{{ stats.valid_checkins }}</p>
            <p class="text-xs text-gray-500 mt-2">Dentro del rango</p>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
            <p class="text-gray-600 text-sm">⚠️ Fuera de Rango</p>
            <p class="text-3xl font-bold text-red-600">{{ stats.invalid_checkins }}</p>
            <p class="text-xs text-gray-500 mt-2">Ubicación inválida</p>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
            <p class="text-gray-600 text-sm">🚨 Fraudes Detectados</p>
            <p class="text-3xl font-bold text-orange-600">{{ stats.fraud_detections }}</p>
            <p class="text-xs text-gray-500 mt-2">Esta semana</p>
          </div>
        </div>

        <!-- CALIDAD DE DATOS -->
        <div class="bg-white rounded-lg shadow-md p-8">
          <h3 class="text-xl font-bold text-gray-800 mb-4">Indicador de Calidad</h3>
          <div class="flex items-center gap-8">
            <div>
              <div class="text-6xl font-bold text-indigo-600">{{ stats.quality_score }}</div>
              <p class="text-gray-600 mt-2">Precisión de datos comerciales</p>
            </div>
            <div class="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
              <div 
                class="h-full bg-gradient-to-r from-green-500 to-indigo-600 transition-all"
                :style="{ width: stats.quality_score }"
              />
            </div>
          </div>
          <p class="text-sm text-gray-500 mt-4">
            {{stats.quality_score >= 90 ? '✅ Excelente integridad de datos' : '⚠️ Revisar validaciones'}}
          </p>
        </div>
      </div>

      <!-- 2️⃣ TAB: ALERTAS DE FRAUDE (PARA GERENCIA) -->
      <div v-if="activeTab === 'fraud-alerts'" class="space-y-6">
        <h2 class="text-2xl font-bold text-gray-800">🚨 Alertas de Fraude y Anomalías</h2>
        
        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
          <p class="text-yellow-800 font-semibold">
            Monitoreo automático de visitas sospechosas
          </p>
          <p class="text-yellow-700 text-sm">
            Se detectan automáticamente: ubicaciones falsas, check-ins duplicados, múltiples ubicaciones en segundos, fuera de horario
          </p>
        </div>

        <!-- TABLA DE ALERTAS -->
        <div class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-red-50 border-b-2 border-red-200">
                <tr>
                  <th class="px-6 py-3 text-left text-red-800 font-bold">Timestamp</th>
                  <th class="px-6 py-3 text-left text-red-800 font-bold">Vendedor</th>
                  <th class="px-6 py-3 text-left text-red-800 font-bold">Cliente</th>
                  <th class="px-6 py-3 text-left text-red-800 font-bold">Distancia</th>
                  <th class="px-6 py-3 text-left text-red-800 font-bold">Flags de Fraude</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="alert in fraudAlerts" 
                  :key="alert.visit_id"
                  class="border-b border-gray-200 hover:bg-red-50 transition-colors"
                >
                  <td class="px-6 py-4 text-gray-700 font-mono text-xs">
                    {{ formatTime(alert.timestamp) }}
                  </td>
                  <td class="px-6 py-4 text-gray-900 font-semibold">{{ alert.seller }}</td>
                  <td class="px-6 py-4 text-gray-700">{{ alert.client }}</td>
                  <td class="px-6 py-4">
                    <span class="bg-red-100 text-red-800 px-3 py-1 rounded-full font-mono">
                      {{ alert.distance_meters.toFixed(0) }}m
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex flex-wrap gap-2">
                      <span 
                        v-for="flag in alert.fraud_flags" 
                        :key="flag"
                        class="bg-orange-100 text-orange-800 px-2 py-1 rounded text-xs font-semibold"
                      >
                        {{ flag }}
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="px-6 py-4 bg-gray-50 text-center text-gray-600 text-sm" v-if="fraudAlerts.length === 0">
            ✅ Sin alertas de fraude en las últimas 24 horas
          </div>
        </div>
      </div>

      <!-- 3️⃣ TAB: CHECK-IN/CHECK-OUT (FUNCIONALIDAD PRINCIPAL) -->
      <div v-if="activeTab === 'checkin'" class="space-y-6 max-w-2xl mx-auto">
        <h2 class="text-2xl font-bold text-gray-800">📍 Check-in del Cliente</h2>

        <!-- FORMULARIO CHECK-IN -->
        <div class="bg-white rounded-lg shadow-lg p-8 space-y-6">
          
          <!-- Selector de Ruta -->
          <div>
            <label class="block text-gray-700 font-bold mb-2">Ruta Programada</label>
            <select 
              v-model="checkinForm.route_id"
              class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-indigo-600"
            >
              <option value="">Seleccionar ruta...</option>
              <option v-for="route in routes" :key="route.id" :value="route.id">
                {{ route.client_name }} - {{ route.planned_time }}
              </option>
            </select>
          </div>

          <!-- UBICACIÓN GPS -->
          <div class="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 space-y-4">
            <h3 class="font-bold text-blue-900 flex items-center gap-2">
              📡 Ubicación GPS Actual
            </h3>
            
            <button 
              @click="captureLocation"
              :disabled="loadingLocation"
              class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {{ loadingLocation ? '⏳ Obteniendo ubicación...' : '📍 Capturar Ubicación GPS' }}
            </button>

            <div v-if="currentLocation" class="bg-white rounded p-4 space-y-2">
              <p class="text-sm text-gray-700">
                <span class="font-semibold">Latitud:</span> 
                <span class="font-mono">{{ currentLocation.latitude.toFixed(6) }}</span>
              </p>
              <p class="text-sm text-gray-700">
                <span class="font-semibold">Longitud:</span> 
                <span class="font-mono">{{ currentLocation.longitude.toFixed(6) }}</span>
              </p>
              <p class="text-sm text-gray-700">
                <span class="font-semibold">Precisión:</span> 
                <span class="font-mono">± {{ currentLocation.accuracy.toFixed(0) }}m</span>
              </p>
              <p class="text-xs text-gray-500 mt-4">
                Ubicación capturada a: {{ formatTime(currentLocation.timestamp) }}
              </p>
            </div>

            <div v-else class="text-center py-4 text-gray-500">
              ⏳ Esperando ubicación GPS...
            </div>
          </div>

          <!-- FOTO GEOETIQUETADA (Prueba Visual) -->
          <div class="bg-purple-50 border-2 border-purple-200 rounded-lg p-6 space-y-4">
            <h3 class="font-bold text-purple-900 flex items-center gap-2">
              📸 Foto Geoetiquetada (Prueba Visual)
            </h3>
            
            <input 
              type="file" 
              accept="image/*"
              @change="selectPhoto"
              class="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:outline-none focus:border-purple-600"
            />

            <div v-if="photoPreview" class="text-center">
              <img :src="photoPreview" alt="preview" class="max-w-xs mx-auto rounded-lg shadow">
              <p class="text-sm text-gray-600 mt-2">📸 Foto seleccionada</p>
            </div>
          </div>

          <!-- CONFIRMACIÓN MANUAL (Anti-fraude) -->
          <div class="bg-green-50 border-2 border-green-200 rounded-lg p-6 space-y-4">
            <h3 class="font-bold text-green-900 flex items-center gap-2">
              ✅ Confirmación del Cliente
            </h3>
            <p class="text-sm text-green-800">
              Por favor, confirma que el cliente se encuentra en la ubicación indicada
            </p>
            
            <div class="flex gap-4">
              <label class="flex items-center gap-2 cursor-pointer">
                <input 
                  type="radio" 
                  v-model="checkinForm.client_found"
                  :value="true"
                  class="w-4 h-4"
                />
                <span class="text-gray-700 font-semibold">✅ Sí, cliente ubicado</span>
              </label>
              
              <label class="flex items-center gap-2 cursor-pointer">
                <input 
                  type="radio" 
                  v-model="checkinForm.client_found"
                  :value="false"
                  class="w-4 h-4"
                />
                <span class="text-gray-700 font-semibold">❌ No, cliente no encontrado</span>
              </label>
            </div>
          </div>

          <!-- NOTAS ADICIONALES -->
          <div>
            <label class="block text-gray-700 font-bold mb-2">Notas (Opcional)</label>
            <textarea 
              v-model="checkinForm.notes"
              placeholder="Ej: Cliente fuera de oficina, dejar en recepción..."
              class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-indigo-600 resize-none"
              rows="3"
            />
          </div>

          <!-- BOTÓN ENVIAR CHECK-IN -->
          <button 
            @click="submitCheckin"
            :disabled="!canSubmitCheckin"
            class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-bold py-4 px-6 rounded-lg transition-colors text-lg flex items-center justify-center gap-2"
          >
            {{ submittingCheckin ? '⏳ Enviando...' : '🚀 Registrar Check-in' }}
          </button>
        </div>

        <!-- RESULTADO CHECK-IN -->
        <div v-if="checkinResult" :class="[
          'rounded-lg p-6 border-l-4',
          checkinResult.success ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'
        ]">
          <h3 class="font-bold text-lg mb-4">
            {{ checkinResult.success ? '✅ Check-in Registrado' : '❌ Error en Check-in' }}
          </h3>
          
          <div class="space-y-2 text-sm">
            <p v-if="checkinResult.distance_meters">
              <span class="font-semibold">Distancia al cliente:</span>
              <span class="font-mono">{{ checkinResult.distance_meters.toFixed(1) }}m</span>
            </p>
            
            <p v-if="checkinResult.is_valid" class="text-green-700 font-semibold">
              ✅ Ubicación válida (dentro de 100m)
            </p>
            
            <p v-if="!checkinResult.is_valid && checkinResult.validation_error" class="text-red-700 font-semibold">
              ⚠️ {{ checkinResult.validation_error }}
            </p>
            
            <div v-if="checkinResult.fraud_flags && checkinResult.fraud_flags.length > 0">
              <p class="font-semibold text-orange-700">Flags detectados:</p>
              <div class="flex flex-wrap gap-2 mt-2">
                <span 
                  v-for="flag in checkinResult.fraud_flags" 
                  :key="flag"
                  class="bg-orange-100 text-orange-800 px-2 py-1 rounded text-xs font-mono"
                >
                  {{ flag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 4️⃣ TAB: RUTAS Y VISITAS -->
      <div v-if="activeTab === 'routes'" class="space-y-6">
        <h2 class="text-2xl font-bold text-gray-800">📋 Rutas y Visitas</h2>
        
        <div class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-indigo-600 text-white">
                <tr>
                  <th class="px-6 py-3 text-left">Cliente</th>
                  <th class="px-6 py-3 text-left">Fecha Programada</th>
                  <th class="px-6 py-3 text-left">Estado</th>
                  <th class="px-6 py-3 text-left">Check-in</th>
                  <th class="px-6 py-3 text-left">Distancia</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="route in routes" :key="route.id" class="border-b border-gray-200">
                  <td class="px-6 py-4 font-semibold text-gray-900">{{ route.client_name }}</td>
                  <td class="px-6 py-4 text-gray-700">{{ formatDate(route.planned_date) }}</td>
                  <td class="px-6 py-4">
                    <span :class="[
                      'px-3 py-1 rounded-full text-xs font-bold',
                      route.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    ]">
                      {{ route.status === 'completed' ? '✅ Completada' : '⏳ Pendiente' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    {{ route.checkin_time ? formatTime(route.checkin_time) : '-' }}
                  </td>
                  <td class="px-6 py-4 font-mono">
                    {{ route.distance ? `${route.distance.toFixed(0)}m` : '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// STATE
const activeTab = ref('dashboard')
const currentUser = ref({ name: 'Jose Manuel' })
const currentTime = ref('')
const currentLocation = ref(null)
const loadingLocation = ref(false)
const selectedPhoto = ref(null)
const photoPreview = ref(null)
const submittingCheckin = ref(false)

// FORMULARIO CHECK-IN
const checkinForm = ref({
  route_id: '',
  seller_id: 'seller-1',
  client_id: '',
  latitude: null,
  longitude: null,
  client_found: null,
  notes: ''
})

const checkinResult = ref(null)

// DATOS DESDE API
const stats = ref({
  total_visits_today: 0,
  valid_checkins: 0,
  invalid_checkins: 0,
  fraud_detections: 0,
  average_distance_meters: 0,
  quality_score: '0%'
})

const fraudAlerts = ref([])
const routes = ref([])

// TABS
const tabs = [
  { id: 'dashboard', name: 'Dashboard', icon: '📊' },
  { id: 'fraud-alerts', name: 'Alertas', icon: '🚨' },
  { id: 'checkin', name: 'Check-in', icon: '📍' },
  { id: 'routes', name: 'Rutas', icon: '📋' }
]

// CONFIG API
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ============================================================================
// FUNCIONES AUXILIARES
// ============================================================================

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// Actualizar hora actual
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

// ============================================================================
// GEOLOCALIZACIÓN
// ============================================================================

const captureLocation = () => {
  if (!navigator.geolocation) {
    alert('❌ Geolocalización no disponible en este navegador')
    return
  }

  loadingLocation.value = true
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      currentLocation.value = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        timestamp: new Date().toISOString()
      }
      
      checkinForm.value.latitude = position.coords.latitude
      checkinForm.value.longitude = position.coords.longitude
      
      loadingLocation.value = false
    },
    (error) => {
      console.error('Error de geolocalización:', error)
      alert(`❌ Error: ${error.message}`)
      loadingLocation.value = false
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    }
  )
}

// ============================================================================
// FOTO
// ============================================================================

const selectPhoto = (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  selectedPhoto.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    photoPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

// ============================================================================
// CHECK-IN
// ============================================================================

const canSubmitCheckin = computed(() => {
  return (
    checkinForm.value.route_id &&
    currentLocation.value &&
    checkinForm.value.client_found !== null
  )
})

const submitCheckin = async () => {
  if (!canSubmitCheckin.value) return

  submittingCheckin.value = true
  
  try {
    const formData = new FormData()
    formData.append('request', JSON.stringify({
      route_id: checkinForm.value.route_id,
      seller_id: checkinForm.value.seller_id,
      client_id: 'client-1', // Extraer desde ruta seleccionada
      latitude: checkinForm.value.latitude,
      longitude: checkinForm.value.longitude,
      client_found: checkinForm.value.client_found,
      notes: checkinForm.value.notes
    }))
    
    if (selectedPhoto.value) {
      formData.append('photo', selectedPhoto.value)
    }

    const response = await fetch(`${API_URL}/visits/checkin/`, {
      method: 'POST',
      body: formData
    })

    const data = await response.json()
    
    if (response.ok) {
      checkinResult.value = {
        ...data,
        success: true
      }
      
      // Limpiar formulario
      setTimeout(() => {
        checkinForm.value = {
          route_id: '',
          seller_id: 'seller-1',
          client_id: '',
          latitude: null,
          longitude: null,
          client_found: null,
          notes: ''
        }
        selectedPhoto.value = null
        photoPreview.value = null
        currentLocation.value = null
      }, 2000)
    } else {
      checkinResult.value = {
        success: false,
        message: data.detail || 'Error en check-in'
      }
    }
  } catch (error) {
    console.error('Error:', error)
    checkinResult.value = {
      success: false,
      message: '❌ Error en comunicación con servidor'
    }
  } finally {
    submittingCheckin.value = false
  }
}

// ============================================================================
// CARGAR DATOS INICIALES
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

const loadFraudAlerts = async () => {
  try {
    const response = await fetch(`${API_URL}/dashboard/fraud-alerts/?hours=24`)
    const data = await response.json()
    fraudAlerts.value = data.alerts
  } catch (error) {
    console.error('Error cargando alertas:', error)
  }
}

const loadRoutes = async () => {
  try {
    const response = await fetch(`${API_URL}/routes/?seller_id=seller-1`)
    const data = await response.json()
    routes.value = data
  } catch (error) {
    console.error('Error cargando rutas:', error)
  }
}

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(() => {
  updateTime()
  setInterval(updateTime, 1000)
  
  loadDashboard()
  loadFraudAlerts()
  loadRoutes()
  
  // Recargar datos cada 30 segundos
  setInterval(loadDashboard, 30000)
  setInterval(loadFraudAlerts, 30000)
})
</script>

<style scoped>
/* Smooth transitions */
* {
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
}

/* Tabla mejorada */
table tbody tr:hover {
  background-color: rgba(99, 102, 241, 0.05);
}
</style>
