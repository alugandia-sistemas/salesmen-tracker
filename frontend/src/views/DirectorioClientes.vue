<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="px-4 py-4">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Directorio de Clientes</h1>
            <p class="text-gray-600 text-sm mt-1">{{ clientesFiltrados.length }} clientes</p>
          </div>
          <button @click="$router.push('/admin/gestion')" class="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-200 transition">
            ← Volver
          </button>
        </div>
      </div>
    </nav>

    <!-- Filtros -->
    <div class="bg-gray-50 border-b border-gray-200 px-4 py-4 sticky top-16 z-40">
      <!-- Tabs de Organización -->
      <div class="flex gap-2 mb-4 overflow-x-auto pb-2">
        <button 
          @click="vistaActual = 'alfabetico'"
          :class="[
            'px-4 py-2 rounded-lg font-semibold text-sm whitespace-nowrap transition',
            vistaActual === 'alfabetico' 
              ? 'bg-gray-900 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
        >
          🔤 Alfabético
        </button>
        <button 
          @click="vistaActual = 'categoria'"
          :class="[
            'px-4 py-2 rounded-lg font-semibold text-sm whitespace-nowrap transition',
            vistaActual === 'categoria' 
              ? 'bg-gray-900 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
        >
          🏷️ Por Categoría
        </button>
      </div>

      <!-- Filtros Alfabéticos -->
      <div v-if="vistaActual === 'alfabetico'" class="flex gap-2 overflow-x-auto pb-2">
        <button 
          @click="grupoAlfabetico = 'todos'"
          :class="[
            'px-3 py-2 rounded-lg font-semibold text-sm whitespace-nowrap transition',
            grupoAlfabetico === 'todos' 
              ? 'bg-gray-900 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
        >
          Todos
        </button>
        <button 
          @click="grupoAlfabetico = 'A-M'"
          :class="[
            'px-3 py-2 rounded-lg font-semibold text-sm whitespace-nowrap transition',
            grupoAlfabetico === 'A-M' 
              ? 'bg-gray-900 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
        >
          A - M ({{ contarGrupo('A-M') }})
        </button>
        <button 
          @click="grupoAlfabetico = 'N-Z'"
          :class="[
            'px-3 py-2 rounded-lg font-semibold text-sm whitespace-nowrap transition',
            grupoAlfabetico === 'N-Z' 
              ? 'bg-gray-900 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
        >
          N - Z ({{ contarGrupo('N-Z') }})
        </button>
      </div>

      <!-- Filtros por Categoría -->
      <div v-if="vistaActual === 'categoria'" class="flex gap-2 overflow-x-auto pb-2">
        <button 
          v-for="cat in categorias" 
          :key="cat.value"
          @click="categoriaSeleccionada = cat.value"
          :class="[
            'px-3 py-2 rounded-lg font-semibold text-sm whitespace-nowrap transition',
            categoriaSeleccionada === cat.value 
              ? 'bg-gray-900 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
        >
          {{ cat.emoji }} {{ cat.label }} ({{ contarCategoria(cat.value) }})
        </button>
      </div>

      <!-- Buscador -->
      <div class="mt-3">
        <input 
          v-model="busqueda" 
          type="text" 
          placeholder="🔍 Buscar cliente..."
          class="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
        />
      </div>
    </div>

    <!-- Lista de Clientes -->
    <div class="px-4 py-4 pb-20">
      <!-- Vista Alfabética -->
      <div v-if="vistaActual === 'alfabetico'">
        <div v-for="letra in letrasConClientes" :key="letra" class="mb-6">
          <!-- Header de Letra -->
          <div class="bg-gray-100 px-4 py-2 rounded-lg mb-3 sticky top-36">
            <h3 class="text-xl font-bold text-gray-900">{{ letra }}</h3>
          </div>
          
          <!-- Clientes de esa letra -->
          <div class="space-y-3">
            <div 
              v-for="cliente in clientesPorLetra(letra)" 
              :key="cliente.id" 
              class="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-gray-400 transition cursor-pointer"
              @click="seleccionarCliente(cliente)"
            >
              <div class="flex items-start gap-3">
                <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                  <span class="text-white font-bold">{{ cliente.name.charAt(0).toUpperCase() }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="text-base font-bold text-gray-900 truncate">{{ cliente.name }}</h4>
                  <p class="text-gray-600 text-sm truncate">📍 {{ cliente.address }}</p>
                  <div class="flex gap-2 mt-2">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-700">
                      {{ getCategoriaLabel(cliente.client_type) }}
                    </span>
                    <span v-if="cliente.phone" class="text-gray-500 text-xs">
                      📞 {{ cliente.phone }}
                    </span>
                  </div>
                </div>
                <div class="text-gray-400">→</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Vista por Categoría -->
      <div v-if="vistaActual === 'categoria'">
        <div v-if="clientesFiltrados.length > 0" class="space-y-3">
          <div 
            v-for="cliente in clientesFiltrados" 
            :key="cliente.id" 
            class="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-gray-400 transition cursor-pointer"
            @click="seleccionarCliente(cliente)"
          >
            <div class="flex items-start gap-3">
              <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold">{{ cliente.name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="text-base font-bold text-gray-900 truncate">{{ cliente.name }}</h4>
                <p class="text-gray-600 text-sm truncate">📍 {{ cliente.address }}</p>
                <p v-if="cliente.phone" class="text-gray-500 text-sm">📞 {{ cliente.phone }}</p>
              </div>
              <div class="text-gray-400">→</div>
            </div>
          </div>
        </div>
        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-600">Sin clientes en esta categoría</p>
        </div>
      </div>

      <!-- Sin resultados -->
      <div v-if="clientesFiltrados.length === 0 && busqueda" class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
        <p class="text-gray-600">No se encontraron clientes para "{{ busqueda }}"</p>
      </div>
    </div>

    <!-- Modal Detalle Cliente -->
    <div v-if="clienteSeleccionado" class="fixed inset-0 bg-black/40 flex items-end z-50">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[85vh] overflow-y-auto">
        <div class="flex justify-between items-start mb-6">
          <div>
            <h3 class="text-2xl font-bold text-gray-900">{{ clienteSeleccionado.name }}</h3>
            <span class="px-3 py-1 rounded-full text-sm font-semibold bg-gray-200 text-gray-900 mt-2 inline-block">
              {{ getCategoriaLabel(clienteSeleccionado.client_type) }}
            </span>
          </div>
          <button @click="clienteSeleccionado = null" class="text-gray-500 text-2xl font-bold">✕</button>
        </div>

        <div class="space-y-4">
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-gray-600 text-sm font-semibold mb-1">Dirección</p>
            <p class="text-gray-900">📍 {{ clienteSeleccionado.address }}</p>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-gray-600 text-sm font-semibold mb-1">Teléfono</p>
              <a :href="'tel:' + clienteSeleccionado.phone" class="text-gray-900 font-semibold">
                📞 {{ clienteSeleccionado.phone }}
              </a>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-gray-600 text-sm font-semibold mb-1">Email</p>
              <a :href="'mailto:' + clienteSeleccionado.email" class="text-gray-900 text-sm truncate block">
                {{ clienteSeleccionado.email || 'No disponible' }}
              </a>
            </div>
          </div>

          <div v-if="clienteSeleccionado.latitude && clienteSeleccionado.longitude" class="bg-gray-50 rounded-lg p-4">
            <p class="text-gray-600 text-sm font-semibold mb-2">Ubicación GPS</p>
            <p class="text-gray-700 text-sm font-mono">
              {{ clienteSeleccionado.latitude.toFixed(5) }}, {{ clienteSeleccionado.longitude.toFixed(5) }}
            </p>
            <a 
              :href="`https://maps.google.com/?q=${clienteSeleccionado.latitude},${clienteSeleccionado.longitude}`"
              target="_blank"
              class="inline-block mt-2 bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-semibold"
            >
              🗺️ Abrir en Google Maps
            </a>
          </div>
        </div>

        <div class="flex gap-3 mt-6 pt-4 border-t border-gray-200">
          <button 
            @click="crearRutaParaCliente(clienteSeleccionado)"
            class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold hover:bg-gray-800 transition"
          >
            📍 Crear Ruta
          </button>
          <button 
            @click="llamarCliente(clienteSeleccionado)"
            class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold hover:bg-gray-200 transition"
          >
            📞 Llamar
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
      vistaActual: 'alfabetico', // 'alfabetico' o 'categoria'
      grupoAlfabetico: 'todos', // 'todos', 'A-M', 'N-Z'
      categoriaSeleccionada: 'todos',
      busqueda: '',
      clienteSeleccionado: null,
      
      categorias: [
        { value: 'todos', label: 'Todos', emoji: '📋' },
        { value: 'carpintero_metalico', label: 'Carpinteros', emoji: '🔧' },
        { value: 'cristalero', label: 'Cristaleros', emoji: '🪟' },
        { value: 'taller', label: 'Talleres', emoji: '🏭' },
        { value: 'instalador', label: 'Instaladores', emoji: '🔨' },
        { value: 'cerrajero', label: 'Cerrajeros', emoji: '🔑' },
        { value: 'constructor', label: 'Constructores', emoji: '🏗️' },
        { value: 'otros', label: 'Otros', emoji: '📦' }
      ]
    }
  },
  computed: {
    clientesFiltrados() {
      let resultado = [...this.clientes]
      
      // Filtro por búsqueda
      if (this.busqueda) {
        const termino = this.busqueda.toLowerCase()
        resultado = resultado.filter(c => 
          c.name.toLowerCase().includes(termino) ||
          c.address?.toLowerCase().includes(termino) ||
          c.phone?.includes(termino)
        )
      }
      
      // Filtro alfabético
      if (this.vistaActual === 'alfabetico' && this.grupoAlfabetico !== 'todos') {
        resultado = resultado.filter(c => {
          const inicial = c.name.charAt(0).toUpperCase()
          if (this.grupoAlfabetico === 'A-M') {
            return inicial >= 'A' && inicial <= 'M'
          } else {
            return inicial >= 'N' && inicial <= 'Z'
          }
        })
      }
      
      // Filtro por categoría
      if (this.vistaActual === 'categoria' && this.categoriaSeleccionada !== 'todos') {
        resultado = resultado.filter(c => c.client_type === this.categoriaSeleccionada)
      }
      
      // Ordenar alfabéticamente
      return resultado.sort((a, b) => a.name.localeCompare(b.name, 'es'))
    },
    
    letrasConClientes() {
      const letras = new Set()
      this.clientesFiltrados.forEach(c => {
        letras.add(c.name.charAt(0).toUpperCase())
      })
      return Array.from(letras).sort()
    }
  },
  mounted() {
    this.fetchClientes()
  },
  methods: {
    async fetchClientes() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/clients/`)
        this.clientes = await response.json()
      } catch (e) {
        console.error('Error fetching clientes:', e)
      }
    },
    
    clientesPorLetra(letra) {
      return this.clientesFiltrados.filter(c => 
        c.name.charAt(0).toUpperCase() === letra
      )
    },
    
    contarGrupo(grupo) {
      return this.clientes.filter(c => {
        const inicial = c.name.charAt(0).toUpperCase()
        if (grupo === 'A-M') {
          return inicial >= 'A' && inicial <= 'M'
        } else {
          return inicial >= 'N' && inicial <= 'Z'
        }
      }).length
    },
    
    contarCategoria(categoria) {
      if (categoria === 'todos') return this.clientes.length
      return this.clientes.filter(c => c.client_type === categoria).length
    },
    
    getCategoriaLabel(tipo) {
      const cat = this.categorias.find(c => c.value === tipo)
      return cat ? `${cat.emoji} ${cat.label}` : tipo
    },
    
    seleccionarCliente(cliente) {
      this.clienteSeleccionado = cliente
    },
    
    crearRutaParaCliente(cliente) {
      // Navegar a gestión con cliente preseleccionado
      this.$router.push({
        path: '/admin/gestion',
        query: { 
          tab: 'rutas',
          clienteId: cliente.id 
        }
      })
    },
    
    llamarCliente(cliente) {
      if (cliente.phone) {
        window.location.href = `tel:${cliente.phone}`
      }
    }
  }
}
</script>

<style scoped>
* {
  -webkit-font-smoothing: antialiased;
}
</style>
