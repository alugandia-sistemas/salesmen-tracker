<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
    <!-- Header -->
    <nav class="bg-gradient-to-r from-red-600 to-red-700 text-white shadow-lg sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <router-link to="/admin" class="flex items-center gap-3 hover:opacity-80">
            <div class="w-12 h-12 bg-white rounded-lg flex items-center justify-center">
              <span class="text-red-600 font-bold text-xl">AT</span>
            </div>
            <h1 class="text-2xl font-bold">Alugandia Tracker</h1>
          </router-link>
        </div>
        <div class="flex items-center gap-6">
          <span class="text-red-100">Gestión de Vendedores</span>
          <button @click="logout" class="bg-white text-red-600 px-4 py-2 rounded-lg font-bold hover:bg-red-50 transition">
            Logout
          </button>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- Title + Create Button -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h2 class="text-4xl font-bold text-white mb-2">Vendedores</h2>
          <p class="text-gray-400">Manage your sales team</p>
        </div>
        <button @click="showCreateModal = true" class="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:shadow-lg transition flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Nuevo Vendedor
        </button>
      </div>

      <!-- Sellers Grid -->
      <div v-if="sellers.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="seller in sellers" :key="seller.id" class="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition overflow-hidden">
          <!-- Card Header -->
          <div class="bg-gradient-to-r from-blue-500 to-blue-600 h-32 relative">
            <div class="absolute bottom-0 left-6 transform translate-y-1/2">
              <div class="w-20 h-20 bg-gradient-to-br from-yellow-300 to-yellow-400 rounded-full border-4 border-white flex items-center justify-center">
                <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
            </div>
          </div>

          <!-- Card Body -->
          <div class="pt-12 px-6 pb-6">
            <h3 class="text-xl font-bold text-gray-900">{{ seller.name }}</h3>
            <p class="text-gray-500 text-sm mt-1">{{ seller.email }}</p>
            
            <div class="mt-4 space-y-2">
              <div class="flex items-center gap-2 text-gray-600">
                <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 00.948-.684l1.498-4.493a1 1 0 011.502-.684l1.498 4.493a1 1 0 00.948.684H19a2 2 0 012 2v1M3 5a2 2 0 002 2h3.28a1 1 0 00.948-.684l1.498-4.493a1 1 0 011.502-.684l1.498 4.493a1 1 0 00.948.684H19a2 2 0 012 2v1"/>
                </svg>
                <span>{{ seller.phone }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-semibold" v-if="seller.is_active">
                  ✓ Activo
                </span>
                <span class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-semibold" v-else>
                  Inactivo
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="mt-6 flex gap-2">
              <button @click="editSeller(seller)" class="flex-1 bg-blue-100 text-blue-600 py-2 rounded-lg font-semibold hover:bg-blue-200 transition">
                Editar
              </button>
              <button @click="deleteSeller(seller.id)" class="flex-1 bg-red-100 text-red-600 py-2 rounded-lg font-semibold hover:bg-red-200 transition">
                Eliminar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="bg-white rounded-2xl shadow-lg p-12 text-center">
        <svg class="w-20 h-20 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.856-1.487M15 10a3 3 0 11-6 0 3 3 0 016 0zM6 20h12v-2a9 9 0 00-18 0v2z"/>
        </svg>
        <h3 class="text-2xl font-bold text-gray-900 mb-2">Sin vendedores</h3>
        <p class="text-gray-500 mb-6">Comienza creando tu primer vendedor</p>
        <button @click="showCreateModal = true" class="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-700 transition">
          Crear Vendedor
        </button>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        <h3 class="text-2xl font-bold text-gray-900 mb-6">
          {{ editingId ? 'Editar Vendedor' : 'Nuevo Vendedor' }}
        </h3>

        <form @submit.prevent="saveSeller" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Nombre</label>
            <input 
              v-model="form.name" 
              type="text" 
              class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="Ej: Ernesto Arocas"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Email</label>
            <input 
              v-model="form.email" 
              type="email" 
              class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="ernesto@alugandia.com"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Teléfono</label>
            <input 
              v-model="form.phone" 
              type="tel" 
              class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="+34 6XX XXX XXX"
              required
            />
          </div>

          <div class="flex items-center gap-2">
            <input 
              v-model="form.is_active" 
              type="checkbox" 
              id="active"
              class="w-5 h-5 text-blue-600"
            />
            <label for="active" class="text-gray-700 font-semibold">Vendedor Activo</label>
          </div>

          <div class="flex gap-4 mt-8">
            <button 
              type="button"
              @click="showCreateModal = false"
              class="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg font-semibold hover:bg-gray-300 transition"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              class="flex-1 bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 transition"
            >
              {{ editingId ? 'Actualizar' : 'Crear' }}
            </button>
          </div>
        </form>
      </div>
    </div>
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
          this.resetForm()
          this.showCreateModal = false
        }
      } catch (e) {
        console.error('Error saving seller:', e)
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
      if (!confirm('¿Estás seguro de que quieres eliminar este vendedor?')) return
      
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/sellers/${id}`, {
          method: 'DELETE'
        })
        this.fetchSellers()
      } catch (e) {
        console.error('Error deleting seller:', e)
      }
    },
    resetForm() {
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
  transition: all 0.3s ease;
}
</style>
