<template>
  <div class="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
    <div class="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[95vh] overflow-y-auto">
      <!-- HEADER MINIMALISTA -->
      <div class="bg-white border-b border-gray-200 px-4 sm:px-6 py-4 sticky top-0 z-10 flex items-center justify-between">
        <h2 class="text-lg sm:text-xl font-semibold text-black">Check-in</h2>
        <button 
          @click="$emit('close')"
          class="text-gray-500 hover:text-black font-semibold text-xl w-8 h-8 flex items-center justify-center"
        >
          ✕
        </button>
      </div>

      <div class="p-4 sm:p-6 space-y-6">
        <!-- INFO DEL CLIENTE -->
        <div class="space-y-4">
          <h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide">Cliente</h3>
          <div class="bg-gray-50 rounded-lg p-4 space-y-2 border border-gray-200">
            <div>
              <p class="text-xs text-gray-600 font-medium">Nombre</p>
              <p class="text-black font-semibold">{{ route.client?.name }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-600 font-medium">Dirección</p>
              <p class="text-gray-700 text-sm break-words">{{ route.client?.address }}</p>
            </div>
            <div class="grid grid-cols-2 gap-4 pt-2">
              <div>
                <p class="text-xs text-gray-600 font-medium">Teléfono</p>
                <p class="text-gray-900 font-mono text-sm">{{ route.client?.phone }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-600 font-medium">Tipo</p>
                <p class="text-gray-900 text-sm">{{ route.client?.client_type }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- GPS -->
        <div class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide">Ubicación GPS</h3>
          <p class="text-xs text-gray-600">Debes estar a menos de 100m del cliente</p>
          
          <button 
            @click="captureLocation"
            :disabled="loadingLocation || locationCaptured"
            class="w-full bg-black text-white font-medium py-2 sm:py-3 px-4 rounded hover:bg-gray-900 disabled:opacity-50 transition-colors text-sm sm:text-base"
          >
            {{ loadingLocation ? 'Obteniendo ubicación...' : locationCaptured ? '✓ Ubicación capturada' : '↓ Capturar GPS' }}
          </button>

          <div v-if="currentLocation" class="bg-gray-50 rounded-lg p-4 space-y-3 border border-gray-200">
            <div class="grid grid-cols-2 gap-4 text-xs">
              <div>
                <p class="text-gray-600 font-medium mb-1">Latitud</p>
                <p class="font-mono text-gray-900">{{ currentLocation.latitude.toFixed(6) }}</p>
              </div>
              <div>
                <p class="text-gray-600 font-medium mb-1">Longitud</p>
                <p class="font-mono text-gray-900">{{ currentLocation.longitude.toFixed(6) }}</p>
              </div>
              <div class="col-span-2">
                <p class="text-gray-600 font-medium mb-1">Precisión</p>
                <p class="text-gray-900">± {{ currentLocation.accuracy.toFixed(0) }}m</p>
              </div>
            </div>
            
            <div v-if="distanceToClient !== null" class="pt-3 border-t border-gray-200">
              <p class="text-gray-600 font-medium mb-2 text-xs">Distancia al cliente</p>
              <div :class="[
                'text-center py-2 rounded font-semibold text-sm',
                distanceToClient <= 100 
                  ? 'bg-gray-100 text-black border border-gray-200' 
                  : 'bg-red-50 text-red-900 border border-red-200'
              ]">
                {{ distanceToClient.toFixed(0) }}m
                <span class="ml-1">
                  {{ distanceToClient <= 100 ? '✓' : '⚠' }}
                </span>
              </div>
            </div>
          </div>

          <div v-if="locationError" class="bg-red-50 border border-red-200 text-red-900 p-3 rounded text-xs">
            <p class="font-semibold">Error: {{ locationError }}</p>
          </div>
        </div>

        <!-- CONFIRMACIÓN -->
        <div class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide">Confirmación</h3>
          <div class="space-y-2">
            <label class="flex items-center gap-3 cursor-pointer p-3 border border-gray-200 rounded hover:bg-gray-50 transition-colors" :class="[
              clientFound === true ? 'border-black bg-gray-50' : ''
            ]">
              <input 
                type="radio" 
                v-model="clientFound" 
                :value="true"
                class="w-4 h-4 cursor-pointer accent-black"
              />
              <span class="text-black font-medium text-sm">Cliente disponible</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer p-3 border border-gray-200 rounded hover:bg-gray-50 transition-colors" :class="[
              clientFound === false ? 'border-black bg-gray-50' : ''
            ]">
              <input 
                type="radio" 
                v-model="clientFound" 
                :value="false"
                class="w-4 h-4 cursor-pointer accent-black"
              />
              <span class="text-black font-medium text-sm">Cliente no disponible</span>
            </label>
          </div>
        </div>

        <!-- NOTAS -->
        <div class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide">Notas</h3>
          <textarea 
            v-model="notes"
            class="w-full px-4 py-3 border border-gray-200 rounded focus:outline-none focus:border-black text-sm bg-gray-50 resize-none"
            rows="3"
            placeholder="Anotaciones sobre la visita..."
          />
        </div>

        <!-- BOTONES -->
        <div class="flex gap-3 pt-4 border-t border-gray-200">
          <button 
            @click="$emit('close')"
            class="flex-1 bg-gray-200 hover:bg-gray-300 text-black font-medium py-2 sm:py-3 px-4 rounded transition-colors text-sm sm:text-base"
          >
            Cancelar
          </button>
          <button 
            @click="submitCheckin"
            :disabled="!canSubmit"
            class="flex-1 bg-black hover:bg-gray-900 text-white font-medium py-2 sm:py-3 px-4 rounded disabled:opacity-50 transition-colors text-sm sm:text-base"
          >
            {{ submitting ? 'Registrando...' : 'Confirmar check-in' }}
          </button>
        </div>

        <!-- RESULTADO -->
        <div 
          v-if="result"
          :class="[
            'p-3 sm:p-4 rounded border font-medium text-sm',
            result.success 
              ? 'bg-gray-100 border-gray-300 text-gray-900' 
              : 'bg-red-50 border-red-200 text-red-900'
          ]"
        >
          {{ result.success ? '✓ Check-in registrado' : '✕ ' }}{{ result.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  route: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'success'])

const API_URL = 'http://localhost:8000'

const currentLocation = ref(null)
const loadingLocation = ref(false)
const clientFound = ref(null)
const notes = ref('')
const submitting = ref(false)
const result = ref(null)
const locationError = ref(null)

const locationCaptured = computed(() => currentLocation.value !== null)

const distanceToClient = computed(() => {
  if (!currentLocation.value || !props.route.client) return null
  
  const lat2 = props.route.client.latitude
  const lng2 = props.route.client.longitude
  
  if (!lat2 || !lng2) return null
  
  const lat1 = currentLocation.value.latitude
  const lng1 = currentLocation.value.longitude
  
  const R = 6371000
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

const captureLocation = () => {
  if (!navigator.geolocation) {
    locationError.value = 'Geolocalización no disponible'
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
      locationError.value = error.message || 'Error al obtener ubicación'
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
        message: 'Check-in registrado exitosamente'
      }
      
      setTimeout(() => {
        emit('success')
      }, 1500)
    } else {
      result.value = {
        success: false,
        message: data.detail || 'Error al registrar check-in'
      }
    }
  } catch (error) {
    result.value = {
      success: false,
      message: 'Error en la comunicación con el servidor'
    }
  } finally {
    submitting.value = false
  }
}

Math.radians = function(degrees) {
  return degrees * (Math.PI / 180)
}
</script>

<style scoped>
* {
  transition: all 0.2s ease;
}

@media (max-width: 640px) {
  :deep(input), :deep(textarea), :deep(select) {
    font-size: 16px;
  }
}

input[type="radio"]:checked {
  accent-color: black;
}
</style>
