<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="px-4 py-4">
        <div class="flex justify-between items-center">
          <router-link to="/admin" class="text-2xl font-bold text-gray-900 hover:opacity-70">
            ← Alugandia
          </router-link>
          <button @click="logout" class="bg-gray-900 text-white px-3 py-2 rounded-lg text-sm font-semibold">
            Salir
          </button>
        </div>
        <p class="text-gray-600 text-sm mt-2">Gestión de Vendedores</p>
      </div>
    </nav>

    <!-- Content -->
    <div class="px-4 py-6 pb-20">
      <!-- Title + Create Button -->
      <div class="mb-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-4">Vendedores</h2>
        <button 
          @click="showCreateModal = true" 
          class="w-full bg-gray-900 text-white py-4 rounded-xl font-semibold text-lg hover:bg-gray-800 transition"
        >
          + Nuevo Vendedor
        </button>
      </div>

      <!-- Sellers List - Mobile Optimized -->
      <div v-if="sellers.length > 0" class="space-y-3 mb-8">
        <div v-for="seller in sellers" :key="seller.id" class="bg-white border-2 border-gray-200 rounded-xl p-5 hover:border-gray-400 transition">
          <!-- Avatar + Name -->
          <div class="flex items-start gap-4 mb-4">
            <div class="w-14 h-14 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
              <span class="text-white font-bold text-lg">
                {{ seller.name.charAt(0).toUpperCase() }}
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-bold text-gray-900">{{ seller.name }}</h3>
              <p class="text-gray-600 text-sm truncate">{{ seller.email }}</p>
            </div>
          </div>

          <!-- Info -->
          <div class="space-y-2 mb-4 pl-0">
            <div class="flex items-center gap-2 text-gray-700 text-sm">
              <svg class="w-5 h-5 text-gray-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 00.948-.684l1.498-4.493a1 1 0 011.502-.684l1.498 4.493a1 1 0 00.948.684H19a2 2 0 012 2v1M3 5a2 2 0 002 2h3.28a1 1 0 00.948-.684l1.498-4.493a1 1 0 011.502-.684l1.498 4.493a1 1 0 00.948.684H19a2 2 0 012 2v1"/>
              </svg>
              <span>{{ seller.phone }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span 
                class="px-3 py-1 rounded-full text-sm font-semibold"
                :class="seller.is_active ? 'bg-gray-200 text-gray-900' : 'bg-gray-100 text-gray-600'"
              >
                {{ seller.is_active ? '✓ Activo' : '• Inactivo' }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <button 
              @click="editSeller(seller)" 
              class="flex-1 bg-gray-100 text-black-900 py-3 rounded-lg font-semibold text-sm hover:bg-gray-200 transition"
            >
              Editar
            </button>
            <button 
              @click="deleteSeller(seller.id)" 
              class="flex-1 bg-gray-900 text-white py-3 rounded-lg font-semibold text-sm hover:bg-gray-800 transition"
            >
              Eliminar
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
        <div class="text-4xl mb-3">📋</div>
        <h3 class="text-xl font-bold text-gray-900 mb-2">Sin vendedores</h3>
        <p class="text-gray-600 text-sm mb-6">Comienza creando tu primer vendedor</p>
        <button 
          @click="showCreateModal = true" 
          class="w-full bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition"
        >
          Crear Vendedor
        </button>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/40 flex items-end z-50 pb-safe">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-2xl font-bold text-gray-900 mb-6">
          {{ editingId ? 'Editar Vendedor' : 'Nuevo Vendedor' }}
        </h3>

        <form @submit.prevent="saveSeller" class="space-y-5">
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Nombre</label>
            <input 
              v-model="form.name" 
              type="text" 
              class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
              placeholder="Ej: Ernesto Arocas"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Email</label>
            <input 
              v-model="form.email" 
              type="email" 
              class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
              placeholder="ernesto@alugandia.com"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Teléfono</label>
            <input 
              v-model="form.phone" 
              type="tel" 
              class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
              placeholder="+34 6XX XXX XXX"
              required
            />
          </div>

          <div class="flex items-center gap-3 py-2">
            <input 
              v-model="form.is_active" 
              type="checkbox" 
              id="active"
              class="w-5 h-5 accent-gray-900"
            />
            <label for="active" class="text-gray-900 font-semibold">Vendedor Activo</label>
          </div>

          <div class="flex gap-3 mt-8 pt-6 border-t border-gray-200">
            <button 
              type="button"
              @click="closeModal()"
              class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold text-lg hover:bg-gray-200 transition"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition"
            >
              {{ editingId ? 'Actualizar' : 'Crear' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div v-if="showCreateModal" @click="closeModal()" class="fixed inset-0 bg-black/40 z-40"></div>
  </div>
</template>

<script>
export default {
  name: 'AdminGestion',
  data() {
    return {
      sellers: [],
      showCreateModal: false,
      editingId: null,
      form: {
        name: '',
        email: '',
        phone: '',
        is_active: true
      }
    }
  },
  mounted() {
    this.fetchSellers()
  },
  methods: {
    async fetchSellers() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/sellers/`)
        this.sellers = await response.json()
      } catch (e) {
        console.error('Error fetching sellers:', e)
      }
    },
    async saveSeller() {
      try {
        const url = this.editingId 
          ? `${import.meta.env.VITE_API_URL}/sellers/${this.editingId}`
          : `${import.meta.env.VITE_API_URL}/sellers/`
        
        const method = this.editingId ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        })
        
        if (response.ok) {
          this.fetchSellers()
          this.closeModal()
        }
      } catch (e) {
        console.error('Error saving seller:', e)
        alert('Error al guardar vendedor')
      }
    },
    editSeller(seller) {
      this.editingId = seller.id
      this.form = {
        name: seller.name,
        email: seller.email,
        phone: seller.phone,
        is_active: seller.is_active
      }
      this.showCreateModal = true
    },
    async deleteSeller(id) {
      if (!confirm('¿Estás seguro?')) return
      
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/sellers/${id}`, {
          method: 'DELETE'
        })
        this.fetchSellers()
      } catch (e) {
        console.error('Error deleting seller:', e)
        alert('Error al eliminar')
      }
    },
    closeModal() {
      this.showCreateModal = false
      this.editingId = null
      this.form = {
        name: '',
        email: '',
        phone: '',
        is_active: true
      }
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
  -moz-osx-font-smoothing: grayscale;
}

/* Safe area support for notch devices */
@supports (padding: max(0px)) {
  .pb-safe {
    padding-bottom: max(1.5rem, env(safe-area-inset-bottom));
  }
}
</style>
