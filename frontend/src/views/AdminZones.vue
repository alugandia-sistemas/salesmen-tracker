<template>
  <div class="h-screen flex flex-col bg-slate-50 dark:bg-slate-900 overflow-hidden relative">
    <!-- Header -->
    <header class="bg-slate-900 text-white p-4 flex justify-between items-center z-[50] shadow-lg border-b border-slate-800 shrink-0 h-16">
      <div class="flex items-center gap-3">
        <!-- Mobile Sidebar Toggle -->
        <button @click="toggleSidebar" class="md:hidden text-white p-1 rounded hover:bg-slate-800">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
           </svg>
        </button>
        
        <button @click="$router.push('/admin/gestion')" class="text-slate-400 hover:text-white transition-colors">
          ← <span class="hidden md:inline">Volver</span>
        </button>
        <h1 class="text-lg md:text-xl font-bold bg-gradient-to-r from-indigo-400 to-indigo-200 bg-clip-text text-transparent truncate max-w-[150px] md:max-w-none">
          Gestión Zonas
        </h1>
      </div>
      <div>
        <button @click="showCreateModal = true" class="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-2 md:px-5 md:py-2.5 rounded-lg text-xs md:text-sm font-bold shadow-md transition-all whitespace-nowrap">
          + <span class="hidden md:inline">Nueva Ruta/Zona</span><span class="md:hidden">Nuevo</span>
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

      <!-- Sidebar Lista -->
      <aside 
         class="absolute md:relative inset-y-0 left-0 w-4/5 md:w-1/3 min-w-[280px] md:min-w-[350px] bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col shadow-2xl z-30 transition-transform duration-300 transform"
         :class="showSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
      >
        
        <!-- Tabs -->
        <div class="flex border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 shrink-0">
          <button 
            @click="activeTab = 'routes'"
            :class="['flex-1 py-4 text-sm font-bold transition-colors', activeTab === 'routes' ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 border-t-2 border-indigo-600' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800']"
          >
            Rutas
          </button>
          <button 
            @click="activeTab = 'zones'"
            :class="['flex-1 py-4 text-sm font-bold transition-colors', activeTab === 'zones' ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 border-t-2 border-indigo-600' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800']"
          >
            Zonas
          </button>
        </div>

        <div class="p-4 overflow-y-auto flex-1 space-y-3 bg-slate-50/50 dark:bg-slate-900/50 pb-20 md:pb-4">
          <!-- Lista Rutas -->
          <transition-group name="fade" tag="div" v-if="activeTab === 'routes'" class="space-y-3">
             <div v-for="route in salesRoutes" :key="route.id" class="group bg-white dark:bg-slate-800 p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 hover:border-indigo-400 dark:hover:border-indigo-500 transition-all cursor-pointer">
               <div class="flex justify-between items-start">
                  <div>
                    <h3 class="font-bold text-slate-900 dark:text-white text-lg">{{ route.name }}</h3>
                    <div class="flex items-center gap-2 mt-1 flex-wrap">
                       <span class="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded">
                          {{ getZoneName(route.zone_id) }}
                       </span>
                       <span class="text-xs text-slate-500 dark:text-slate-400 truncate max-w-[150px]">
                          👤 {{ getSellerName(route.seller_id) }}
                       </span>
                    </div>
                  </div>
                  <button @click.stop="editRoute(route)" class="text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900 p-2 rounded-lg transition-colors">
                     ✏️
                  </button>
               </div>
             </div>
             <div v-if="salesRoutes.length === 0" class="text-center py-10">
               <div class="bg-slate-200 dark:bg-slate-700 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3">
                  🗺️
               </div>
               <p class="text-slate-500 dark:text-slate-400">No hay rutas definidas</p>
             </div>
          </transition-group>

          <!-- Lista Zonas -->
          <transition-group name="fade" tag="div" v-else class="space-y-3">
             <div v-for="zone in zones" :key="zone.id" class="bg-white dark:bg-slate-800 p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
               <div class="flex justify-between items-center">
                   <h3 class="font-bold text-slate-900 dark:text-white text-lg">{{ zone.name }}</h3>
                   <span class="text-xs bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded text-slate-600 dark:text-slate-300">
                      {{ countRoutesInZone(zone.id) }} rutas
                   </span>
               </div>
             </div>
          </transition-group>
        </div>
      </aside>

      <!-- Mapa -->
      <main class="flex-1 relative bg-slate-200 dark:bg-slate-900 w-full h-full">
        <div id="map" class="absolute inset-0 z-0"></div>
        
        <!-- Legend Overlay -->
        <div class="absolute bottom-6 right-6 md:bottom-6 md:right-6 bg-white/90 dark:bg-slate-800/90 backdrop-blur p-4 rounded-xl shadow-xl z-10 text-xs border border-slate-200 dark:border-slate-700 hidden md:block">
             <h4 class="font-bold text-slate-700 dark:text-slate-200 mb-2 uppercase tracking-wide">Leyenda</h4>
             <div class="flex items-center gap-2 mb-2">
               <span class="w-3 h-3 rounded-full bg-blue-500 inline-block shadow-sm"></span> 
               <span class="text-slate-600 dark:text-slate-300">Cliente Asignado</span>
             </div>
             <div class="flex items-center gap-2">
               <span class="w-3 h-3 rounded-full bg-rose-500 inline-block shadow-sm"></span> 
               <span class="text-slate-600 dark:text-slate-300">Sin Ruta</span>
             </div>
        </div>
      </main>
    </div>

    <!-- Modal Create -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in-up">
        <div class="bg-slate-50 dark:bg-slate-900 p-6 border-b border-slate-100 dark:border-slate-700">
           <h2 class="text-xl font-bold text-slate-900 dark:text-white">Nueva Ruta de Venta</h2>
        </div>
        
        <form @submit.prevent="createSalesRoute" class="p-6 space-y-5">
          <div>
            <label class="label-driver">Nombre de la Ruta</label>
            <input v-model="newRoute.name" type="text" class="input-driver h-12 text-base" placeholder="Ej: Ruta Alicante Norte" required />
          </div>
          
          <div>
            <label class="label-driver">Zona</label>
            <select v-model="newRoute.zone_id" class="input-driver h-12 text-base">
              <option :value="null">-- Seleccionar Zona --</option>
              <option v-for="z in zones" :key="z.id" :value="z.id">{{ z.name }}</option>
            </select>
            <div class="mt-2 text-right">
              <button type="button" @click="createNewZone" class="text-sm font-bold text-indigo-600 dark:text-indigo-400 hover:underline">
                 + Crear nueva zona
              </button>
            </div>
          </div>

          <div>
             <label class="label-driver">Asignar Vendedor</label>
             <select v-model="newRoute.seller_id" class="input-driver h-12 text-base">
               <option :value="null">-- Sin asignar --</option>
               <option v-for="s in sellers" :key="s.id" :value="s.id">{{ s.name }}</option>
             </select>
          </div>

          <div class="flex gap-3 pt-4">
            <button type="button" @click="showCreateModal = false" class="btn-driver-secondary h-12 text-base">Cancelar</button>
            <button type="submit" class="btn-driver-primary h-12 text-base">Guardar Ruta</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminZones",
  data() {
    return {
      map: null,
      markers: [],
      
      activeTab: 'routes',
      showCreateModal: false,
      showSidebar: false,
      
      zones: [],
      salesRoutes: [],
      sellers: [],
      clients: [],
      
      newRoute: {
        name: '',
        zone_id: null,
        seller_id: null
      }
    }
  },
  mounted() {
    this.initMap()
    this.fetchData()
  },
  methods: {
    initMap() {
        if (!window.L) return
        
        // Default center
        this.map = L.map('map', {
            zoomControl: false 
        }).setView([38.96, -0.18], 11) // Gandia/Real

        L.control.zoom({ position: 'bottomright' }).addTo(this.map)

        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap contributors © CARTO',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(this.map)

        // --- LEAFLET DRAW SETUP ---
        // FeatureGroup is to store editable layers
        this.drawnItems = new L.FeatureGroup()
        this.map.addLayer(this.drawnItems)

        // Init Draw Control
        const drawControl = new L.Control.Draw({
            draw: {
                polygon: true,
                polyline: false,
                rectangle: true, 
                circle: false,
                marker: false,
                circlemarker: false
            },
            edit: {
                featureGroup: this.drawnItems,
                remove: true
            }
        })
        this.map.addControl(drawControl)

        // Event Handler
        this.map.on(L.Draw.Event.CREATED, (e) => {
            const layer = e.layer
            this.drawnItems.clearLayers() // Only allow one zone being drawn at a time for simplicity? 
            // Or allow multiple? Let's stick to one new zone creation at a time.
            this.drawnItems.addLayer(layer)
            
            // Auto trigger creation modal if desired, or just store it
            // Let's store it and prompt user
            this.tempLayer = layer
            this.promptCreateZone()
        })
    },
    
    // ... existing fetchData ...

    // ... existing plotClients ...

    toWKT(layer) {
        if (!layer) return null
        
        // Simple Polygon WKT: POLYGON((lng lat, lng lat, ...))
        // Leaflet LatLngs: [{lat, lng}, ...]
        // Note: Polygon might have holes, but let's assume simple polygon for now
        // Also handling Rectangle (bounds -> polygon)
        
        let latlngs = layer.getLatLngs()
        
        // Handle nested arrays (MultiPolygon or Polygon with holes)
        // Leaflet Polygon.getLatLngs() returns [ [LatLng, LatLng, ...] ] for simple polygon
        if (Array.isArray(latlngs[0]) && !('lat' in latlngs[0])) {
             latlngs = latlngs[0]
        }
        
        // Close the loop
        const points = latlngs.map(p => `${p.lng} ${p.lat}`)
        points.push(`${latlngs[0].lng} ${latlngs[0].lat}`) // Close loop
        
        return `POLYGON((${points.join(', ')}))`
    },

    promptCreateZone() {
        // Simple prompt flow or open modal
        // Let's use the prompt flow first for simplicity 
        // Or better: Open a specific "Save Zone" modal? 
        // For compliance with current UI, let's reuse createNewZone logic but autoset geometry
        
        const name = prompt("Has dibujado una zona. ¿Nombre de la nueva Zona?")
        if (name) {
             this.createNewZoneWithGeometry(name, this.toWKT(this.tempLayer))
        } else {
             this.drawnItems.removeLayer(this.tempLayer)
        }
    },
    
    async createNewZoneWithGeometry(name, wkt) {
         try {
             const res = await fetch(`${import.meta.env.VITE_API_URL}/zones/`, {
                 method: 'POST',
                 headers: {'Content-Type': 'application/json'},
                 body: JSON.stringify({ name, geometry: wkt })
             })
             if (res.ok) {
                 const zone = await res.json()
                 this.zones.push(zone)
                 this.drawnItems.clearLayers()
                 
                 // FIX: Switch tab to ensure visibility
                 this.activeTab = 'zones'
                 // Open sidebar on mobile if closed
                 this.showSidebar = true
                 
                 alert("Zona creada exitosamente")
             } else {
                 alert("Error al crear zona")
             }
         } catch (e) {
             console.error(e)
             alert("Error de conexión")
         }
    },

    async createNewZone() {
        // Fallback for non-drawing creation
        const name = prompt("Nombre de la nueva Zona (Sin geometría):")
        if (name) {
             this.createNewZoneWithGeometry(name, null)
        }
    },
    
    toggleSidebar() {
        this.showSidebar = !this.showSidebar
    },
    
    async createSalesRoute() {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/sales-routes/`, {
             method: 'POST',
             headers: {'Content-Type': 'application/json'},
             body: JSON.stringify(this.newRoute)
        })
        
        if (res.ok) {
            const route = await res.json()
            this.salesRoutes.push(route)
            this.showCreateModal = false
        } else {
            alert("Error creando ruta")
        }
    },
    
    getZoneName(id) {
        const z = this.zones.find(x => x.id === id)
        return z ? z.name : 'Sin Zona'
    },
    
    getSellerName(id) {
        const s = this.sellers.find(x => x.id === id)
        return s ? s.name : 'Sin Asignar'
    },
    
    countRoutesInZone(zoneId) {
        return this.salesRoutes.filter(r => r.zone_id === zoneId).length
    },
    
    editRoute(route) {
        // TODO simple name edit
        const newName = prompt("Nuevo nombre:", route.name)
        if (newName) {
            // Update logic
        }
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
</style>
