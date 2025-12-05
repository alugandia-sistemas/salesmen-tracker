<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="px-4 py-4">
        <div class="flex justify-between items-center mb-4">
          <h1 class="text-2xl font-bold text-gray-900">Alugandia</h1>
          <button @click="logout" class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-800 transition">
            Salir
          </button>
        </div>
        <p class="text-gray-600 text-sm">Panel de Administración</p>
      </div>
    </nav>

    <!-- Tabs/Navigation -->
    <div class="bg-white border-b border-gray-200 sticky top-16 z-40">
      <div class="px-4 py-0 flex gap-0 overflow-x-auto">
        <button 
          @click="activeTab = 'vendedores'"
          :class="[
            'px-4 py-4 font-semibold text-sm border-b-2 transition whitespace-nowrap',
            activeTab === 'vendedores' 
              ? 'border-gray-900 text-gray-900' 
              : 'border-transparent text-gray-600 hover:text-gray-900'
          ]"
        >
          👥 Vendedores
        </button>     
        <button 
          @click="activeTab = 'clientes'"
          :class="[
            'px-4 py-4 font-semibold text-sm border-b-2 transition whitespace-nowrap',
            activeTab === 'clientes' 
              ? 'border-gray-900 text-gray-900' 
              : 'border-transparent text-gray-600 hover:text-gray-900'
          ]"
        >
          🏢 Clientes
        </button>
        <button 
          @click="activeTab = 'rutas'"
          :class="[
            'px-4 py-4 font-semibold text-sm border-b-2 transition whitespace-nowrap',
            activeTab === 'rutas' 
              ? 'border-gray-900 text-gray-900' 
              : 'border-transparent text-gray-600 hover:text-gray-900'
          ]"
        >
          🗺️ Rutas
        </button>

        <button 
          @click="$router.push('/admin/invitaciones')"
          class="px-4 py-4 font-semibold text-sm border-b-2 border-transparent text-gray-600 hover:text-gray-900 transition whitespace-nowrap"
        >
          📧 Invitaciones
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="px-4 py-6 pb-20">
      <!-- VENDEDORES TAB -->
      <div v-if="activeTab === 'vendedores'">
        <div class="mb-6">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Vendedores</h2>
          <button 
            @click="showVendedorModal = true" 
            class="w-full bg-gray-900 text-white py-4 rounded-xl font-semibold text-lg hover:bg-gray-800 transition"
          >
            + Nuevo Vendedor
          </button>
        </div>

        <div v-if="vendedores.length > 0" class="space-y-3">
          <div v-for="vendedor in vendedores" :key="vendedor.id" class="bg-white border-2 border-gray-200 rounded-xl p-5">
            <div class="flex items-start gap-4 mb-4">
              <div class="w-14 h-14 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold text-lg">{{ vendedor.name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-lg font-bold text-gray-900">{{ vendedor.name }}</h3>
                <p class="text-gray-600 text-sm truncate">{{ vendedor.email }}</p>
              </div>
            </div>
            <div class="space-y-2 mb-4">
              <p class="text-gray-700 text-sm">📞 {{ vendedor.phone }}</p>
              <span class="inline-block px-3 py-1 rounded-full text-sm font-semibold"
                :class="vendedor.is_active ? 'bg-gray-200 text-gray-900' : 'bg-gray-100 text-gray-600'">
                {{ vendedor.is_active ? '✓ Activo' : '• Inactivo' }}
              </span>
            </div>
            <div class="flex gap-2">
              <button @click="editVendedor(vendedor)" class="flex-1 bg-gray-100 text-gray-900 py-3 rounded-lg font-semibold text-sm hover:bg-gray-200 transition">
                Editar
              </button>
              <button @click="deleteVendedor(vendedor.id)" class="flex-1 bg-gray-900 text-white py-3 rounded-lg font-semibold text-sm hover:bg-gray-800 transition">
                Eliminar
              </button>
            </div>
          </div>
        </div>
        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-600 text-sm mb-4">Sin vendedores registrados</p>
          <button @click="showVendedorModal = true" class="w-full bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition">
            Crear Vendedor
          </button>
        </div>
      </div>

      <!-- CLIENTES TAB -->
      <div v-if="activeTab === 'clientes'">
        <div class="mb-6">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Clientes</h2>
          
          <!-- ✅ ACCESO RÁPIDO AL DIRECTORIO -->
          <div class="grid grid-cols-2 gap-3 mb-4">
            <button 
              @click="$router.push('/admin/clientes')"
              class="bg-gray-100 text-gray-900 border-2 border-gray-300 py-4 rounded-xl font-semibold text-base hover:bg-gray-200 transition"
            >
              📋 Directorio
            </button>
            <button 
              @click="showClienteModal = true" 
              class="bg-gray-900 text-white py-4 rounded-xl font-semibold text-base hover:bg-gray-800 transition"
            >
              + Nuevo Cliente
            </button>
          </div>

          <!-- Stats rápidos -->
          <div class="grid grid-cols-3 gap-2 mb-4">
            <div class="bg-gray-50 rounded-lg p-3 text-center border border-gray-200">
              <p class="text-2xl font-bold text-gray-900">{{ contarPorTipo('carpintero_metalico') }}</p>
              <p class="text-xs text-gray-600">Carpinteros</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 text-center border border-gray-200">
              <p class="text-2xl font-bold text-gray-900">{{ contarPorTipo('cristalero') }}</p>
              <p class="text-xs text-gray-600">Cristaleros</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 text-center border border-gray-200">
              <p class="text-2xl font-bold text-gray-900">{{ contarPorTipo('taller') }}</p>
              <p class="text-xs text-gray-600">Talleres</p>
            </div>
          </div>
        </div>

        <!-- Lista resumida de clientes recientes -->
        <h3 class="text-lg font-bold text-gray-900 mb-3">Clientes Recientes</h3>
        <div v-if="clientes.length > 0" class="space-y-3">
          <div v-for="cliente in clientesRecientes" :key="cliente.id" class="bg-white border-2 border-gray-200 rounded-xl p-4">
            <div class="flex items-start gap-3">
              <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold">{{ cliente.name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="text-base font-bold text-gray-900 truncate">{{ cliente.name }}</h4>
                <p class="text-gray-600 text-sm truncate">{{ cliente.address }}</p>
                <span class="px-2 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-700 mt-1 inline-block">
                  {{ getTipoCliente(cliente.client_type) }}
                </span>
              </div>
              <button @click="editCliente(cliente)" class="text-gray-400 hover:text-gray-900">✏️</button>
            </div>
          </div>
          
          <button 
            @click="$router.push('/admin/clientes')"
            class="w-full bg-gray-100 text-gray-700 py-3 rounded-lg font-semibold text-sm hover:bg-gray-200 transition"
          >
            Ver todos los clientes ({{ clientes.length }}) →
          </button>
        </div>
        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-600 text-sm mb-4">Sin clientes registrados</p>
          <button @click="showClienteModal = true" class="w-full bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition">
            Crear Cliente
          </button>
        </div>
      </div>

      <!-- RUTAS TAB -->
      <div v-if="activeTab === 'rutas'">
        <div class="mb-6">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Rutas</h2>
          <button 
            @click="showRutaModal = true" 
            class="w-full bg-gray-900 text-white py-4 rounded-xl font-semibold text-lg hover:bg-gray-800 transition"
          >
            + Nueva Ruta
          </button>
        </div>

        <div v-if="rutas.length > 0" class="space-y-3">
          <div v-for="ruta in rutas" :key="ruta.id" class="bg-white border-2 border-gray-200 rounded-xl p-5">
            <div class="mb-4">
              <div class="flex justify-between items-start mb-2">
                <h3 class="text-lg font-bold text-gray-900">{{ getNombreVendedor(ruta.seller_id) }}</h3>
                <span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-200 text-gray-900">
                  {{ ruta.status }}
                </span>
              </div>
              <p class="text-gray-600 text-sm">📍 {{ getNombreCliente(ruta.client_id) }}</p>
            </div>
            <div class="space-y-2 mb-4">
              <p class="text-gray-700 text-sm">📅 {{ formatDate(ruta.planned_date) }}</p>
            </div>
            <div class="flex gap-2">
              <button @click="editRuta(ruta)" class="flex-1 bg-gray-100 text-gray-900 py-3 rounded-lg font-semibold text-sm hover:bg-gray-200 transition">
                Editar
              </button>
              <button @click="deleteRuta(ruta.id)" class="flex-1 bg-gray-900 text-white py-3 rounded-lg font-semibold text-sm hover:bg-gray-800 transition">
                Eliminar
              </button>
            </div>
          </div>
        </div>
        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-600 text-sm mb-4">Sin rutas registradas</p>
          <button @click="showRutaModal = true" class="w-full bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition">
            Crear Ruta
          </button>
        </div>
      </div>
    </div>

    <!-- MODALES -->
    <!-- Modal Vendedor -->
    <div v-if="showVendedorModal" class="fixed inset-0 bg-black/40 flex items-end z-50">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-2xl font-bold text-gray-900 mb-6">
          {{ editingVendedor ? 'Editar Vendedor' : 'Nuevo Vendedor' }}
        </h3>
        <form @submit.prevent="saveVendedor" class="space-y-5">
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Nombre</label>
            <input v-model="formVendedor.name" type="text" placeholder="Ej: Ernesto Arocas" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Email</label>
            <input v-model="formVendedor.email" type="email" placeholder="ernesto@alugandia.com" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Teléfono</label>
            <input v-model="formVendedor.phone" type="tel" placeholder="+34 600 123 456" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required />
          </div>

          <div class="flex items-center gap-3 py-2">
            <input v-model="formVendedor.is_active" type="checkbox" id="vendedor-active" class="w-5 h-5 accent-gray-900" />
            <label for="vendedor-active" class="text-gray-900 font-semibold">Vendedor Activo</label>
          </div>
          <div class="flex gap-3 pt-6 border-t border-gray-200">
            <button type="button" @click="closeVendedorModal()" class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold text-lg hover:bg-gray-200 transition">
              Cancelar
            </button>
            <button type="submit" class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition">
              {{ editingVendedor ? 'Actualizar' : 'Crear' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Cliente -->
    <div v-if="showClienteModal" class="fixed inset-0 bg-black/40 flex items-end z-50">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-2xl font-bold text-gray-900 mb-6">
          {{ editingCliente ? 'Editar Cliente' : 'Nuevo Cliente' }}
        </h3>
        <form @submit.prevent="saveCliente" class="space-y-5">
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Nombre del Cliente</label>
            <input v-model="formCliente.name" type="text" placeholder="Ej: Cerrajería García" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Dirección</label>
            <input v-model="formCliente.address" type="text" placeholder="Ej: Calle Principal 123, Real de Gandia" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Teléfono</label>
            <input v-model="formCliente.phone" type="tel" placeholder="+34 600 123 456" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Email</label>
            <input v-model="formCliente.email" type="email" placeholder="info@cliente.com" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" />
          </div>

          <!-- ✅ CATEGORÍAS ACTUALIZADAS -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Tipo de Cliente</label>
            <select v-model="formCliente.client_type" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required>
              <option value="">-- Selecciona tipo --</option>
              <option value="carpintero_metalico">🔧 Carpintero Metálico</option>
              <option value="cristalero">🪟 Cristalero</option>
              <option value="taller">🏭 Taller Industrial</option>
              <option value="instalador">🔨 Instalador</option>
              <option value="cerrajero">🔑 Cerrajero</option>
              <option value="constructor">🏗️ Constructor</option>
              <option value="otros">📦 Otros</option>
            </select>
          </div>

          <!-- GEOLOCALIZACIÓN -->
          <div class="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mt-6 mb-4">
            <h4 class="font-bold text-blue-900 text-sm mb-2">📍 Geolocalización (PostGIS)</h4>
            <p class="text-blue-800 text-xs mb-3">Necesario para check-in geolocalizado de vendedores</p>

            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">Latitud</label>
              <input v-model.number="formCliente.latitude" type="number" placeholder="39.2000" step="0.0001" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required />
              <p class="text-gray-500 text-xs mt-1">Ej: 39.2000 (Real de Gandia)</p>
            </div>

            <div class="mt-3">
              <label class="block text-sm font-semibold text-gray-900 mb-2">Longitud</label>
              <input v-model.number="formCliente.longitude" type="number" placeholder="-0.1500" step="0.0001" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required />
              <p class="text-gray-500 text-xs mt-1">Ej: -0.1500 (Real de Gandia)</p>
            </div>

            <p class="text-gray-600 text-xs mt-3 bg-gray-100 p-2 rounded">
              💡 Tip: Obtén coordenadas en Google Maps → Click derecho → Copiar coordenadas
            </p>
          </div>
          <div class="flex gap-3 pt-6 border-t border-gray-200">
            <button type="button" @click="closeClienteModal()" class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold text-lg hover:bg-gray-200 transition">
              Cancelar
            </button>
            <button type="submit" class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition">
              {{ editingCliente ? 'Actualizar' : 'Crear' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Ruta -->
    <div v-if="showRutaModal" class="fixed inset-0 bg-black/40 flex items-end z-50">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-2xl font-bold text-gray-900 mb-6">
          {{ editingRuta ? 'Editar Ruta' : 'Nueva Ruta' }}
        </h3>
        <form @submit.prevent="saveRuta" class="space-y-5">
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Vendedor</label>
            <select v-model="formRuta.seller_id" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required>
              <option value="">-- Selecciona vendedor --</option>
              <option v-for="v in vendedores" :key="v.id" :value="v.id">{{ v.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Cliente</label>
            <select v-model="formRuta.client_id" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required>
              <option value="">-- Selecciona cliente --</option>
              <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Fecha de la Ruta</label>
            <input v-model="formRuta.planned_date" type="date" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required />
            <p class="text-gray-500 text-xs mt-1">Ej: 2025-12-02</p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Estado de la Ruta</label>
            <select v-model="formRuta.status" class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" required>
              <option value="pending">⏳ Pendiente</option>
              <option value="in_progress">🚀 En Progreso</option>
              <option value="completed">✅ Completada</option>
              <option value="cancelled">❌ Cancelada</option>
            </select>
          </div>
          <div class="flex gap-3 pt-6 border-t border-gray-200">
            <button type="button" @click="closeRutaModal()" class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold text-lg hover:bg-gray-200 transition">
              Cancelar
            </button>
            <button type="submit" class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition">
              {{ editingRuta ? 'Actualizar' : 'Crear' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminPanel',
  data() {
    return {
      activeTab: 'vendedores',
      vendedores: [],
      clientes: [],
      rutas: [],
      
      showVendedorModal: false,
      showClienteModal: false,
      showRutaModal: false,
      
      editingVendedor: null,
      editingCliente: null,
      editingRuta: null,
      
      formVendedor: { name: '', email: '', phone: '', is_active: true },
      formCliente: { name: '', address: '', phone: '', email: '', latitude: 0, longitude: 0, client_type: '' },
      formRuta: { seller_id: '', client_id: '', planned_date: '', status: 'pending' },
      
      // Mapeo de tipos de cliente
      tiposCliente: {
        'carpintero_metalico': '🔧 Carpintero Metálico',
        'cristalero': '🪟 Cristalero',
        'taller': '🏭 Taller Industrial',
        'instalador': '🔨 Instalador',
        'cerrajero': '🔑 Cerrajero',
        'constructor': '🏗️ Constructor',
        'otros': '📦 Otros',
        // Compatibilidad con tipos antiguos
        'carpenter': '🔧 Carpintero',
        'installer': '🔨 Instalador',
        'industrial': '🏭 Industrial'
      }
    }
  },
  computed: {
    clientesRecientes() {
      // Mostrar solo los 5 más recientes
      return this.clientes.slice(0, 5)
    }
  },
  mounted() {
    this.fetchVendedores()
    this.fetchClientes()
    this.fetchRutas()
    
    // Verificar si viene con tab específico desde query params
    const tab = this.$route.query.tab
    if (tab) {
      this.activeTab = tab
    }
  },
  methods: {
    async fetchVendedores() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/sellers/`)
        this.vendedores = await response.json()
      } catch (e) {
        console.error('Error fetching vendedores:', e)
      }
    },
    async fetchClientes() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/clients/`)
        this.clientes = await response.json()
      } catch (e) {
        console.error('Error fetching clientes:', e)
      }
    },
    async fetchRutas() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/`)
        this.rutas = await response.json()
      } catch (e) {
        console.error('Error fetching rutas:', e)
      }
    },
    
    // Contar clientes por tipo
    contarPorTipo(tipo) {
      return this.clientes.filter(c => c.client_type === tipo).length
    },
    
    // VENDEDORES
    editVendedor(v) {
      this.editingVendedor = v.id
      this.formVendedor = { ...v }
      this.showVendedorModal = true
    },
    async saveVendedor() {
      try {
        const url = this.editingVendedor 
          ? `${import.meta.env.VITE_API_URL}/sellers/${this.editingVendedor}`
          : `${import.meta.env.VITE_API_URL}/sellers/`
        const method = this.editingVendedor ? 'PUT' : 'POST'
        
        await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.formVendedor)
        })
        this.fetchVendedores()
        this.closeVendedorModal()
      } catch (e) {
        console.error('Error saving vendedor:', e)
      }
    },
    async deleteVendedor(id) {
      if (!confirm('¿Eliminar?')) return
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/sellers/${id}`, { method: 'DELETE' })
        this.fetchVendedores()
      } catch (e) {
        console.error('Error deleting vendedor:', e)
      }
    },
    closeVendedorModal() {
      this.showVendedorModal = false
      this.editingVendedor = null
      this.formVendedor = { name: '', email: '', phone: '', is_active: true }
    },
    
    // CLIENTES
    editCliente(c) {
      this.editingCliente = c.id
      this.formCliente = {
        name: c.name,
        address: c.address,
        phone: c.phone,
        email: c.email,
        latitude: c.latitude,
        longitude: c.longitude,
        client_type: c.client_type
      }
      this.showClienteModal = true
    },
    async saveCliente() {
      try {
        const url = this.editingCliente 
          ? `${import.meta.env.VITE_API_URL}/clients/${this.editingCliente}`
          : `${import.meta.env.VITE_API_URL}/clients/`
        const method = this.editingCliente ? 'PUT' : 'POST'
        
        await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.formCliente)
        })
        this.fetchClientes()
        this.closeClienteModal()
      } catch (e) {
        console.error('Error saving cliente:', e)
      }
    },
    async deleteCliente(id) {
      if (!confirm('¿Eliminar?')) return
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/clients/${id}`, { method: 'DELETE' })
        this.fetchClientes()
      } catch (e) {
        console.error('Error deleting cliente:', e)
      }
    },
    closeClienteModal() {
      this.showClienteModal = false
      this.editingCliente = null
      this.formCliente = { name: '', address: '', phone: '', email: '', latitude: 0, longitude: 0, client_type: '' }
    },
    
    // RUTAS
    editRuta(r) {
      this.editingRuta = r.id
      this.formRuta = { ...r }
      this.showRutaModal = true
    },
    async saveRuta() {
      try {
        const url = this.editingRuta 
          ? `${import.meta.env.VITE_API_URL}/routes/${this.editingRuta}`
          : `${import.meta.env.VITE_API_URL}/routes/`
        const method = this.editingRuta ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            seller_id: this.formRuta.seller_id,
            client_id: this.formRuta.client_id,
            planned_date: this.formRuta.planned_date,
            status: this.formRuta.status
          })
        })
        
        if (!response.ok) {
          const error = await response.json()
          alert(`Error: ${error.detail || 'Error al guardar ruta'}`)
          return
        }
        
        this.fetchRutas()
        this.closeRutaModal()
      } catch (e) {
        console.error('Error saving ruta:', e)
        alert(`Error: ${e.message}`)
      }
    },
    async deleteRuta(id) {
      if (!confirm('¿Eliminar?')) return
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/routes/${id}`, { method: 'DELETE' })
        this.fetchRutas()
      } catch (e) {
        console.error('Error deleting ruta:', e)
      }
    },
    closeRutaModal() {
      this.showRutaModal = false
      this.editingRuta = null
      this.formRuta = { seller_id: '', client_id: '', planned_date: '', status: 'pending' }
    },
    
    // HELPERS
    getTipoCliente(type) {
      return this.tiposCliente[type] || type
    },
    getNombreVendedor(id) {
      const v = this.vendedores.find(x => x.id === id)
      return v ? v.name : 'Desconocido'
    },
    getNombreCliente(id) {
      const c = this.clientes.find(x => x.id === id)
      return c ? c.name : 'Desconocido'
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
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
