<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="px-4 py-4">
        <div class="flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Alugandia</h1>
          <button @click="logout" class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-800 transition">
            Salir
          </button>
        </div>
        <p class="text-gray-600 text-sm mt-2">Panel Admin</p>
      </div>
    </nav>

    <!-- Tabs Navigation -->
    <div class="bg-white border-b border-gray-200 sticky top-16 z-40">
      <div class="px-4 py-0 flex gap-0 overflow-x-auto">
        <button 
          @click="$router.push('/admin/gestion')"
          class="px-4 py-4 font-semibold text-sm border-b-2 border-transparent text-gray-600 hover:text-gray-900 transition whitespace-nowrap"
        >
          👥 Vendedores
        </button>
        <button 
          @click="$router.push('/admin/gestion')"
          class="px-4 py-4 font-semibold text-sm border-b-2 border-transparent text-gray-600 hover:text-gray-900 transition whitespace-nowrap"
        >
          🏢 Clientes
        </button>
        <button 
          @click="$router.push('/admin/gestion')"
          class="px-4 py-4 font-semibold text-sm border-b-2 border-transparent text-gray-600 hover:text-gray-900 transition whitespace-nowrap"
        >
          🗺️ Rutas
        </button>
        <button 
          class="px-4 py-4 font-semibold text-sm border-b-2 border-gray-900 text-gray-900 transition whitespace-nowrap"
        >
          📧 Invitaciones
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="px-4 py-6 pb-20">
      <h2 class="text-3xl font-bold text-gray-900 mb-8">Invitaciones de Vendedores</h2>

      <!-- Generar Invitación -->
      <div class="bg-white border-2 border-gray-200 rounded-xl p-6 mb-8">
        <h3 class="text-xl font-bold text-gray-900 mb-6">+ Generar Nueva Invitación</h3>

        <form @submit.prevent="generarInvitacion" class="space-y-5">
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Nombre del Vendedor</label>
            <input 
              v-model="nuevoVendedor.nombre" 
              type="text" 
              placeholder="Ej: Ernesto Arocas"
              class="w-full px-4 py-3 text-lg text-gray-900 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 placeholder-gray-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Email</label>
            <input 
              v-model="nuevoVendedor.email" 
              type="email" 
              placeholder="Ej: ernesto@alugandia.com"
              class="w-full px-4 py-3 text-lg text-gray-900 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 placeholder-gray-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Teléfono</label>
            <input 
              v-model="nuevoVendedor.telefono" 
              type="tel" 
              placeholder="Ej: +34 600 123 456"
              class="w-full px-4 py-3 text-lg text-gray-900 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 placeholder-gray-500"
              required
            />
          </div>

          <button 
            type="submit"
            :disabled="cargandoInvitacion"
            class="w-full bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ cargandoInvitacion ? '⏳ Generando...' : '📧 Generar Invitación' }}
          </button>
        </form>

        <!-- Mensajes -->
        <div v-if="mensaje" class="mt-4 p-4 bg-green-50 border-2 border-green-200 rounded-lg">
          <p class="text-green-900 font-semibold text-sm">✅ {{ mensaje }}</p>
        </div>
        <div v-if="error" class="mt-4 p-4 bg-red-50 border-2 border-red-200 rounded-lg">
          <p class="text-red-900 font-semibold text-sm">❌ {{ error }}</p>
        </div>
      </div>

      <!-- Invitaciones Generadas -->
      <h3 class="text-xl font-bold text-gray-900 mb-4">Invitaciones Generadas</h3>

      <div v-if="invitaciones.length > 0" class="space-y-3">
        <div v-for="inv in invitaciones" :key="inv.id" class="bg-gray-50 border-2 border-gray-200 rounded-xl p-5">
          <!-- Información de vendedor -->
          <div class="flex items-start gap-3 mb-4">
            <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
              <span class="text-white font-bold text-sm">{{ inv.seller_name.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="flex-1">
              <h4 class="text-lg font-bold text-gray-900">{{ inv.seller_name }}</h4>
              <p class="text-gray-600 text-sm">📧 {{ inv.email }}</p>
              <p class="text-gray-600 text-sm">📱 {{ inv.seller_phone }}</p>
            </div>
          </div>

          <!-- Status -->
          <div class="flex gap-2 mb-4">
            <span 
              class="px-3 py-1 rounded-full text-xs font-semibold"
              :class="inv.is_used ? 'bg-green-200 text-green-900' : 'bg-orange-200 text-orange-900'"
            >
              {{ inv.is_used ? '✅ Usado' : '⏳ Pendiente' }}
            </span>
            <span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-200 text-gray-900">
              📅 Vence: {{ formatDate(inv.expires_at) }}
            </span>
          </div>

          <!-- Link de invitación -->
          <div v-if="!inv.is_used" class="mb-4">
            <label class="block text-sm font-semibold text-gray-900 mb-2">Link de Invitación</label>
            <div class="flex gap-2">
              <input 
                :value="getInviteLink(inv.token)" 
                type="text" 
                readonly
                class="flex-1 px-4 py-3 text-sm text-gray-900 bg-gray-100 border-2 border-gray-300 rounded-lg font-mono focus:outline-none"
              />
              <button 
                @click="copiarLink(inv.token)"
                class="bg-gray-900 text-white px-4 py-3 rounded-lg font-semibold text-sm hover:bg-gray-800 transition whitespace-nowrap"
              >
                Copiar
              </button>
            </div>
            <p class="text-gray-500 text-xs mt-2">💡 Comparte este link con el vendedor por email o WhatsApp</p>
          </div>

          <!-- Info creación -->
          <p class="text-gray-500 text-xs">
            Creado: {{ formatDateTime(inv.created_at) }}
          </p>
        </div>
      </div>

      <!-- Sin invitaciones -->
      <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
        <p class="text-gray-600 text-sm">Sin invitaciones generadas aún</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminInvitaciones',
  data() {
    return {
      nuevoVendedor: {
        nombre: '',
        email: '',
        telefono: ''
      },
      invitaciones: [],
      cargandoInvitacion: false,
      mensaje: null,
      error: null
    }
  },
  mounted() {
    this.cargarInvitaciones()
  },
  methods: {
    async generarInvitacion() {
      this.error = null
      this.mensaje = null
      this.cargandoInvitacion = true

      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/admin/invitations/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            seller_name: this.nuevoVendedor.nombre,
            email: this.nuevoVendedor.email,
            seller_phone: this.nuevoVendedor.telefono
          })
        })

        if (!response.ok) {
          const errorData = await response.json()
          this.error = errorData.detail || 'Error al generar invitación'
          return
        }

        const data = await response.json()
        this.mensaje = '✅ Invitación generada. Link copiado al portapapeles.'
        
        // Copiar link automáticamente
        const link = `${window.location.origin}/registro?token=${data.token}`
        navigator.clipboard.writeText(link).catch(() => {
          console.log('Link:', link)
        })

        // Limpiar formulario
        this.nuevoVendedor = { nombre: '', email: '', telefono: '' }

        // Recargar invitaciones
        await this.cargarInvitaciones()

        // Limpiar mensaje después de 3 segundos
        setTimeout(() => {
          this.mensaje = null
        }, 3000)
      } catch (e) {
        this.error = 'Error: ' + e.message
      } finally {
        this.cargandoInvitacion = false
      }
    },

    async cargarInvitaciones() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/admin/invitations/`)
        
        if (!response.ok) {
          console.error('Error al cargar invitaciones')
          return
        }

        this.invitaciones = await response.json()
        
        // Ordenar: pendientes primero, luego usadas
        this.invitaciones.sort((a, b) => {
          if (a.is_used === b.is_used) {
            return new Date(b.created_at) - new Date(a.created_at)
          }
          return a.is_used ? 1 : -1
        })
      } catch (e) {
        console.error('Error fetching invitations:', e)
      }
    },

    getInviteLink(token) {
      return `${window.location.origin}/registro?token=${token}`
    },

    async copiarLink(token) {
      const link = this.getInviteLink(token)
      try {
        await navigator.clipboard.writeText(link)
        alert('✅ Link copiado al portapapeles')
      } catch (e) {
        console.error('Error copying:', e)
        alert('Link: ' + link)
      }
    },

    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('es-ES', { 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    formatDateTime(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('es-ES', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('seller')
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
