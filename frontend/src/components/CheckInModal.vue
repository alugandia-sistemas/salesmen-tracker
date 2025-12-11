<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <!-- HEADER -->
      <div class="bg-indigo-600 text-white px-6 py-4 flex items-center justify-between sticky top-0">
        <h2 class="text-2xl font-bold flex items-center gap-2">
          ✅ Check-in - Llegada al Cliente
        </h2>
        <button 
          @click="$emit('close')"
          class="text-white hover:bg-indigo-700 px-3 py-1 rounded font-bold text-xl"
        >
          ✕
        </button>
      </div>

      <div class="p-8 space-y-6">
        <!-- INFO DEL CLIENTE -->
        <div class="bg-indigo-50 rounded-lg p-6 border-2 border-indigo-200">
          <h3 class="text-lg font-bold text-gray-900 mb-4">📍 Cliente a Visitar</h3>
          <div class="space-y-2">
            <p><span class="font-semibold text-gray-700">Nombre:</span> <span class="text-gray-900 font-bold">{{ route.client?.name }}</span></p>
            <p><span class="font-semibold text-gray-700">Dirección:</span> <span class="text-gray-900">{{ route.client?.address }}</span></p>
            <p><span class="font-semibold text-gray-700">Teléfono:</span> <span class="text-gray-900 font-mono">{{ route.client?.phone }}</span></p>
            <p><span class="font-semibold text-gray-700">Tipo:</span> <span class="text-gray-900">{{ route.client?.client_type }}</span></p>
          </div>
        </div>

        <!-- CAPTURA DE UBICACIÓN GPS (REQUERIDA) -->
        <div class="bg-blue-50 rounded-lg p-6 border-2 border-blue-200">
          <h3 class="text-lg font-bold text-gray-900 mb-4">📡 Validar Ubicación GPS</h3>
          <p class="text-gray-700 text-sm mb-4">El sistema validará que estás dentro de 100 metros del cliente</p>
          
          <button 
            @click="captureLocation"
            :disabled="loadingLocation || locationCaptured"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2 mb-4"
          >
            {{ loadingLocation ? '⏳ Obteniendo ubicación...' : locationCaptured ? '✅ Ubicación validada' : '📍 Capturar GPS' }}
          </button>

          <div v-if="currentLocation" class="bg-white rounded-lg p-4 space-y-3 border border-blue-200">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-600 font-semibold">Latitud</p>
                <p class="text-lg font-mono text-gray-900">{{ currentLocation.latitude.toFixed(6) }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600 font-semibold">Longitud</p>
                <p class="text-lg font-mono text-gray-900">{{ currentLocation.longitude.toFixed(6) }}</p>
              </div>
            </div>
            <div>
              <p class="text-sm text-gray-600 font-semibold">Precisión</p>
              <p class="text-gray-900">± {{ currentLocation.accuracy.toFixed(0) }} metros</p>
            </div>
            
            <!-- DISTANCIA AL CLIENTE -->
            <div v-if="distanceToClient !== null" class="pt-3 border-t border-blue-200">
              <p class="text-sm text-gray-600 font-semibold mb-2">Distancia al Cliente</p>
              <div :class="[
                'text-center py-3 rounded-lg font-bold text-lg',
                distanceToClient <= 100 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              ]">
                {{ distanceToClient.toFixed(0) }} metros
                <span v-if="distanceToClient <= 100" class="text-2xl ml-2">✅</span>
                <span v-else class="text-2xl ml-2">⚠️ Muy lejos</span>
              </div>
            </div>
          </div>

          <div v-if="locationError" class="bg-red-100 border-2 border-red-500 text-red-800 p-4 rounded-lg mt-4">
            <p class="font-semibold">❌ Error: {{ locationError }}</p>
          </div>
        </div>

        <!-- CONFIRMACIÓN DE CLIENTE -->
        <div class="bg-green-50 rounded-lg p-6 border-2 border-green-200">
          <h3 class="text-lg font-bold text-gray-900 mb-4">✅ ¿Cliente Encontrado?</h3>
          <div class="space-y-3">
            <label class="flex items-center gap-3 cursor-pointer p-3 border-2 rounded-lg" :class="[
              clientFound === true ? 'border-green-500 bg-green-100' : 'border-gray-200'
            ]">
              <input 
                type="radio" 
                v-model="clientFound" 
                :value="true"
                class="w-5 h-5 cursor-pointer"
              />
              <span class="text-gray-900 font-semibold">Sí, cliente disponible</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer p-3 border-2 rounded-lg" :class="[
              clientFound === false ? 'border-red-500 bg-red-100' : 'border-gray-200'
            ]">
              <input 
                type="radio" 
                v-model="clientFound" 
                :value="false"
                class="w-5 h-5 cursor-pointer"
              />
              <span class="text-gray-900 font-semibold">No, cliente no disponible</span>
            </label>
          </div>
        </div>

        <!-- NOTAS -->
        <div>
          <h3 class="text-lg font-bold text-gray-900 mb-3">📝 Notas de Llegada</h3>
          <textarea 
            v-model="notes"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-indigo-600"
            rows="3"
            placeholder="Observaciones sobre el cliente, estado, próximos pasos..."
          />
        </div>

        <!-- BOTONES DE ACCIÓN -->
        <div class="flex gap-3 pt-4 border-t border-gray-200">
          <button 
            @click="$emit('close')"
            class="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-900 font-bold py-3 px-4 rounded-lg transition-colors"
          >
            Cancelar
          </button>
          <button 
            @click="submitCheckin"
            :disabled="!canSubmit"
            class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {{ submitting ? '⏳ Registrando...' : '✅ Confirmar Llegada' }}
          </button>
        </div>

        <!-- RESULTADO -->
        <div 
          v-if="result"
          :class="[
            'p-4 rounded-lg font-semibold border-2',
            result.success 
              ? 'bg-green-100 text-green-800 border-green-500' 
              : 'bg-red-100 text-red-800 border-red-500'
          ]"
        >
          {{ result.success ? '✅' : '❌' }} {{ result.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  route: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'success'])

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ============================================================================
// ESTADO REACTIVO
// ============================================================================

const currentLocation = ref(null)
const loadingLocation = ref(false)
const clientFound = ref(null)
const notes = ref('')
const submitting = ref(false)
const result = ref(null)
const locationError = ref(null)

// ============================================================================
// COMPUTED
// ============================================================================

const locationCaptured = computed(() => currentLocation.value !== null)

const distanceToClient = computed(() => {
  if (!currentLocation.value || !props.route.client) return null
  
  // Obtener coordenadas del cliente
  const lat2 = props.route.client.latitude
  const lng2 = props.route.client.longitude
  
  if (!lat2 || !lng2) {
    console.warn('Cliente sin coordenadas GPS')
    return null
  }
  
  // Calcular distancia usando Haversine
  const lat1 = currentLocation.value.latitude
  const lng1 = currentLocation.value.longitude
  
  const R = 6371000 // Radio de la Tierra en metros
  const phi1 = Math.radians(lat1)
  const phi2 = Math.radians(lat2)
  const delta_phi = Math.radians(lat2 - lat1)
  const delta_lambda = Math.radians(lng2 - lng1)
  
  const a = Math.sin(delta_phi / 2) ** 2 +
            Math.cos(phi1) * Math.cos(phi2) * Math.sin(delta_lambda / 2) ** 2
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  
  return R * c
})

const canSubmit = computed(() => {
  return (
    locationCaptured.value &&
    clientFound.value !== null &&
    distanceToClient.value !== null &&
    distanceToClient.value <= 100
  )
})

// ============================================================================
// FUNCIONES
// ============================================================================

const captureLocation = () => {
  if (!navigator.geolocation) {
    locationError.value = 'Geolocalización no disponible en este navegador'
    return
  }

  loadingLocation.value = true
  locationError.value = null
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      currentLocation.value = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        timestamp: new Date().toISOString()
      }
      loadingLocation.value = false
    },
    (error) => {
      console.error('❌ Error de geolocalización:', error.code, error.message)
      
      // Mensajes más específicos según el tipo de error
      let errorMessage = error.message || 'Error desconocido'
      if (error.code === error.PERMISSION_DENIED) {
        errorMessage = 'Permiso de ubicación denegado. Por favor, activa GPS en tu dispositivo.'
      } else if (error.code === error.POSITION_UNAVAILABLE) {
        errorMessage = 'GPS no disponible. Asegúrate de tener señal y GPS activado.'
      } else if (error.code === error.TIMEOUT) {
        errorMessage = 'Timeout al obtener GPS. Intenta en un lugar con mejor cobertura.'
      }
      
      locationError.value = errorMessage
      loadingLocation.value = false
    },
    {
      enableHighAccuracy: true,
      timeout: 30000,  // Increased from 10s to 30s for mobile
      maximumAge: 0
    }
  )
}

const submitCheckin = async () => {
  if (!canSubmit.value) return

  submitting.value = true
  
  try {
    const payload = {
      route_id: props.route.id,
      seller_id: props.route.seller_id,
      client_id: props.route.client_id,
      latitude: currentLocation.value.latitude,
      longitude: currentLocation.value.longitude,
      client_found: clientFound.value,
      notes: notes.value
    }

    console.log('📤 Enviando check-in a:', `${API_URL}/visits/checkin/`)
    console.log('📦 Payload:', payload)

    const response = await fetch(`${API_URL}/visits/checkin/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    console.log('📥 Response status:', response.status, response.statusText)
    const data = await response.json()
    console.log('📥 Response data:', data)
    
    if (response.ok) {
      result.value = {
        success: true,
        message: '✅ Check-in registrado - Ya estás en cliente'
      }
      
      setTimeout(() => {
        emit('success')
      }, 1500)
    } else {
      result.value = {
        success: false,
        message: `❌ Error: ${data.detail || 'Error en check-in'}`
      }
    }
  } catch (error) {
    console.error('❌ Error en submitCheckin:', error)
    result.value = {
      success: false,
      message: `❌ Error en comunicación: ${error.message}`
    }
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

Math.radians = function(degrees) {
  return degrees * (Math.PI / 180)
}
</script>

<style scoped>
* {
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
}
</style>
