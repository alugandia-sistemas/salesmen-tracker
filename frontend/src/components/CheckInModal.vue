<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <!-- HEADER -->
      <div class="bg-indigo-600 text-white px-6 py-4 flex items-center justify-between sticky top-0">
        <h2 class="text-2xl font-bold flex items-center gap-2">
          ✅ Check-in del Cliente
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

        <!-- CAPTURA DE UBICACIÓN GPS -->
        <div class="bg-blue-50 rounded-lg p-6 border-2 border-blue-200">
          <h3 class="text-lg font-bold text-gray-900 mb-4">📡 Ubicación GPS Actual</h3>
          
          <button 
            @click="captureLocation"
            :disabled="loadingLocation || locationCaptured"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2 mb-4"
          >
            {{ loadingLocation ? '⏳ Obteniendo ubicación...' : locationCaptured ? '✅ Ubicación capturada' : '📍 Capturar Ubicación GPS' }}
          </button>

          <div v-if="currentLocation" class="bg-white rounded-lg p-4 space-y-2 border border-blue-200">
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
            <div v-if="distanceToClient !== null" class="pt-2 border-t border-blue-200">
              <p class="text-sm text-gray-600 font-semibold">Distancia al Cliente</p>
              <p :class="[
                'text-lg font-bold',
                distanceToClient <= 100 ? 'text-green-600' : 'text-red-600'
              ]">
                {{ distanceToClient.toFixed(0) }} metros
                <span v-if="distanceToClient <= 100" class="text-green-600">✅</span>
                <span v-else class="text-red-600">⚠️ Demasiado lejos</span>
              </p>
            </div>
          </div>
        </div>

        <!-- CONFIRMACIÓN DE CLIENTE -->
        <div class="bg-green-50 rounded-lg p-6 border-2 border-green-200">
          <h3 class="text-lg font-bold text-gray-900 mb-4">✅ ¿Cliente Confirmado?</h3>
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
              <span class="text-gray-900 font-semibold">Sí, cliente encontrado y disponible</span>
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
          <h3 class="text-lg font-bold text-gray-900 mb-3">📝 Notas (Opcional)</h3>
          <textarea 
            v-model="notes"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-indigo-600"
            rows="4"
            placeholder="Anotaciones sobre la visita, comportamiento del cliente, próximos pasos, etc..."
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
            {{ submitting ? '⏳ Registrando...' : '✅ Confirmar Check-in' }}
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

const API_URL = 'http://localhost:8000'

// ============================================================================
// ESTADO REACTIVO
// ============================================================================

const currentLocation = ref(null)
const loadingLocation = ref(false)
const clientFound = ref(null)
const notes = ref('')
const submitting = ref(false)
const result = ref(null)

// ============================================================================
// COMPUTED
// ============================================================================

const locationCaptured = computed(() => currentLocation.value !== null)

const distanceToClient = computed(() => {
  if (!currentLocation.value || !props.route.client) return null
  
  // Calcular distancia usando Haversine
  const lat1 = currentLocation.value.latitude
  const lng1 = currentLocation.value.longitude
  const lat2 = props.route.client.latitude
  const lng2 = props.route.client.longitude
  
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

    const response = await fetch(`${API_URL}/visits/checkin/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    const data = await response.json()
    
    if (response.ok) {
      result.value = {
        success: true,
        message: '✅ Check-in registrado correctamente'
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
    console.error('Error:', error)
    result.value = {
      success: false,
      message: '❌ Error en comunicación con servidor'
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
