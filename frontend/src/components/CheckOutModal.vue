<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <!-- HEADER -->
      <div class="bg-orange-600 text-white px-6 py-4 flex items-center justify-between sticky top-0">
        <h2 class="text-2xl font-bold flex items-center gap-2">
          🚪 Check-out del Cliente
        </h2>
        <button 
          @click="$emit('close')"
          class="text-white hover:bg-orange-700 px-3 py-1 rounded font-bold text-xl"
        >
          ✕
        </button>
      </div>

      <div class="p-8 space-y-6">
        <!-- INFO DE VISITA PREVIA -->
        <div class="bg-orange-50 rounded-lg p-6 border-2 border-orange-200">
          <h3 class="text-lg font-bold text-gray-900 mb-4">📋 Información de Visita</h3>
          <div class="space-y-2">
            <p><span class="font-semibold text-gray-700">Cliente:</span> <span class="text-gray-900 font-bold">{{ visit?.client?.name }}</span></p>
            <p><span class="font-semibold text-gray-700">Check-in registrado:</span> <span class="text-gray-900">{{ formatTime(visit?.checkin_time) }}</span></p>
            <p><span class="font-semibold text-gray-700">Tiempo en sitio:</span> <span class="text-gray-900 font-bold">{{ timeInSite }}</span></p>
          </div>
        </div>

        <!-- CAPTURA DE UBICACIÓN GPS -->
        <div class="bg-blue-50 rounded-lg p-6 border-2 border-blue-200">
          <h3 class="text-lg font-bold text-gray-900 mb-4">📡 Ubicación GPS al Salir</h3>
          
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
          </div>
        </div>

        <!-- RESULTADO DE VISITA -->
        <div class="bg-purple-50 rounded-lg p-6 border-2 border-purple-200">
          <h3 class="text-lg font-bold text-gray-900 mb-4">📊 Resultado de Visita</h3>
          <div class="space-y-3">
            <label class="flex items-center gap-3 cursor-pointer p-3 border-2 rounded-lg" :class="[
              visitResult === 'success' ? 'border-green-500 bg-green-100' : 'border-gray-200'
            ]">
              <input 
                type="radio" 
                v-model="visitResult" 
                value="success"
                class="w-5 h-5 cursor-pointer"
              />
              <span class="text-gray-900 font-semibold">✅ Visita exitosa - Cerrado positivo</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer p-3 border-2 rounded-lg" :class="[
              visitResult === 'pending' ? 'border-yellow-500 bg-yellow-100' : 'border-gray-200'
            ]">
              <input 
                type="radio" 
                v-model="visitResult" 
                value="pending"
                class="w-5 h-5 cursor-pointer"
              />
              <span class="text-gray-900 font-semibold">⏳ Requiere seguimiento</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer p-3 border-2 rounded-lg" :class="[
              visitResult === 'cancelled' ? 'border-red-500 bg-red-100' : 'border-gray-200'
            ]">
              <input 
                type="radio" 
                v-model="visitResult" 
                value="cancelled"
                class="w-5 h-5 cursor-pointer"
              />
              <span class="text-gray-900 font-semibold">❌ Cancelado - Cliente no disponible</span>
            </label>
          </div>
        </div>

        <!-- NOTAS -->
        <div>
          <h3 class="text-lg font-bold text-gray-900 mb-3">📝 Observaciones (Opcional)</h3>
          <textarea 
            v-model="notes"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-orange-600"
            rows="4"
            placeholder="Resumen de la visita, puntos clave, próximas acciones, observaciones importantes..."
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
            @click="submitCheckout"
            :disabled="!canSubmit"
            class="flex-1 bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {{ submitting ? '⏳ Registrando...' : '🚪 Confirmar Check-out' }}
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
  visit: {
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
const visitResult = ref('success')
const notes = ref('')
const submitting = ref(false)
const result = ref(null)

// ============================================================================
// COMPUTED
// ============================================================================

const locationCaptured = computed(() => currentLocation.value !== null)

const timeInSite = computed(() => {
  if (!props.visit?.checkin_time) return '-'
  
  const checkinTime = new Date(props.visit.checkin_time)
  const now = new Date()
  const diffMs = now - checkinTime
  const diffMins = Math.floor(diffMs / 60000)
  const hours = Math.floor(diffMins / 60)
  const mins = diffMins % 60
  
  if (hours > 0) {
    return `${hours}h ${mins}m`
  }
  return `${mins}m`
})

const canSubmit = computed(() => {
  return locationCaptured.value && visitResult.value
})

// ============================================================================
// FUNCIONES
// ============================================================================

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

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

const submitCheckout = async () => {
  if (!canSubmit.value) return

  submitting.value = true
  
  try {
    const payload = {
      visit_id: props.visit.id,
      latitude: currentLocation.value.latitude,
      longitude: currentLocation.value.longitude,
      notes: notes.value,
      visit_result: visitResult.value
    }

    const response = await fetch(`${API_URL}/visits/checkout/`, {
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
        message: '✅ Check-out registrado correctamente'
      }
      
      setTimeout(() => {
        emit('success')
      }, 1500)
    } else {
      result.value = {
        success: false,
        message: `❌ Error: ${data.detail || 'Error en check-out'}`
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
</script>

<style scoped>
* {
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
}
</style>
