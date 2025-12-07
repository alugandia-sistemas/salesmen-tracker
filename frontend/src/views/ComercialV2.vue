<template>
  <div class="h-screen flex flex-col bg-slate-50 dark:bg-slate-900 overflow-hidden relative">
    <!-- Header -->
    <header class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 p-4 flex justify-between items-center z-[50] shrink-0 h-16 shadow-sm">
      <div class="flex items-center gap-3">
        <!-- Mobile Sidebar Toggle -->
        <button @click="toggleSidebar" class="md:hidden text-slate-900 dark:text-white p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
           </svg>
        </button>
        
        <div class="flex flex-col">
          <h1 class="text-lg font-bold bg-gradient-to-r from-indigo-600 to-indigo-400 bg-clip-text text-transparent leading-tight">
            Alugandia Tracker
          </h1>
          <div class="flex items-center gap-1.5" v-if="sellerName">
             <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
             <p class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide truncate max-w-[150px]">{{ sellerName }}</p>
          </div>
        </div>
      </div>
      
      <div class="flex items-center gap-2">
         <button @click="fetchData" class="md:hidden p-2 text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg">
           🔄
         </button>
      </div>
    </header>

    <div class="flex-1 flex relative overflow-hidden">
      
      <!-- Mobile Backdrop -->
      <div 
        v-if="showSidebar" 
        @click="showSidebar = false"
        class="absolute inset-0 bg-black/50 z-20 md:hidden backdrop-blur-sm transition-opacity"
      ></div>

      <!-- Sidebar Navigation -->
      <aside 
         class="absolute md:relative inset-y-0 left-0 w-3/4 md:w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col shadow-2xl z-30 transition-transform duration-300 transform"
         :class="showSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
      >
        <div class="p-4 space-y-2 flex-1 overflow-y-auto">
           <button 
             v-for="tab in tabs" 
             :key="tab.id"
             @click="activeTab = tab.id; showSidebar = false"
             :class="[
               'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-bold text-sm',
               activeTab === tab.id 
                 ? 'bg-indigo-600 text-white shadow-md' 
                 : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
             ]"
           >
             <span class="text-xl">{{ tab.icon }}</span>
             <span>{{ tab.label }}</span>
           </button>
           
           <div class="my-4 border-t border-slate-100 dark:border-slate-700"></div>

           <router-link to="/my-route" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/40 font-bold text-sm transition-all">
              <span class="text-xl">📍</span>
              <span>Mi Cartera</span>
           </router-link>
        </div>
        
        <!-- Sidebar Footer -->
        <div class="p-4 border-t border-slate-100 dark:border-slate-700">
           <button @click="logout" class="w-full flex items-center gap-2 justify-center py-3 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg font-bold text-sm hover:bg-slate-200 transition-colors">
              🚪 Cerrar Sesión
           </button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-900 p-4 md:p-8 w-full">
         <div class="max-w-3xl mx-auto pb-20 md:pb-0">
             
           <!-- TAB: HOY -->
           <transition name="fade" mode="out-in">
             <div v-if="activeTab === 'hoy'" key="hoy"> 
               <div class="flex justify-between items-center mb-6">
                  <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Rutas de Hoy</h2>
                  <span class="bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200 px-3 py-1 rounded-full text-xs font-bold">
                    {{ routesHoy.length }} programadas
                  </span>
               </div>
               
               <div v-if="routesHoy.length > 0" class="space-y-4">
                 <div 
                   v-for="ruta in routesHoy" 
                   :key="ruta.id" 
                   class="card-driver relative overflow-hidden group"
                 >
                   <!-- Status Line -->
                   <div 
                      class="absolute left-0 top-0 bottom-0 w-1.5"
                      :class="{
                         'bg-slate-300': ruta.status === 'pending',
                         'bg-emerald-500': ruta.status === 'completed',
                         'bg-indigo-500': ruta.status === 'in_progress',
                         'bg-rose-500': ruta.status === 'cancelled'
                      }"
                   ></div>
                   
                   <div class="pl-3">
                      <!-- Header: Time & Status -->
                      <div class="flex justify-between items-center mb-3">
                         <span class="text-slate-500 dark:text-slate-400 font-mono text-sm font-bold flex items-center gap-1">
                            🕒 {{ formatTime(ruta.planned_date) }}
                         </span>
                         <span class="badge-driver" :class="getStatusBadgeClass(ruta.status)">
                            {{ getStatusLabel(ruta.status) }}
                         </span>
                      </div>
                      
                      <!-- Main Content: Client Info -->
                      <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-1">
                         {{ ruta.client?.name }}
                      </h3>
                      <p class="text-slate-600 dark:text-slate-400 text-base mb-4 flex items-start gap-1">
                         📍 {{ ruta.client?.address }}
                      </p>
                      
                      <!-- Actions Area -->
                      <div class="grid grid-cols-2 gap-3 mt-4">
                         <template v-if="ruta.status === 'pending'">
                            <button @click="iniciarCheckin(ruta)" class="btn-driver-primary col-span-2">
                                📍 CHECK-IN
                            </button>
                            <button @click="mostrarAplazar(ruta)" class="btn-driver-secondary text-sm h-12">
                                ⏰ Aplazar
                            </button>
                            <a :href="'tel:' + ruta.client?.phone" class="btn-driver-secondary text-sm h-12">
                                📞 Llamar
                            </a>
                         </template>
                         
                         <button v-else-if="ruta.status === 'completed'" @click="verDetalleVisita(ruta)" class="btn-driver-secondary col-span-2 text-sm">
                             Ver Detalles
                         </button>
                      </div>
                   </div>
                 </div>
               </div>
               
               <div v-else class="text-center py-12 px-4">
                 <div class="bg-indigo-50 dark:bg-slate-800 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span class="text-4xl">📅</span>
                 </div>
                 <h3 class="text-lg font-bold text-slate-900 dark:text-white mb-2">Todo listo por hoy</h3>
                 <p class="text-slate-500 dark:text-slate-400 max-w-xs mx-auto">No tienes más rutas programadas para hoy.</p>
               </div>
             </div>
           
             <!-- TAB: HISTORIAL -->
             <div v-else-if="activeTab === 'historial'" key="historial">
               <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-6">Historial</h2>
                <div class="mb-6 flex gap-2 overflow-x-auto pb-2 no-scrollbar">
                   <button class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold text-sm whitespace-nowrap">Todas</button>
                   <button class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-4 py-2 rounded-lg font-bold text-sm whitespace-nowrap text-slate-600 dark:text-slate-300">Ventas</button>
                   <button class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-4 py-2 rounded-lg font-bold text-sm whitespace-nowrap text-slate-600 dark:text-slate-300">Seguimiento</button>
                </div>
                
                <div v-if="historialRutas.length > 0" class="space-y-4">
                    <div v-for="ruta in historialRutas" :key="ruta.id" class="card-driver p-4">
                       <div class="flex justify-between mb-2">
                           <span class="text-sm text-slate-500 font-bold">{{ formatDateShort(ruta.planned_date) }}</span>
                           <span class="badge-driver bg-slate-100 text-slate-700" v-if="ruta.visit?.result">
                              {{ getResultIcon(ruta.visit.result) }} {{ getResultLabel(ruta.visit.result) }}
                           </span>
                       </div>
                       <h4 class="font-bold text-slate-900 dark:text-white mb-1">{{ ruta.client?.name }}</h4>
                       <p class="text-sm text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900 p-2 rounded italic mb-0">
                          "{{ ruta.visit?.quick_notes }}"
                       </p>
                    </div>
                </div>
             </div>
             
             <!-- OTHER TABS -->
             <div v-else key="other" class="text-center py-20 text-slate-500 dark:text-slate-400">
                <div class="text-6xl mb-4">🚧</div>
                <h3 class="text-xl font-bold mb-2">En Construcción</h3>
                <p>Esta sección estará disponible próximamente.</p>
             </div>
           </transition>
         </div>
      </main>
    </div>

    <!-- Modal Checkin -->
    <div v-if="showCheckinModal" class="fixed inset-0 z-[60] flex items-end sm:items-center justify-center bg-slate-900/80 backdrop-blur-sm p-0 sm:p-4 animate-fade-in-up">
       <div class="bg-white dark:bg-slate-900 w-full max-w-lg rounded-t-3xl sm:rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
          
          <!-- Modal Header -->
          <div class="p-5 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-900">
             <div>
                <p class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Check-in para</p>
                <h3 class="text-xl font-bold text-slate-900 dark:text-white truncate max-w-[200px]">{{ rutaActual?.client?.name }}</h3>
             </div>
             <button @click="cerrarCheckin" class="bg-slate-200 dark:bg-slate-800 h-10 w-10 rounded-full flex items-center justify-center text-slate-500 dark:text-slate-400 font-bold hover:bg-slate-300 dark:hover:bg-slate-700 transition">✕</button>
          </div>

          <!-- Modal Body -->
          <div class="flex-1 overflow-y-auto p-5 space-y-6">
             
             <!-- GPS Status -->
             <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 flex items-center gap-3 border border-slate-200 dark:border-slate-700">
                <div class="h-10 w-10 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center flex-shrink-0" v-if="ubicacionActual">
                   📍
                </div>
                <div class="h-10 w-10 rounded-full bg-slate-200 animate-pulse flex-shrink-0" v-else></div>
                
                <div>
                   <p class="text-sm font-bold text-slate-900 dark:text-white">
                      {{ ubicacionActual ? 'Ubicación Detectada' : 'Buscando satélites...' }}
                   </p>
                   <p class="text-xs text-slate-500 dark:text-slate-400" v-if="ubicacionActual">
                      Precisión: ±{{ ubicacionActual.accuracy.toFixed(0) }}m
                   </p>
                </div>
             </div>

             <!-- Result Grid -->
             <div>
                <label class="label-driver">Resultado de la visita</label>
                <div class="grid grid-cols-2 gap-3">
                   <button 
                      v-for="res in resultadosVisita" 
                      :key="res.value"
                      @click="visitResult = res.value"
                      class="h-16 rounded-xl border-2 font-bold flex flex-col items-center justify-center transition-all"
                      :class="visitResult === res.value 
                         ? 'border-indigo-600 bg-indigo-50 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-200' 
                         : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'"
                   >
                      <span class="text-xl">{{ res.icon }}</span>
                      <span class="text-sm">{{ res.label }}</span>
                   </button>
                </div>
             </div>

             <!-- Notes -->
             <div>
                <label class="label-driver">Notas Rápidas</label>
                <input 
                   v-model="quickNotes"
                   type="text" 
                   class="input-driver" 
                   placeholder="Ej: Muy interesado, volver lunes" 
                />
             </div>
             
             <!-- Confirm Check -->
             <label class="flex items-center gap-4 bg-slate-50 dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                 <input type="checkbox" v-model="clienteEncontrado" class="w-6 h-6 accent-indigo-600 rounded">
                 <span class="font-bold text-slate-700 dark:text-slate-200">Cliente encontrado en el sitio</span>
             </label>

          </div>

          <!-- Modal Footer -->
          <div class="p-5 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800">
             <button 
                @click="hacerCheckin" 
                :disabled="!puedeHacerCheckin || cargandoCheckin"
                class="btn-driver-primary disabled:opacity-50 disabled:bg-slate-300"
             >
                {{ cargandoCheckin ? 'Guardando...' : 'CONFIRMAR VISITA' }}
             </button>
          </div>

       </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'ComercialV2',
  data() {
    return {
      // Auth
      seller: null,
      sellerName: 'Vendedor',
      
      // UI State
      activeTab: 'hoy',
      showSidebar: false, // NEW: Sidebar toggle
      showCheckinModal: false,
      
      tabs: [
        { id: 'hoy', label: 'Rutas de Hoy', icon: '🚙' },
        { id: 'historial', label: 'Historial', icon: '📜' },
        { id: 'clientes', label: 'Mis Clientes', icon: '👥' },
        { id: 'resumen', label: 'Estadísticas', icon: '📊' }
      ],
      
      // Data
      routesHoy: [],
      historialRutas: [],
      
      // Modal State
      rutaActual: null,
      ubicacionActual: null,
      visitResult: null,
      quickNotes: '',
      clienteEncontrado: false,
      cargandoCheckin: false,
      
      resultadosVisita: [
        { value: 'venta', label: 'Venta', icon: '💰' },
        { value: 'interesado', label: 'Interesado', icon: '👍' },
        { value: 'seguimiento', label: 'Seguimiento', icon: '👋' },
        { value: 'no_venta', label: 'No Venta', icon: '❌' },
        { value: 'ausente', label: 'Ausente', icon: '🚪' }
      ]
    }
  },
  computed: {
    puedeHacerCheckin() {
       return this.visitResult && this.quickNotes.length > 3 && this.ubicacionActual
    }
  },
  mounted() {
    const sellerData = localStorage.getItem('seller')
    if (!sellerData) return this.$router.push('/login')
    
    this.seller = JSON.parse(sellerData)
    this.sellerName = this.seller.name
    
    this.fetchData()
    this.startGPS()
  },
  methods: {
    toggleSidebar() {
       this.showSidebar = !this.showSidebar
    },
    async fetchData() {
       try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/?seller_id=${this.seller.id}`)
        if(response.ok) {
            const all = await response.json()
            const hoy = new Date().toISOString().split('T')[0]
            this.routesHoy = all.filter(r => r.planned_date?.startsWith(hoy))
            this.historialRutas = all 
        }
       } catch(e) { console.error(e) }
    },
    
    startGPS() {
       if("geolocation" in navigator) {
          navigator.geolocation.watchPosition(
             pos => {
                this.ubicacionActual = {
                   latitude: pos.coords.latitude,
                   longitude: pos.coords.longitude,
                   accuracy: pos.coords.accuracy
                }
             }, 
             err => console.error(err),
             { enableHighAccuracy: true }
          )
       }
    },
    
    iniciarCheckin(ruta) {
       this.rutaActual = ruta
       this.showCheckinModal = true
       this.quickNotes = ''
       this.visitResult = null
       this.clienteEncontrado = false
    },
    
    cerrarCheckin() {
       this.showCheckinModal = false
    },
    
    async hacerCheckin() {
       this.cargandoCheckin = true
       try {
         const payload = {
            route_id: this.rutaActual.id,
            seller_id: this.seller.id,
            client_id: this.rutaActual.client_id,
            latitude: this.ubicacionActual.latitude,
            longitude: this.ubicacionActual.longitude,
            visit_result: this.visitResult,
            quick_notes: this.quickNotes,
            client_found: this.clienteEncontrado
         }
         
         const res = await fetch(`${import.meta.env.VITE_API_URL}/visits/checkin/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
         })
         
         if(res.ok) {
             this.showCheckinModal = false
             this.fetchData() 
             alert("Visita confirmada")
         } else {
             alert("Error al guardar visita")
         }
       } catch(e) {
          alert("Error de conexión")
       } finally {
          this.cargandoCheckin = false
       }
    },
    
    // Helpers
    formatTime(dateStr) {
       if(!dateStr) return '--:--'
       return new Date(dateStr).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    },
    formatDateShort(dateStr) {
       return new Date(dateStr).toLocaleDateString([], {month: 'short', day: 'numeric'})
    },
    getStatusLabel(status) {
       const map = { pending: 'Pendiente', completed: 'Completada', in_progress: 'En curso', cancelled: 'Cancelada' }
       return map[status] || status
    },
    getStatusBadgeClass(status) {
       const map = {
          pending: 'bg-slate-100 text-slate-600',
          completed: 'bg-emerald-100 text-emerald-800',
          in_progress: 'bg-indigo-100 text-indigo-800',
          cancelled: 'bg-rose-100 text-rose-800'
       }
       return map[status] || 'bg-gray-100'
    },
    getResultLabel(res) {
       const r = this.resultadosVisita.find(x => x.value === res)
       return r ? r.label : res
    },
    getResultIcon(res) {
       const r = this.resultadosVisita.find(x => x.value === res)
       return r ? r.icon : ''
    },
    logout() {
       localStorage.removeItem('seller')
       this.$router.push('/login')
    },
    mostrarAplazar(ruta) {
       alert("Funcionalidad de aplazar (TODO)")
    },
    verDetalleVisita(ruta) {
       alert("Detalle visita (TODO)")
    }
  }
}
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
/* Hide scrollbar for Chrome, Safari and Opera */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
/* Hide scrollbar for IE, Edge and Firefox */
.no-scrollbar {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}
</style>
