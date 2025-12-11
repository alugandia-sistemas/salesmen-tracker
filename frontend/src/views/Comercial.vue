<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="px-4 py-4">
        <div class="flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Alugandia</h1>
          <button @click="logout" class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-semibold">
            Salir
          </button>
        </div>
        <p class="text-gray-600 text-sm mt-2">App de Vendedor</p>
      </div>
    </nav>

    <!-- Content -->
    <div class="px-4 py-6 pb-20">
      <!-- Greeting -->
      <h2 class="text-3xl font-bold text-gray-900 mb-6">¡Hola, {{ sellerName }}!</h2>

      <!-- Rutas para hoy -->
      <div class="mb-8">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Rutas de hoy</h3>
        
        <div v-if="routesHoy.length > 0" class="space-y-3">
          <div v-for="ruta in routesHoy" :key="ruta.id" class="bg-gray-50 border-2 border-gray-200 rounded-xl p-5">
            <!-- Cliente -->
            <div class="flex items-start gap-3 mb-4">
              <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold">{{ getNombreCliente(ruta.client_id).charAt(0) }}</span>
              </div>
              <div class="flex-1">
                <h4 class="text-lg font-bold text-gray-900">{{ getNombreCliente(ruta.client_id) }}</h4>
                <p class="text-gray-600 text-sm">📍 {{ getClienteDireccion(ruta.client_id) }}</p>
              </div>
            </div>

            <!-- Status badges -->
            <div class="flex gap-2 mb-4">
              <span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-200 text-gray-900">
                📅 {{ formatDate(ruta.planned_date) }}
              </span>
              <span 
                class="px-3 py-1 rounded-full text-xs font-semibold"
                :class="ruta.status === 'pending' ? 'bg-orange-200 text-orange-900' : 'bg-green-200 text-green-900'"
              >
                {{ ruta.status === 'pending' ? '⏳ Pendiente' : '✅ Completada' }}
              </span>
            </div>

            <!-- Check-in Button -->
            <button 
              v-if="ruta.status === 'pending'"
              @click="iniciarCheckin(ruta)" 
              class="w-full bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition"
            >
              📍 Iniciar Check-in
            </button>
            <button 
              v-else
              @click="verVisita(ruta.id)"
              class="w-full bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold text-lg hover:bg-gray-200 transition"
            >
              Ver detalles
            </button>
          </div>
        </div>

        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-600 text-sm">Sin rutas para hoy</p>
        </div>
      </div>

      <!-- Historial de visitas -->
      <div>
        <h3 class="text-xl font-bold text-gray-900 mb-4">Historial de visitas</h3>
        
        <div v-if="visitasRecientes.length > 0" class="space-y-3">
          <div v-for="visita in visitasRecientes" :key="visita.id" class="bg-gray-50 border-2 border-gray-200 rounded-xl p-5">
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-bold text-gray-900">{{ getNombreCliente(visita.client_id) }}</h4>
              <span 
                class="px-3 py-1 rounded-full text-xs font-semibold"
                :class="visita.checkin_is_valid ? 'bg-green-200 text-green-900' : 'bg-red-200 text-red-900'"
              >
                {{ visita.checkin_is_valid ? '✅ Válido' : '❌ Inválido' }}
              </span>
            </div>
            <p class="text-gray-600 text-sm mb-2">{{ formatDate(visita.checkin_time) }}</p>
            <p class="text-gray-700 text-sm">📍 Distancia: {{ visita.checkin_distance_meters.toFixed(1) }}m</p>
            <p v-if="visita.checkin_validation_error" class="text-red-600 text-sm mt-2">
              ⚠️ {{ visita.checkin_validation_error }}
            </p>
          </div>
        </div>

        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-600 text-sm">Sin visitas registradas</p>
        </div>
      </div>
    </div>

    <!-- MODAL CHECK-IN -->
    <div v-if="showCheckinModal" class="fixed inset-0 bg-black/40 flex items-end z-50">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-2xl font-bold text-gray-900 mb-6">
          Check-in: {{ getNombreCliente(rutaActual.client_id) }}
        </h3>

        <!-- Mapa o información de ubicación -->
        <div class="bg-gray-100 rounded-lg p-4 mb-6 text-center">
          <p class="text-gray-600 text-sm mb-4">📍 Esperando ubicación...</p>
          <div v-if="ubicacionActual" class="text-left space-y-2">
            <p class="text-gray-900 font-semibold">Ubicación detectada:</p>
            <p class="text-gray-700 text-sm">Latitud: {{ ubicacionActual.latitude.toFixed(5) }}</p>
            <p class="text-gray-700 text-sm">Longitud: {{ ubicacionActual.longitude.toFixed(5) }}</p>
            <p class="text-gray-700 text-sm">Precisión: ±{{ ubicacionActual.accuracy.toFixed(0) }}m</p>
          </div>
          <div v-else class="text-gray-500 text-sm">
            <p>Permitir acceso a ubicación</p>
            <p class="text-xs mt-2">La app necesita tu GPS</p>
          </div>
        </div>

        <!-- Cliente encontrado -->
        <div class="mb-6">
          <label class="flex items-center gap-4 p-4 border-2 border-gray-300 rounded-lg cursor-pointer hover:border-gray-900">
            <input 
              v-model="clienteEncontrado" 
              type="checkbox" 
              class="w-6 h-6 accent-gray-900"
            />
            <span class="text-gray-900 font-semibold">✓ Cliente confirmado en la ubicación</span>
          </label>
        </div>

        <!-- Notas -->
        <div class="mb-6">
          <label class="block text-sm font-semibold text-gray-900 mb-2">Notas (opcional)</label>
          <textarea 
            v-model="notasCheckin" 
            placeholder="Ej: Cliente no estaba disponible..."
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 text-sm"
            rows="3"
          ></textarea>
        </div>

        <!-- Botones -->
        <div class="flex gap-3">
          <button 
            @click="cerrarModal()"
            class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold text-lg hover:bg-gray-200 transition"
          >
            Cancelar
          </button>
          <button 
            @click="hacerCheckin()"
            :disabled="!ubicacionActual"
            class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ cargandoCheckin ? '⏳ Guardando...' : '📍 Confirmar Check-in' }}
          </button>
        </div>
      </div>
    </div>

    <!-- RESULTADO CHECK-IN -->
    <div v-if="showResultado" class="fixed inset-0 bg-black/40 flex items-end z-50">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl">
        <div class="text-center">
          <div class="text-5xl mb-4">{{ resultadoCheckin.is_valid ? '✅' : '⚠️' }}</div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">
            {{ resultadoCheckin.is_valid ? 'Check-in Válido' : 'Check-in con Advertencias' }}
          </h3>
          <p class="text-gray-600 text-lg mb-6">
            {{ resultadoCheckin.message }}
          </p>

          <!-- Distancia -->
          <div class="bg-gray-50 rounded-lg p-4 mb-6 text-center">
            <p class="text-gray-600 text-sm">Distancia al cliente</p>
            <p class="text-3xl font-bold text-gray-900">{{ resultadoCheckin.distance_meters.toFixed(1) }}m</p>
          </div>

          <!-- Errores/Advertencias -->
          <div v-if="resultadoCheckin.validation_error" class="bg-red-50 border-2 border-red-200 rounded-lg p-4 mb-6 text-left">
            <p class="text-red-900 font-semibold text-sm">⚠️ {{ resultadoCheckin.validation_error }}</p>
          </div>

          <div v-if="resultadoCheckin.fraud_flags && resultadoCheckin.fraud_flags.length > 0" class="bg-orange-50 border-2 border-orange-200 rounded-lg p-4 mb-6 text-left">
            <p class="text-orange-900 font-semibold text-sm mb-2">🚨 Alertas detectadas:</p>
            <ul class="text-orange-900 text-sm space-y-1">
              <li v-for="flag in resultadoCheckin.fraud_flags" :key="flag">• {{ flag }}</li>
            </ul>
          </div>

          <!-- Botones -->
          <div class="flex gap-3">
            <button 
              @click="cerrarResultado()"
              class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition"
            >
              {{ resultadoCheckin.is_valid ? 'Continuar' : 'Aceptar' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Comercial',
  data() {
    return {
      seller: null,
      sellerName: 'Vendedor',
      routesHoy: [],
      visitasRecientes: [],
      clientes: [],
      
      showCheckinModal: false,
      showResultado: false,
      rutaActual: null,
      
      ubicacionActual: null,
      clienteEncontrado: false,
      notasCheckin: '',
      cargandoCheckin: false,
      
      resultadoCheckin: null,
      geoWatcher: null
    }
  },
  mounted() {
    // Verificar si está logueado
    const sellerData = localStorage.getItem('seller')
    if (!sellerData) {
      this.$router.push('/login')
      return
    }

    this.seller = JSON.parse(sellerData)
    this.sellerName = this.seller.name

    this.fetchRutasHoy()
    this.fetchVisitas()
    this.fetchClientes()
    this.iniciarGPS()
  },
  beforeUnmount() {
    if (this.geoWatcher) {
      navigator.geolocation.clearWatch(this.geoWatcher)
    }
  },
  methods: {
    async fetchRutasHoy() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/?seller_id=${this.seller.id}`)
        const todas = await response.json()
        
        // Filtrar por hoy
        const hoy = new Date().toISOString().split('T')[0]
        this.routesHoy = todas.filter(r => r.planned_date.split('T')[0] === hoy)
      } catch (e) {
        console.error('Error:', e)
      }
    },
    async fetchVisitas() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/visits/`)
        this.visitasRecientes = await response.json()
      } catch (e) {
        console.error('Error:', e)
      }
    },
    async fetchClientes() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/clients/`)
        this.clientes = await response.json()
      } catch (e) {
        console.error('Error:', e)
      }
    },
    
    iniciarGPS() {
      if (!navigator.geolocation) {
        alert('Geolocalización no disponible en tu dispositivo')
        return
      }
      
      console.log('🔍 Starting GPS initialization (Comercial)...')
      
      // Obtener ubicación inicial
      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log('✅ GPS location obtained:', position.coords)
          this.ubicacionActual = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          }
        },
        (error) => {
          console.error('❌ GPS error:', error.code, error.message)
          let message = 'Error de ubicación: '
          switch(error.code) {
            case error.PERMISSION_DENIED:
              message += 'Permiso de ubicación denegado. Habilita los permisos de geolocalización en tu navegador.'
              break
            case error.POSITION_UNAVAILABLE:
              message += 'Información de posición no disponible.'
              break
            case error.TIMEOUT:
              message += 'La solicitud de ubicación tardó demasiado.'
              break
            default:
              message += error.message
          }
          console.warn(message)
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      )
      
      // Monitorear cambios de ubicación
      this.geoWatcher = navigator.geolocation.watchPosition(
        (position) => {
          console.log('📍 GPS watch update:', position.coords)
          this.ubicacionActual = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          }
        },
        (error) => {
          console.error('❌ GPS watch error:', error.code, error.message)
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      )
    },
    
    iniciarCheckin(ruta) {
      this.rutaActual = ruta
      this.clienteEncontrado = false
      this.notasCheckin = ''
      this.showCheckinModal = true
    },
    
    async hacerCheckin() {
      if (!this.ubicacionActual) {
        alert('Ubicación no disponible')
        return
      }
      
      this.cargandoCheckin = true
      
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/visits/checkin/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            route_id: this.rutaActual.id,
            seller_id: this.rutaActual.seller_id,
            client_id: this.rutaActual.client_id,
            latitude: this.ubicacionActual.latitude,
            longitude: this.ubicacionActual.longitude,
            client_found: this.clienteEncontrado,
            notes: this.notasCheckin || null
          })
        })
        
        this.resultadoCheckin = await response.json()
        this.showCheckinModal = false
        this.showResultado = true
        this.fetchVisitas()
      } catch (e) {
        console.error('Error en check-in:', e)
        alert('Error al hacer check-in')
      } finally {
        this.cargandoCheckin = false
      }
    },
    
    cerrarModal() {
      this.showCheckinModal = false
      this.rutaActual = null
      this.clienteEncontrado = false
      this.notasCheckin = ''
    },
    
    cerrarResultado() {
      this.showResultado = false
      this.resultadoCheckin = null
    },
    
    getNombreCliente(id) {
      const c = this.clientes.find(x => x.id === id)
      return c ? c.name : 'Desconocido'
    },
    
    getClienteDireccion(id) {
      const c = this.clientes.find(x => x.id === id)
      return c ? c.address : 'Sin dirección'
    },
    
    formatDate(date) {
      return new Date(date).toLocaleDateString('es-ES', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    
    verVisita(rutaId) {
      // TODO: Ver detalles de visita
    },
    
    logout() {
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
* {
  -webkit-font-smoothing: antialiased;
}
</style>
