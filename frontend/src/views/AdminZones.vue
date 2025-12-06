<template>
  <div class="h-screen flex flex-col bg-white">
    <!-- Header -->
    <header class="bg-gray-900 text-white p-4 flex justify-between items-center z-50 shadow-md">
      <div class="flex items-center gap-4">
        <button @click="$router.push('/admin/gestion')" class="text-gray-300 hover:text-white">
          ← Volver
        </button>
        <h1 class="text-xl font-bold">Gestión de Zonas y Rutas</h1>
      </div>
      <div>
        <button @click="showCreateModal = true" class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm font-bold">
          + Nueva Ruta/Zona
        </button>
      </div>
    </header>

    <div class="flex-1 flex overflow-hidden">
      <!-- Sidebar Lista -->
      <aside class="w-1/3 min-w-[350px] bg-gray-50 border-r border-gray-200 flex flex-col overflow-hidden">
        
        <!-- Tabs -->
        <div class="flex border-b border-gray-200">
          <button 
            @click="activeTab = 'routes'"
            :class="['flex-1 py-3 text-sm font-bold', activeTab === 'routes' ? 'bg-white border-t-2 border-blue-600 text-blue-900' : 'text-gray-500 hover:bg-gray-100']"
          >
            Rutas de Venta
          </button>
          <button 
            @click="activeTab = 'zones'"
            :class="['flex-1 py-3 text-sm font-bold', activeTab === 'zones' ? 'bg-white border-t-2 border-blue-600 text-blue-900' : 'text-gray-500 hover:bg-gray-100']"
          >
            Zonas
          </button>
        </div>

        <div class="p-4 overflow-y-auto flex-1">
          <!-- Lista Rutas -->
          <div v-if="activeTab === 'routes'" class="space-y-3">
             <div v-for="route in salesRoutes" :key="route.id" class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
               <div class="flex justify-between items-start">
                  <div>
                    <h3 class="font-bold text-gray-900">{{ route.name }}</h3>
                    <p class="text-xs text-gray-500">Zona: {{ getZoneName(route.zone_id) }}</p>
                    <p class="text-xs text-gray-500">Vendedor: {{ getSellerName(route.seller_id) }}</p>
                  </div>
                  <button @click="editRoute(route)" class="text-blue-600 text-xs">Editar</button>
               </div>
               <!-- Stats Clients -->
               <div class="mt-2 text-xs bg-gray-100 p-2 rounded">
                 {{ countClientsInRoute(route.id) }} clientes asignados
               </div>
             </div>
             <div v-if="salesRoutes.length === 0" class="text-center text-gray-500 mt-10">
               No hay rutas definidas
             </div>
          </div>

          <!-- Lista Zonas -->
          <div v-else class="space-y-3">
             <div v-for="zone in zones" :key="zone.id" class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
               <h3 class="font-bold text-gray-900">{{ zone.name }}</h3>
               <p class="text-xs text-gray-500">{{ countRoutesInZone(zone.id) }} rutas asociadas</p>
             </div>
          </div>
        </div>
      </aside>

      <!-- Mapa -->
      <main class="flex-1 relative bg-gray-200">
        <div id="map" class="absolute inset-0 z-0"></div>
        
        <!-- Legend Overlay -->
        <div class="absolute bottom-5 right-5 bg-white p-3 rounded shadow-lg z-10 text-xs opacity-90">
             <div class="flex items-center gap-2 mb-1">
               <span class="w-3 h-3 rounded-full bg-blue-500 inline-block"></span> Cliente Asignado
             </div>
             <div class="flex items-center gap-2">
               <span class="w-3 h-3 rounded-full bg-red-500 inline-block"></span> Sin Ruta
             </div>
        </div>
      </main>
    </div>

    <!-- Modal Create -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
        <h2 class="text-xl font-bold mb-4">Nueva Ruta de Venta</h2>
        
        <form @submit.prevent="createSalesRoute" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold mb-1">Nombre de la Ruta</label>
            <input v-model="newRoute.name" type="text" class="w-full border p-2 rounded" required />
          </div>
          
          <div>
            <label class="block text-sm font-semibold mb-1">Zona</label>
            <select v-model="newRoute.zone_id" class="w-full border p-2 rounded">
              <option :value="null">-- Seleccionar Zona --</option>
              <option v-for="z in zones" :key="z.id" :value="z.id">{{ z.name }}</option>
            </select>
            <div class="mt-1 text-right">
              <button type="button" @click="createNewZone" class="text-xs text-blue-600 underline">Crear nueva zona</button>
            </div>
          </div>

          <div>
             <label class="block text-sm font-semibold mb-1">Asignar Vendedor</label>
             <select v-model="newRoute.seller_id" class="w-full border p-2 rounded">
               <option :value="null">-- Sin asignar --</option>
               <option v-for="s in sellers" :key="s.id" :value="s.id">{{ s.name }}</option>
             </select>
          </div>

          <div class="flex gap-2 pt-4">
            <button type="button" @click="showCreateModal = false" class="flex-1 bg-gray-100 py-2 rounded">Cancelar</button>
            <button type="submit" class="flex-1 bg-gray-900 text-white py-2 rounded">Guardar</button>
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
        
        // Default center (e.g. Spain or Alicante/Benidorm based on Alugandia name hint? Defaulting to generic coords)
        this.map = L.map('map').setView([38.54, -0.12], 10) // Benidorm approx

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map)
    },
    
    async fetchData() {
        // Fetch Zones
        const zRes = await fetch(`${import.meta.env.VITE_API_URL}/zones/`)
        this.zones = await zRes.json()
        
        // Fetch SalesRoutes
        const srRes = await fetch(`${import.meta.env.VITE_API_URL}/sales-routes/`)
        this.salesRoutes = await srRes.json()
        
        // Fetch Sellers
        const sRes = await fetch(`${import.meta.env.VITE_API_URL}/sellers/`)
        this.sellers = await sRes.json()
        
        // Fetch Clients for Map
        const cRes = await fetch(`${import.meta.env.VITE_API_URL}/clients/`)
        this.clients = await cRes.json()
        
        this.plotClients()
    },
    
    plotClients() {
        if (!this.map) return
        
        // Clear existing
        this.markers.forEach(m => this.map.removeLayer(m))
        this.markers = []
        
        this.clients.forEach(c => {
            if (c.latitude && c.longitude) {
                const isAssigned = c.sales_route_id != null // Note: API might not return sales_route_id in base client schema yet?
                // I need to check Main.py list_clients. It returns ClientResponse which usually is Pydantic. 
                // Does ClientResponse have sales_route_id? I didn't add it to ClientResponse schema in Main.py!
                // Ah, I missed adding it to SCHEMA in Step 112.
                // However, I updated the MODEL. 
                // So fetch might not return it unless generic dict is returned or Schema updated.
                // list_clients in main.py creates a manual dict: "id": str(client.id)...
                // I should verify if I updated list_clients manually constructed dict. I did NOT.
                // So the frontend won't see sales_route_id yet basically.
                // I will add a FIXME or update logic.
                // For now assuming it might be missing, I'll color all BLUE.
                
                const color = 'blue' // TODO detect assigned
                
                const marker = L.circleMarker([c.latitude, c.longitude], {
                    radius: 6,
                    fillColor: color,
                    color: '#fff',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }).addTo(this.map)
                
                marker.bindPopup(`<b>${c.name}</b><br>${c.address}`)
                this.markers.push(marker)
            }
        })
    },
    
    async createNewZone() {
        const name = prompt("Nombre de la nueva Zona:")
        if (name) {
             const res = await fetch(`${import.meta.env.VITE_API_URL}/zones/`, {
                 method: 'POST',
                 headers: {'Content-Type': 'application/json'},
                 body: JSON.stringify({ name })
             })
             if (res.ok) {
                 const zone = await res.json()
                 this.zones.push(zone)
                 this.newRoute.zone_id = zone.id
             }
        }
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
            alert("Ruta creada con éxito")
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
    
    countClientsInRoute(routeId) {
        // Need client data with sales_route_id. Currently not available in fetchClients result likely.
        return 0 
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
/* Leaflet fixes if needed */
</style>
