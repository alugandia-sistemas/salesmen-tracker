<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="px-4 py-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-3">
            <button @click="$router.back()" class="text-gray-600 hover:text-gray-900">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
              </svg>
            </button>
            <h1 class="text-xl font-bold text-gray-900">Directorio</h1>
          </div>
          <span class="text-sm text-gray-500">{{ clientesFiltrados.length }} clientes</span>
        </div>
      </div>
    </nav>

    <!-- Buscador -->
    <div class="px-4 py-3 bg-gray-50 border-b border-gray-200 sticky top-16 z-40">
      <div class="relative">
        <input 
          v-model="busqueda"
          type="text"
          placeholder="Buscar cliente..."
          class="w-full pl-10 pr-4 py-3 text-base border-2 border-gray-200 rounded-xl focus:outline-none focus:border-gray-900 bg-white"
        />
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <button 
          v-if="busqueda"
          @click="busqueda = ''"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Tabs: Alfabético / Categorías -->
    <div class="px-4 py-2 bg-white border-b border-gray-200 sticky top-32 z-30">
      <div class="flex gap-2">
        <button 
          @click="vistaActual = 'alfabetico'"
          :class="[
            'flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition',
            vistaActual === 'alfabetico' 
              ? 'bg-gray-900 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          A–Z
        </button>
        <button 
          @click="vistaActual = 'categorias'"
          :class="[
            'flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition',
            vistaActual === 'categorias' 
              ? 'bg-gray-900 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          Categorías
        </button>
      </div>
    </div>

    <!-- VISTA ALFABÉTICA -->
    <div v-if="vistaActual === 'alfabetico'" class="pb-20">
      <!-- Navegación rápida por grupos -->
      <div class="px-4 py-3 bg-gray-50 border-b border-gray-200 overflow-x-auto">
        <div class="flex gap-2 min-w-max">
          <button 
            v-for="grupo in gruposAlfabeticos" 
            :key="grupo.id"
            @click="scrollToGroup(grupo.id)"
            :class="[
              'px-3 py-2 rounded-lg text-sm font-bold transition whitespace-nowrap',
              grupoActivo === grupo.id
                ? 'bg-gray-900 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
            ]"
          >
            {{ grupo.label }}
            <span class="ml-1 text-xs opacity-70">({{ contarClientesEnGrupo(grupo.letras) }})</span>
          </button>
        </div>
      </div>

      <!-- Lista de clientes por grupo -->
      <div class="px-4">
        <div 
          v-for="grupo in gruposAlfabeticos" 
          :key="grupo.id"
          :id="'grupo-' + grupo.id"
          class="py-4"
        >
          <!-- Header del grupo -->
          <div 
            v-if="clientesEnGrupo(grupo.letras).length > 0"
            class="sticky top-44 bg-gray-100 -mx-4 px-4 py-2 border-b border-gray-200 z-20"
          >
            <h2 class="text-lg font-bold text-gray-900">
              {{ grupo.label }}
              <span class="text-sm font-normal text-gray-500 ml-2">
                {{ clientesEnGrupo(grupo.letras).length }} clientes
              </span>
            </h2>
          </div>

          <!-- Clientes del grupo -->
          <div class="space-y-2 mt-2">
            <div 
              v-for="cliente in clientesEnGrupo(grupo.letras)" 
              :key="cliente.id"
              @click="seleccionarCliente(cliente)"
              class="bg-white border border-gray-200 rounded-xl p-4 hover:border-gray-400 hover:shadow-sm transition cursor-pointer"
            >
              <div class="flex items-start gap-3">
                <!-- Avatar -->
                <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                  <span class="text-white font-bold text-lg">{{ cliente.name.charAt(0).toUpperCase() }}</span>
                </div>
                
                <!-- Info -->
                <div class="flex-1 min-w-0">
                  <h3 class="font-bold text-gray-900 truncate">{{ cliente.name }}</h3>
                  <p class="text-gray-500 text-sm truncate">{{ cliente.address }}</p>
                  <div class="flex items-center gap-2 mt-1">
                    <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-700">
                      {{ getEmojiTipo(cliente.client_type) }} {{ getLabelTipo(cliente.client_type) }}
                    </span>
                  </div>
                </div>

                <!-- Acciones rápidas -->
                <div class="flex flex-col gap-1">
                  <a 
                    :href="'tel:' + cliente.phone" 
                    @click.stop
                    class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200 transition"
                  >
                    <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </div>

          <!-- Grupo vacío -->
          <div 
            v-if="clientesEnGrupo(grupo.letras).length === 0 && !busqueda"
            class="py-8 text-center text-gray-400 text-sm"
          >
            Sin clientes en {{ grupo.label }}
          </div>
        </div>
      </div>
    </div>

    <!-- VISTA POR CATEGORÍAS -->
    <div v-if="vistaActual === 'categorias'" class="pb-20">
      <!-- Selector de categoría -->
      <div class="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div class="grid grid-cols-4 gap-2">
          <button 
            v-for="cat in categoriasVisibles" 
            :key="cat.id"
            @click="categoriaActiva = categoriaActiva === cat.id ? null : cat.id"
            :class="[
              'py-3 px-2 rounded-xl text-center transition',
              categoriaActiva === cat.id
                ? 'bg-gray-900 text-white'
                : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-100'
            ]"
          >
            <div class="text-xl mb-1">{{ cat.emoji }}</div>
            <div class="text-xs font-semibold truncate">{{ cat.short }}</div>
            <div class="text-xs opacity-70">{{ contarPorCategoria(cat.id) }}</div>
          </button>
        </div>
      </div>

      <!-- Lista de clientes por categoría -->
      <div class="px-4 py-4">
        <div v-if="clientesPorCategoria.length > 0" class="space-y-2">
          <div 
            v-for="cliente in clientesPorCategoria" 
            :key="cliente.id"
            @click="seleccionarCliente(cliente)"
            class="bg-white border border-gray-200 rounded-xl p-4 hover:border-gray-400 hover:shadow-sm transition cursor-pointer"
          >
            <div class="flex items-start gap-3">
              <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold text-lg">{{ cliente.name.charAt(0).toUpperCase() }}</span>
              </div>
              
              <div class="flex-1 min-w-0">
                <h3 class="font-bold text-gray-900 truncate">{{ cliente.name }}</h3>
                <p class="text-gray-500 text-sm truncate">{{ cliente.address }}</p>
                <p class="text-gray-600 text-sm mt-1">📞 {{ cliente.phone }}</p>
              </div>

              <a 
                :href="'tel:' + cliente.phone" 
                @click.stop
                class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200 transition"
              >
                <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>

        <div v-else class="py-12 text-center">
          <div class="text-4xl mb-3">📂</div>
          <p class="text-gray-500">
            {{ categoriaActiva ? 'Sin clientes en esta categoría' : 'Selecciona una categoría' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Sin resultados de búsqueda -->
    <div v-if="busqueda && clientesFiltrados.length === 0" class="px-4 py-12 text-center">
      <div class="text-4xl mb-3">🔍</div>
      <p class="text-gray-500">No se encontraron clientes para "{{ busqueda }}"</p>
    </div>

    <!-- MODAL DETALLE CLIENTE -->
    <div v-if="clienteSeleccionado" class="fixed inset-0 bg-black/40 flex items-end z-50" @click.self="clienteSeleccionado = null">
      <div class="w-full bg-white rounded-t-2xl shadow-2xl max-h-[85vh] overflow-y-auto">
        <!-- Header modal -->
        <div class="sticky top-0 bg-white border-b border-gray-200 px-4 py-4 flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900">Detalle Cliente</h2>
          <button @click="clienteSeleccionado = null" class="text-gray-500 hover:text-gray-900 text-2xl font-bold">×</button>
        </div>

        <div class="p-4 space-y-4">
          <!-- Info principal -->
          <div class="flex items-start gap-4">
            <div class="w-16 h-16 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
              <span class="text-white font-bold text-2xl">{{ clienteSeleccionado.name.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="flex-1">
              <h3 class="text-xl font-bold text-gray-900">{{ clienteSeleccionado.name }}</h3>
              <span class="inline-block mt-1 text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-700">
                {{ getEmojiTipo(clienteSeleccionado.client_type) }} {{ getLabelTipo(clienteSeleccionado.client_type) }}
              </span>
            </div>
          </div>

          <!-- Datos de contacto -->
          <div class="bg-gray-50 rounded-xl p-4 space-y-3">
            <div>
              <p class="text-xs text-gray-500 font-semibold uppercase">Dirección</p>
              <p class="text-gray-900">{{ clienteSeleccionado.address }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 font-semibold uppercase">Teléfono</p>
              <a :href="'tel:' + clienteSeleccionado.phone" class="text-gray-900 font-mono hover:underline">
                {{ clienteSeleccionado.phone }}
              </a>
            </div>
            <div v-if="clienteSeleccionado.email">
              <p class="text-xs text-gray-500 font-semibold uppercase">Email</p>
              <a :href="'mailto:' + clienteSeleccionado.email" class="text-gray-900 hover:underline">
                {{ clienteSeleccionado.email }}
              </a>
            </div>
          </div>

          <!-- Coordenadas -->
          <div v-if="clienteSeleccionado.latitude && clienteSeleccionado.longitude" class="bg-blue-50 rounded-xl p-4">
            <p class="text-xs text-blue-700 font-semibold uppercase mb-2">📍 Ubicación GPS</p>
            <p class="text-blue-900 font-mono text-sm">
              {{ clienteSeleccionado.latitude.toFixed(5) }}, {{ clienteSeleccionado.longitude.toFixed(5) }}
            </p>
          </div>

          <!-- Acciones -->
          <div class="grid grid-cols-2 gap-3">
            <a 
              :href="'tel:' + clienteSeleccionado.phone"
              class="bg-gray-900 text-white py-4 rounded-xl font-semibold text-center hover:bg-gray-800 transition flex items-center justify-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
              Llamar
            </a>
            <a 
              v-if="clienteSeleccionado.latitude && clienteSeleccionado.longitude"
              :href="'https://www.google.com/maps/search/?api=1&query=' + clienteSeleccionado.latitude + ',' + clienteSeleccionado.longitude"
              target="_blank"
              class="bg-gray-100 text-gray-900 py-4 rounded-xl font-semibold text-center hover:bg-gray-200 transition flex items-center justify-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              Maps
            </a>
            <button
              v-else
              disabled
              class="bg-gray-100 text-gray-400 py-4 rounded-xl font-semibold text-center cursor-not-allowed"
            >
              Sin GPS
            </button>
          </div>

          <!-- Crear ruta -->
          <button 
            @click="crearRutaRapida(clienteSeleccionado)"
            class="w-full bg-gray-100 text-gray-900 border-2 border-gray-300 py-4 rounded-xl font-semibold hover:bg-gray-200 transition"
          >
            📅 Crear Ruta para Hoy
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DirectorioClientes',
  data() {
    return {
      clientes: [],
      busqueda: '',
      vistaActual: 'alfabetico', // 'alfabetico' | 'categorias'
      categoriaActiva: null,
      grupoActivo: 'ac',
      clienteSeleccionado: null,
      
      // Grupos alfabéticos: A–C, D–F, G–I, J–L, M–O, P–R, S–T, U–Z
      gruposAlfabeticos: [
        { id: 'ac', label: 'A–C', letras: ['A', 'B', 'C'] },
        { id: 'df', label: 'D–F', letras: ['D', 'E', 'F'] },
        { id: 'gi', label: 'G–I', letras: ['G', 'H', 'I'] },
        { id: 'jl', label: 'J–L', letras: ['J', 'K', 'L'] },
        { id: 'mo', label: 'M–O', letras: ['M', 'N', 'O'] },
        { id: 'pr', label: 'P–R', letras: ['P', 'Q', 'R'] },
        { id: 'st', label: 'S–T', letras: ['S', 'T'] },
        { id: 'uz', label: 'U–Z', letras: ['U', 'V', 'W', 'X', 'Y', 'Z'] }
      ],
      
      // Categorías de clientes
      categorias: [
        { id: 'carpintero_metalico', label: 'Carpinteros Metálicos', short: 'Carpint.', emoji: '🔧' },
        { id: 'cristalero', label: 'Cristaleros', short: 'Cristal.', emoji: '🪟' },
        { id: 'taller', label: 'Talleres', short: 'Talleres', emoji: '🏭' },
        { id: 'instalador', label: 'Instaladores', short: 'Install.', emoji: '🔨' },
        { id: 'cerrajero', label: 'Cerrajeros', short: 'Cerraj.', emoji: '🔑' },
        { id: 'constructor', label: 'Constructores', short: 'Constr.', emoji: '🏗️' },
        { id: 'otros', label: 'Otros', short: 'Otros', emoji: '📦' },
        // Tipos legacy (para compatibilidad)
        { id: 'carpenter', label: 'Carpintero (legacy)', short: 'Carp.', emoji: '🔧', legacy: true },
        { id: 'installer', label: 'Instalador (legacy)', short: 'Inst.', emoji: '🔨', legacy: true },
        { id: 'industrial', label: 'Industrial (legacy)', short: 'Indust.', emoji: '🏭', legacy: true }
      ]
    }
  },
  computed: {
    clientesFiltrados() {
      if (!this.busqueda) return this.clientes
      
      const termino = this.busqueda.toLowerCase().trim()
      return this.clientes.filter(c => 
        c.name.toLowerCase().includes(termino) ||
        c.address.toLowerCase().includes(termino) ||
        c.phone.includes(termino)
      )
    },
    
    clientesPorCategoria() {
      if (!this.categoriaActiva) return []
      
      return this.clientesFiltrados
        .filter(c => c.client_type === this.categoriaActiva)
        .sort((a, b) => a.name.localeCompare(b.name, 'es'))
    },
    
    // Solo mostrar categorías con clientes o las principales (no legacy vacías)
    categoriasVisibles() {
      return this.categorias.filter(cat => {
        const count = this.contarPorCategoria(cat.id)
        // Mostrar si tiene clientes o no es legacy
        return count > 0 || !cat.legacy
      })
    }
  },
  mounted() {
    this.cargarClientes()
  },
  methods: {
    async cargarClientes() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/clients/`)
        this.clientes = await response.json()
        
        // Ordenar alfabéticamente
        this.clientes.sort((a, b) => a.name.localeCompare(b.name, 'es'))
      } catch (e) {
        console.error('Error cargando clientes:', e)
      }
    },
    
    clientesEnGrupo(letras) {
      return this.clientesFiltrados.filter(c => {
        const inicial = c.name.charAt(0).toUpperCase()
        return letras.includes(inicial)
      })
    },
    
    contarClientesEnGrupo(letras) {
      return this.clientesEnGrupo(letras).length
    },
    
    contarPorCategoria(tipo) {
      return this.clientesFiltrados.filter(c => c.client_type === tipo).length
    },
    
    scrollToGroup(grupoId) {
      this.grupoActivo = grupoId
      const element = document.getElementById('grupo-' + grupoId)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    },
    
    seleccionarCliente(cliente) {
      this.clienteSeleccionado = cliente
    },
    
    getEmojiTipo(tipo) {
      const cat = this.categorias.find(c => c.id === tipo)
      return cat ? cat.emoji : '📦'
    },
    
    getLabelTipo(tipo) {
      const cat = this.categorias.find(c => c.id === tipo)
      return cat ? cat.short : tipo
    },
    
    async crearRutaRapida(cliente) {
      // Obtener seller del localStorage
      const sellerData = localStorage.getItem('seller')
      if (!sellerData) {
        alert('No hay vendedor logueado')
        return
      }
      
      const seller = JSON.parse(sellerData)
      const hoy = new Date().toISOString().split('T')[0]
      
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            seller_id: seller.id,
            client_id: cliente.id,
            planned_date: hoy,
            status: 'pending'
          })
        })
        
        if (response.ok) {
          alert(`✅ Ruta creada para ${cliente.name}`)
          this.clienteSeleccionado = null
        } else {
          const error = await response.json()
          alert(`Error: ${error.detail}`)
        }
      } catch (e) {
        alert('Error de conexión')
      }
    }
  }
}
</script>

<style scoped>
* {
  -webkit-font-smoothing: antialiased;
}

/* Scroll suave */
html {
  scroll-behavior: smooth;
}

/* Ocultar scrollbar horizontal en navegación */
.overflow-x-auto::-webkit-scrollbar {
  height: 0;
}
</style>
