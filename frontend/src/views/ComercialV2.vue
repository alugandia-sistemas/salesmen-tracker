<template>
   <div class="min-h-screen bg-white">
      <!-- Sidebar Overlay -->
      <div v-if="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black/40 z-40 md:hidden"></div>

      <!-- Sidebar -->
      <div
         :class="['fixed top-0 left-0 h-full w-64 bg-white shadow-2xl z-50 transform transition-transform duration-300 md:hidden', sidebarOpen ? 'translate-x-0' : '-translate-x-full']">
         <div class="p-6">
            <div class="flex justify-between items-center mb-8">
               <h2 class="text-xl font-bold text-gray-900">Menú</h2>
               <button @click="sidebarOpen = false" class="text-gray-600 hover:text-gray-900">
                  <span class="text-2xl">×</span>
               </button>
            </div>
            <nav class="space-y-4">
               <a href="#rutas" @click="sidebarOpen = false"
                  class="block px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-900 font-semibold">
                  📍 Rutas de hoy
               </a>
               <a href="#historico" @click="sidebarOpen = false"
                  class="block px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-900 font-semibold">
                  📊 Histórico
               </a>
               <a href="#clientes" @click="sidebarOpen = false"
                  class="block px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-900 font-semibold">
                  👥 Clientes
               </a>
               <a href="#visitas" @click="sidebarOpen = false"
                  class="block px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-900 font-semibold">
                  📝 Historial de visitas
               </a>
            </nav>
         </div>
      </div>

      <!-- Header -->
      <nav class="bg-white border-b border-gray-200 sticky top-0 z-30">
         <div class="px-4 py-4">
            <div class="flex justify-between items-center">
               <div class="flex items-center gap-3">
                  <button @click="sidebarOpen = !sidebarOpen"
                     class="md:hidden text-gray-900 p-2 hover:bg-gray-100 rounded-lg">
                     <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                           d="M4 6h16M4 12h16M4 18h16"></path>
                     </svg>
                  </button>
                  <h1 class="text-2xl font-bold text-gray-900">Alugandia</h1>
               </div>
               <button @click="logout" class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-semibold">
                  Salir
               </button>
            </div>
            <p class="text-gray-600 text-sm mt-2 ml-11 md:ml-0">App de Vendedor</p>
         </div>
      </nav>

      <!-- Content -->
      <div class="px-4 py-6 pb-20">
         <!-- Greeting -->
         <h2 class="text-3xl font-bold text-gray-900 mb-6">¡Hola, {{ sellerName }}!</h2>

         <!-- Rutas para hoy -->
         <div id="rutas" class="mb-8">
            <h3 class="text-xl font-bold text-gray-900 mb-4">Rutas de hoy</h3>

            <div v-if="routesHoy.length > 0" class="space-y-3">
               <div v-for="ruta in routesHoy" :key="ruta.id" class="bg-gray-50 border-2 border-gray-200 rounded-xl p-5">
                  <div class="flex items-start gap-3 mb-4">
                     <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                        <span class="text-white font-bold">{{ getNombreCliente(ruta.client_id).charAt(0) }}</span>
                     </div>
                     <div class="flex-1">
                        <h4 class="text-lg font-bold text-gray-900">{{ getNombreCliente(ruta.client_id) }}</h4>
                        <p class="text-gray-600 text-sm">📍 {{ getClienteDireccion(ruta.client_id) }}</p>
                     </div>
                  </div>

                  <div class="flex gap-2 mb-4">
                     <span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-200 text-gray-900">
                        📅 {{ formatDate(ruta.planned_date) }}
                     </span>
                     <span class="px-3 py-1 rounded-full text-xs font-semibold"
                        :class="ruta.status === 'pending' ? 'bg-orange-200 text-orange-900' : 'bg-green-200 text-green-900'">
                        {{ ruta.status === 'pending' ? '⏳ Pendiente' : '✅ Completada' }}
                     </span>
                  </div>

                  <button v-if="ruta.status === 'pending'" @click="iniciarCheckin(ruta)"
                     class="w-full bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition">
                     📍 Iniciar Check-in
                  </button>
                  <button v-else @click="verVisita(ruta.id)"
                     class="w-full bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold text-lg hover:bg-gray-200 transition">
                     Ver detalles
                  </button>
               </div>
            </div>

            <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
               <p class="text-gray-600 text-sm">Sin rutas para hoy</p>
            </div>
         </div>

         <!-- Histórico de Rutas -->
         <div id="historico" class="mb-8">
            <h3 class="text-xl font-bold text-gray-900 mb-4">📊 Histórico de Rutas</h3>

            <div v-if="loadingStats" class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
               <p class="text-gray-600 text-sm">⏳ Cargando estadísticas...</p>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
               <!-- Total Visits -->
               <div class="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-xl p-6">
                  <div class="flex items-center justify-between mb-2">
                     <h4 class="text-sm font-semibold text-blue-900">Total de Visitas</h4>
                     <span class="text-2xl">📍</span>
                  </div>
                  <p class="text-4xl font-bold text-blue-900 mb-1">{{ historicStats.total_visits }}</p>
                  <p class="text-xs text-blue-700">Todas las visitas realizadas</p>
               </div>

               <!-- Completed Visits -->
               <div class="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 rounded-xl p-6">
                  <div class="flex items-center justify-between mb-2">
                     <h4 class="text-sm font-semibold text-green-900">Visitas Completadas</h4>
                     <span class="text-2xl">✅</span>
                  </div>
                  <p class="text-4xl font-bold text-green-900 mb-1">{{ historicStats.completed_visits }}</p>
                  <div class="flex items-center gap-2">
                     <div class="flex-1 bg-green-200 rounded-full h-2">
                        <div class="bg-green-600 h-2 rounded-full"
                           :style="{ width: historicStats.visits_completion_percentage + '%' }"></div>
                     </div>
                     <span class="text-xs font-bold text-green-700">{{ historicStats.visits_completion_percentage
                        }}%</span>
                  </div>
               </div>
            </div>
         </div>

         <!-- 🔍 BÚSQUEDA + PAGINACIÓN DE CLIENTES -->
         <div id="clientes" class="mb-8">
            <h3 class="text-xl font-bold text-gray-900 mb-4">Buscar Clientes</h3>

            <!-- Input de búsqueda -->
            <div class="mb-4">
               <div class="relative">
                  <input v-model="searchQuery" type="text" placeholder="Busca por nombre, teléfono o email..."
                     class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 pl-10"
                     @input="handleSearch" />
                  <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                  </svg>
                  <button v-if="searchQuery" type="button" @click="searchQuery=''; handleSearch();" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" aria-label="Limpiar búsqueda">
                     <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
               </div>
               <p class="text-gray-500 text-xs mt-2">
                  {{ clientesMetadata.total }} clientes encontrados
               </p>
            </div>

            <!-- Estado de carga -->
            <div v-if="cargandoClientes" class="text-center py-8">
               <p class="text-gray-600">⏳ Buscando clientes...</p>
            </div>

            <!-- Lista de clientes -->
            <div v-else-if="clientesFiltrados.length > 0" class="space-y-3">
               <div v-for="cliente in clientesFiltrados" :key="cliente.id"
                  class="bg-gray-50 border-2 border-gray-200 rounded-xl p-5 hover:border-gray-900 cursor-pointer transition"
                  @click="seleccionarCliente(cliente)">
                  <div class="flex items-start justify-between">
                     <div class="flex-1">
                        <h4 class="text-lg font-bold text-gray-900">{{ cliente.name }}</h4>
                        <p class="text-gray-600 text-sm">📍 {{ cliente.address }}</p>
                        <div class="flex gap-4 mt-2">
                           <span class="text-gray-700 text-xs font-mono">📞 {{ cliente.phone }}</span>
                           <span v-if="cliente.email" class="text-gray-700 text-xs truncate">📧 {{ cliente.email
                           }}</span>
                        </div>
                     </div>
                     <span
                        class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-200 text-gray-900 whitespace-nowrap">
                        {{ cliente.client_type }}
                     </span>
                  </div>
               </div>
            </div>

            <!-- Sin resultados -->
            <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
               <p class="text-gray-600 text-sm">
                  {{ searchQuery ? 'No se encontraron clientes' : 'Escribe para buscar clientes' }}
               </p>
            </div>

            <!-- 📄 PAGINACIÓN -->
            <div v-if="clientesFiltrados.length > 0" class="flex items-center justify-between mt-6 px-2">
               <button @click="irAPagina(clientesMetadata.page - 1)" :disabled="!clientesMetadata.has_prev"
                  class="px-4 py-2 rounded-lg font-semibold text-sm bg-gray-900 text-white disabled:bg-gray-400 transition">
                  ← Anterior
               </button>

               <div class="text-center text-xs font-semibold text-gray-900">
                  <p>Página {{ clientesMetadata.page }} de {{ clientesMetadata.total_pages }}</p>
                  <p class="text-gray-600 text-xs mt-1">
                     Mostrando {{ clientesFiltrados.length }} de {{ clientesMetadata.total }}
                  </p>
               </div>

               <button @click="irAPagina(clientesMetadata.page + 1)" :disabled="!clientesMetadata.has_next"
                  class="px-4 py-2 rounded-lg font-semibold text-sm bg-gray-900 text-white disabled:bg-gray-400 transition">
                  Siguiente →
               </button>
            </div>

            <!-- Selector de items por página -->
            <div class="flex items-center justify-center gap-3 mt-4">
               <label class="text-gray-600 text-sm font-semibold">Items por página:</label>
               <select v-model.number="clientesMetadata.limit" @change="fetchClientes(1)"
                  class="px-3 py-2 border-2 border-gray-300 rounded-lg text-sm focus:outline-none focus:border-gray-900">
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                  <option :value="200">200</option>
               </select>
            </div>
         </div>

         <!-- Historial de visitas -->
         <div id="visitas">
            <h3 class="text-xl font-bold text-gray-900 mb-4">Historial de visitas</h3>

            <div v-if="visitasRecientes.length > 0" class="space-y-3">
               <div v-for="visita in visitasRecientes" :key="visita.id"
                  class="bg-gray-50 border-2 border-gray-200 rounded-xl p-5">
                  <div class="flex items-start justify-between mb-2">
                     <h4 class="font-bold text-gray-900">{{ getNombreCliente(visita.client_id) }}</h4>
                     <span class="px-3 py-1 rounded-full text-xs font-semibold"
                        :class="visita.checkin_is_valid ? 'bg-green-200 text-green-900' : 'bg-red-200 text-red-900'">
                        {{ visita.checkin_is_valid ? '✅ Válido' : '❌ Inválido' }}
                     </span>
                  </div>
                  <p class="text-gray-600 text-sm mb-2">{{ formatDate(visita.checkin_time) }}</p>
                  <p class="text-gray-700 text-sm">📍 Distancia: {{ visita.checkin_distance_meters.toFixed(1) }}m</p>
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

            <div class="bg-gray-100 rounded-lg p-4 mb-6 text-center">
               <p class="text-gray-600 text-sm mb-4">📍 Esperando ubicación...</p>
               <div v-if="ubicacionActual" class="text-left space-y-2">
                  <p class="text-gray-900 font-semibold">Ubicación detectada:</p>
                  <p class="text-gray-700 text-sm">Latitud: {{ ubicacionActual.latitude.toFixed(5) }}</p>
                  <p class="text-gray-700 text-sm">Longitud: {{ ubicacionActual.longitude.toFixed(5) }}</p>
                  <p class="text-gray-700 text-sm">Precisión: ±{{ ubicacionActual.accuracy.toFixed(0) }}m</p>
               </div>
            </div>

            <div class="mb-6">
               <label
                  class="flex items-center gap-4 p-4 border-2 border-gray-300 rounded-lg cursor-pointer hover:border-gray-900">
                  <input v-model="clienteEncontrado" type="checkbox" class="w-6 h-6 accent-gray-900" />
                  <span class="text-gray-900 font-semibold">✓ Cliente confirmado en la ubicación</span>
               </label>
            </div>

            <div class="mb-6">
               <label class="block text-sm font-semibold text-gray-900 mb-2">Notas (opcional)</label>
               <textarea v-model="notasCheckin" placeholder="Ej: Cliente no estaba disponible..."
                  class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 text-sm"
                  rows="3"></textarea>
            </div>

            <div class="flex gap-3">
               <button @click="cerrarModal()"
                  class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold text-lg hover:bg-gray-200 transition">
                  Cancelar
               </button>
               <button @click="hacerCheckin()" :disabled="!ubicacionActual"
                  class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed">
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

               <div class="bg-gray-50 rounded-lg p-4 mb-6 text-center">
                  <p class="text-gray-600 text-sm">Distancia al cliente</p>
                  <p class="text-3xl font-bold text-gray-900">{{ resultadoCheckin.distance_meters.toFixed(1) }}m</p>
               </div>

               <div v-if="resultadoCheckin.validation_error"
                  class="bg-red-50 border-2 border-red-200 rounded-lg p-4 mb-6 text-left">
                  <p class="text-red-900 font-semibold text-sm">⚠️ {{ resultadoCheckin.validation_error }}</p>
               </div>

               <div class="flex gap-3">
                  <button @click="cerrarResultado()"
                     class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition">
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

         // 🔍 BÚSQUEDA Y PAGINACIÓN
         clientesFiltrados: [],
         searchQuery: '',
         cargandoClientes: false,
         searchTimeout: null,
         clientesMetadata: {
            page: 1,
            limit: 100,
            total: 0,
            total_pages: 0,
            has_next: false,
            has_prev: false
         },

         // 📊 HISTÓRICO DE RUTAS
         historicStats: {
            total_routes: 0,
            completed_routes: 0,
            routes_completion_percentage: 0,
            total_visits: 0,
            completed_visits: 0,
            visits_completion_percentage: 0
         },
         loadingStats: false,

         // 📱 SIDEBAR
         sidebarOpen: false,

         // CHECK-IN
         showCheckinModal: false,
         showResultado: false,
         rutaActual: null,

         ubicacionActual: null,
         clienteEncontrado: false,
         notasCheckin: '',
         cargandoCheckin: false,

         resultadoCheckin: null,
         geoWatcher: null,

         // ✅ NUEVO: Mapa de clientes
         clientesMap: {},
         clientesMapLoaded: false,
      }
   },
   async mounted() {
    const sellerData = localStorage.getItem('seller')
    if (sellerData) {
        this.seller = JSON.parse(sellerData)
        this.sellerName = this.seller.name.split(' ')[0]
        
        // 🔑 CRÍTICO: Cargar clientes PRIMERO
        await this.loadAllClientes()
        
        this.fetchRoutesHoy()
        this.fetchClientes(1)
        this.fetchHistoricStats()
    } else {
        this.$router.push('/login')
    }
   },
   beforeUnmount() {
      if (this.geoWatcher) {
         navigator.geolocation.clearWatch(this.geoWatcher)
      }
      if (this.searchTimeout) {
         clearTimeout(this.searchTimeout)
      }
   },
   methods: {
      // 🔍 BÚSQUEDA CON DEBOUNCE
      handleSearch() {
         // Limpiar timeout anterior
         if (this.searchTimeout) {
            clearTimeout(this.searchTimeout)
         }

         // Esperar 500ms sin que el usuario escriba para buscar
         this.searchTimeout = setTimeout(() => {
            this.fetchClientes(1)  // Volver a página 1 cuando busca
         }, 500)
      },

      // 📊 CARGAR ESTADÍSTICAS HISTÓRICAS
      async fetchHistoricStats() {
         try {
            this.loadingStats = true
            const response = await fetch(
               `${import.meta.env.VITE_API_URL}/routes/stats/?seller_id=${this.seller.id}`
            )
            const data = await response.json()
            this.historicStats = data
         } catch (e) {
            console.error('Error fetching historic stats:', e)
         } finally {
            this.loadingStats = false
         }
      },

      // 📄 CARGAR CLIENTES CON PAGINACIÓN
      async fetchClientes(page = 1) {
         try {
            this.cargandoClientes = true

            // Construir URL con parámetros
            const params = new URLSearchParams({
               page: page,
               limit: this.clientesMetadata.limit,
               ...(this.searchQuery && { search: this.searchQuery })
            })

            const response = await fetch(
               `${import.meta.env.VITE_API_URL}/clients/?${params.toString()}`
            )

            const data = await response.json()

            this.clientesFiltrados = data.data || []
            this.clientesMetadata = data.pagination || {}
         } catch (e) {
            console.error('Error fetching clientes:', e)
            this.clientesFiltrados = []
         } finally {
            this.cargandoClientes = false
         }
      },

      // ⬅️ ➡️ NAVEGAR ENTRE PÁGINAS
      irAPagina(page) {
         if (page >= 1 && page <= this.clientesMetadata.total_pages) {
            this.fetchClientes(page)
            // Scroll al top
            window.scrollTo({ top: 0, behavior: 'smooth' })
         }
      },

      // 👆 SELECCIONAR CLIENTE DESDE LISTA
      seleccionarCliente(cliente) {
         // Podrías crear una ruta rápida aquí
         console.log('Cliente seleccionado:', cliente)
         // TODO: Mostrar opciones (crear ruta, ver historial, etc)
      },

      async fetchRutasHoy() {
         try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/?seller_id=${this.seller.id}`)
            const todas = await response.json()

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

      iniciarGPS() {
         if (!navigator.geolocation) {
            alert('Geolocalización no disponible en tu dispositivo')
            return
         }

         navigator.geolocation.getCurrentPosition(
            (position) => {
               this.ubicacionActual = {
                  latitude: position.coords.latitude,
                  longitude: position.coords.longitude,
                  accuracy: position.coords.accuracy
               }
            },
            (error) => {
               console.error('GPS error:', error.message)
            },
            { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
         )

         this.geoWatcher = navigator.geolocation.watchPosition(
            (position) => {
               this.ubicacionActual = {
                  latitude: position.coords.latitude,
                  longitude: position.coords.longitude,
                  accuracy: position.coords.accuracy
               }
            },
            (error) => {
               console.error('GPS watch error:', error.message)
            },
            { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
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
         const c = this.clientesFiltrados.find(x => x.id === id)
         return c ? c.name : 'Desconocido'
      },

      getClienteDireccion(id) {
         const c = this.clientesFiltrados.find(x => x.id === id)
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
      },
      async loadAllClientes() {
         if (this.clientesMapLoaded) return
         
         try {
            console.log('📦 ComercialV2: Cargando clientes...')
            const response = await fetch(`${import.meta.env.VITE_API_URL}/clients/sync/`)
            
            if (response.ok) {
               const data = await response.json()
               const allClientes = data.clients || []
               
               this.clientesMap = {}
               allClientes.forEach(client => {
               this.clientesMap[client.id] = client
               })
               
               this.clientesMapLoaded = true
               console.log(`✅ ${Object.keys(this.clientesMap).length} clientes cargados`)
            } else {
               // Fallback
               const resp2 = await fetch(`${import.meta.env.VITE_API_URL}/clients/?limit=500`)
               const data2 = await resp2.json()
               const clientes = data2.data || (Array.isArray(data2) ? data2 : [])
               
               this.clientesMap = {}
               clientes.forEach(c => { this.clientesMap[c.id] = c })
               this.clientesMapLoaded = true
            }
         } catch (e) {
            console.error('❌ Error:', e)
         }
      },

      getNombreCliente(id) {
      if (!id) return 'Sin cliente'
      const client = this.clientesMap[id]
      return client ? client.name : 'Cargando...'
      },

      getClienteDireccion(id) {
      if (!id) return ''
      const client = this.clientesMap[id]
      return client ? client.address : ''
      },
   }
}
</script>

<style scoped>
* {
   -webkit-font-smoothing: antialiased;
}
</style>