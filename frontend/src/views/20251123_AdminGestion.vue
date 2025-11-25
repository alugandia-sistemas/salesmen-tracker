<template>
  <div class="min-h-screen bg-white">
    <!-- HEADER -->
    <header class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="px-3 sm:px-4 py-4 sm:py-5">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-10 h-10 bg-black rounded-lg flex items-center justify-center text-white text-xs font-bold">
              AD
            </div>
            <h1 class="text-lg sm:text-xl font-semibold text-black truncate">Alugandia</h1>
          </div>
          <div class="text-right text-xs sm:text-sm">
            <p class="text-black font-medium hidden sm:block">Gestión</p>
            <p class="text-gray-500 text-xs">{{ currentTime }}</p>
          </div>
        </div>
      </div>
    </header>

    <div class="px-3 sm:px-4 py-4 sm:py-8 max-w-7xl mx-auto">
      <!-- TAB NAVIGATION -->
      <div class="flex gap-2 sm:gap-4 mb-8 border-b border-gray-200">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'pb-3 sm:pb-4 font-medium text-sm sm:text-base transition-all border-b-2 whitespace-nowrap',
            activeTab === tab.id 
              ? 'text-black border-b-black' 
              : 'text-gray-400 border-b-transparent hover:text-gray-600'
          ]"
        >
          {{ tab.icon }} <span class="hidden xs:inline">{{ tab.name }}</span>
        </button>
      </div>

      <!-- 1️⃣ GESTIÓN DE CLIENTES -->
      <div v-if="activeTab === 'clientes'" class="space-y-6">
        <div class="flex items-center justify-between gap-2">
          <h2 class="text-2xl sm:text-3xl font-semibold text-black">Clientes</h2>
          <button 
            @click="showClientForm = true; formMode = 'create'; currentClient = null"
            class="bg-black text-white px-3 sm:px-4 py-2 rounded font-medium text-sm hover:bg-gray-900"
          >
            + Nuevo
          </button>
        </div>

        <!-- TABLA CLIENTES -->
        <div class="border border-gray-200 rounded-lg overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700">Nombre</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 hidden sm:table-cell">Dirección</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700">Teléfono</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 hidden md:table-cell">Tipo</th>
                  <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="client in clients" :key="client.id" class="border-b border-gray-100 hover:bg-gray-50">
                  <td class="px-4 py-3 font-medium text-gray-900">{{ client.name }}</td>
                  <td class="px-4 py-3 text-gray-600 hidden sm:table-cell text-xs">{{ client.address }}</td>
                  <td class="px-4 py-3 text-gray-600 text-xs">{{ client.phone }}</td>
                  <td class="px-4 py-3 text-gray-600 text-xs hidden md:table-cell">{{ client.client_type }}</td>
                  <td class="px-4 py-3 text-center">
                    <button 
                      @click="editClient(client)"
                      class="text-blue-600 hover:text-blue-800 font-semibold text-xs mr-2"
                    >
                      Editar
                    </button>
                    <button 
                      @click="deleteClient(client.id)"
                      class="text-red-600 hover:text-red-800 font-semibold text-xs"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="clients.length === 0" class="px-4 py-8 text-center text-gray-500 text-sm">
            Sin clientes
          </div>
        </div>

        <!-- MODAL CREAR/EDITAR CLIENTE -->
        <div v-if="showClientForm" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <div class="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[95vh] overflow-y-auto">
            <div class="bg-white border-b border-gray-200 px-4 sm:px-6 py-4 sticky top-0 z-10 flex items-center justify-between">
              <h2 class="text-lg sm:text-xl font-semibold text-black">
                {{ formMode === 'create' ? 'Nuevo Cliente' : 'Editar Cliente' }}
              </h2>
              <button 
                @click="showClientForm = false"
                class="text-gray-500 hover:text-black font-semibold text-xl w-8 h-8 flex items-center justify-center"
              >
                ✕
              </button>
            </div>

            <div class="p-4 sm:p-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                <input v-model="clientForm.name" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none" placeholder="Ej: Carpintería Valencia" />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Dirección *</label>
                <input v-model="clientForm.address" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none" placeholder="Ej: Av. del Puerto 245" />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono *</label>
                  <input v-model="clientForm.phone" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none" placeholder="963123456" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input v-model="clientForm.email" type="email" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none" />
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Tipo *</label>
                  <select v-model="clientForm.client_type" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none">
                    <option value="">Seleccionar</option>
                    <option value="carpenter">Carpintero</option>
                    <option value="installer">Instalador</option>
                    <option value="industrial">Industrial</option>
                    <option value="lead">Lead</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                  <select v-model="clientForm.status" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none">
                    <option value="active">Activo</option>
                    <option value="inactive">Inactivo</option>
                    <option value="pending">Pendiente</option>
                  </select>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Latitud *</label>
                  <input v-model.number="clientForm.latitude" type="number" step="0.0001" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none" placeholder="39.4699" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Longitud *</label>
                  <input v-model.number="clientForm.longitude" type="number" step="0.0001" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none" placeholder="-0.3763" />
                </div>
              </div>

              <div class="flex gap-3 pt-4 border-t border-gray-200">
                <button 
                  @click="showClientForm = false"
                  class="flex-1 bg-gray-200 hover:bg-gray-300 text-black font-medium py-2 px-4 rounded"
                >
                  Cancelar
                </button>
                <button 
                  @click="saveClient"
                  class="flex-1 bg-black hover:bg-gray-900 text-white font-medium py-2 px-4 rounded"
                >
                  {{ formMode === 'create' ? 'Crear' : 'Actualizar' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2️⃣ GESTIÓN DE RUTAS -->
      <div v-if="activeTab === 'rutas'" class="space-y-6">
        <div class="flex items-center justify-between gap-2">
          <h2 class="text-2xl sm:text-3xl font-semibold text-black">Rutas</h2>
          <button 
            @click="showRouteForm = true; formMode = 'create'; currentRoute = null"
            class="bg-black text-white px-3 sm:px-4 py-2 rounded font-medium text-sm hover:bg-gray-900"
          >
            + Nueva
          </button>
        </div>

        <!-- TABLA RUTAS -->
        <div class="border border-gray-200 rounded-lg overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700">Vendedor</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700">Cliente</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 hidden sm:table-cell">Fecha</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700">Hora</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 hidden md:table-cell">Estado</th>
                  <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="route in routes" :key="route.id" class="border-b border-gray-100 hover:bg-gray-50">
                  <td class="px-4 py-3 font-medium text-gray-900 text-xs">{{ route.seller?.name }}</td>
                  <td class="px-4 py-3 text-gray-600 text-xs">{{ route.client?.name }}</td>
                  <td class="px-4 py-3 text-gray-600 text-xs hidden sm:table-cell">{{ formatDate(route.planned_date) }}</td>
                  <td class="px-4 py-3 text-gray-600 text-xs">{{ route.planned_time }}</td>
                  <td class="px-4 py-3 text-gray-600 text-xs hidden md:table-cell">{{ route.status }}</td>
                  <td class="px-4 py-3 text-center">
                    <button 
                      @click="editRoute(route)"
                      class="text-blue-600 hover:text-blue-800 font-semibold text-xs mr-2"
                    >
                      Editar
                    </button>
                    <button 
                      @click="deleteRoute(route.id)"
                      class="text-red-600 hover:text-red-800 font-semibold text-xs"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="routes.length === 0" class="px-4 py-8 text-center text-gray-500 text-sm">
            Sin rutas
          </div>
        </div>

        <!-- MODAL CREAR/EDITAR RUTA -->
        <div v-if="showRouteForm" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <div class="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[95vh] overflow-y-auto">
            <div class="bg-white border-b border-gray-200 px-4 sm:px-6 py-4 sticky top-0 z-10 flex items-center justify-between">
              <h2 class="text-lg sm:text-xl font-semibold text-black">
                {{ formMode === 'create' ? 'Nueva Ruta' : 'Editar Ruta' }}
              </h2>
              <button 
                @click="showRouteForm = false"
                class="text-gray-500 hover:text-black font-semibold text-xl w-8 h-8 flex items-center justify-center"
              >
                ✕
              </button>
            </div>

            <div class="p-4 sm:p-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Vendedor *</label>
                <select v-model="routeForm.seller_id" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none">
                  <option value="">Seleccionar</option>
                  <option v-for="seller in sellers" :key="seller.id" :value="seller.id">{{ seller.name }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Cliente *</label>
                <select v-model="routeForm.client_id" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none">
                  <option value="">Seleccionar</option>
                  <option v-for="client in clients" :key="client.id" :value="client.id">{{ client.name }}</option>
                </select>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Fecha *</label>
                  <input v-model="routeForm.planned_date" type="date" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Hora *</label>
                  <input v-model="routeForm.planned_time" type="time" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none" />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                <select v-model="routeForm.status" class="w-full px-3 py-2 border border-gray-200 rounded focus:border-black focus:outline-none">
                  <option value="pending">Pendiente</option>
                  <option value="in_progress">En progreso</option>
                  <option value="completed">Completada</option>
                  <option value="cancelled">Cancelada</option>
                </select>
              </div>

              <div class="flex gap-3 pt-4 border-t border-gray-200">
                <button 
                  @click="showRouteForm = false"
                  class="flex-1 bg-gray-200 hover:bg-gray-300 text-black font-medium py-2 px-4 rounded"
                >
                  Cancelar
                </button>
                <button 
                  @click="saveRoute"
                  class="flex-1 bg-black hover:bg-gray-900 text-white font-medium py-2 px-4 rounded"
                >
                  {{ formMode === 'create' ? 'Crear' : 'Actualizar' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_URL = 'http://localhost:8000'

const activeTab = ref('clientes')
const currentTime = ref('')

const tabs = [
  { id: 'clientes', name: 'Clientes', icon: '◆' },
  { id: 'rutas', name: 'Rutas', icon: '→' }
]

// CLIENTES
const clients = ref([])
const sellers = ref([])
const showClientForm = ref(false)
const formMode = ref('create')
const currentClient = ref(null)
const clientForm = ref({
  name: '',
  address: '',
  phone: '',
  email: '',
  client_type: '',
  status: 'active',
  latitude: null,
  longitude: null
})

// RUTAS
const routes = ref([])
const showRouteForm = ref(false)
const currentRoute = ref(null)
const routeForm = ref({
  seller_id: '',
  client_id: '',
  planned_date: '',
  planned_time: '',
  status: 'pending'
})

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-ES', { weekday: 'short', month: 'short', day: 'numeric' })
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

// CRUD CLIENTES
const loadClients = async () => {
  try {
    const response = await fetch(`${API_URL}/clients/`)
    clients.value = await response.json()
  } catch (error) {
    console.error('Error:', error)
  }
}

const saveClient = async () => {
  try {
    const method = formMode.value === 'create' ? 'POST' : 'PUT'
    const url = formMode.value === 'create' ? `${API_URL}/clients/` : `${API_URL}/clients/${currentClient.value.id}`
    
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(clientForm.value)
    })

    if (response.ok) {
      showClientForm.value = false
      await loadClients()
      resetClientForm()
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const editClient = (client) => {
  formMode.value = 'edit'
  currentClient.value = client
  clientForm.value = { ...client }
  showClientForm.value = true
}

const deleteClient = async (clientId) => {
  if (!confirm('¿Eliminar este cliente?')) return
  
  try {
    const response = await fetch(`${API_URL}/clients/${clientId}`, { method: 'DELETE' })
    if (response.ok) {
      await loadClients()
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const resetClientForm = () => {
  clientForm.value = {
    name: '',
    address: '',
    phone: '',
    email: '',
    client_type: '',
    status: 'active',
    latitude: null,
    longitude: null
  }
}

// CRUD RUTAS
const loadRoutes = async () => {
  try {
    const response = await fetch(`${API_URL}/routes/`)
    routes.value = await response.json()
  } catch (error) {
    console.error('Error:', error)
  }
}

const saveRoute = async () => {
  try {
    const method = formMode.value === 'create' ? 'POST' : 'PUT'
    const url = formMode.value === 'create' ? `${API_URL}/routes/` : `${API_URL}/routes/${currentRoute.value.id}`
    
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(routeForm.value)
    })

    if (response.ok) {
      showRouteForm.value = false
      await loadRoutes()
      resetRouteForm()
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const editRoute = (route) => {
  formMode.value = 'edit'
  currentRoute.value = route
  routeForm.value = {
    seller_id: route.seller_id,
    client_id: route.client_id,
    planned_date: route.planned_date.split('T')[0],
    planned_time: route.planned_time,
    status: route.status
  }
  showRouteForm.value = true
}

const deleteRoute = async (routeId) => {
  if (!confirm('¿Eliminar esta ruta?')) return
  
  try {
    const response = await fetch(`${API_URL}/routes/${routeId}`, { method: 'DELETE' })
    if (response.ok) {
      await loadRoutes()
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const resetRouteForm = () => {
  routeForm.value = {
    seller_id: '',
    client_id: '',
    planned_date: '',
    planned_time: '',
    status: 'pending'
  }
}

onMounted(async () => {
  updateTime()
  setInterval(updateTime, 1000)
  
  await loadClients()
  await loadSellers()
  await loadRoutes()
})

const loadSellers = async () => {
  try {
    const response = await fetch(`${API_URL}/sellers/`)
    sellers.value = await response.json()
  } catch (error) {
    console.error('Error:', error)
  }
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
</style>
