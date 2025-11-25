<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <nav class="bg-blue-600 text-white p-4">
      <div class="max-w-7xl mx-auto flex justify-between items-center">
        <h1 class="text-2xl font-bold">Alugandia Salesmen Tracker</h1>
        <div>
          <router-link to="/admin" class="mr-4">Dashboard</router-link>
          <router-link to="/admin/gestion" class="mr-4">Gestión</router-link>
          <button @click="logout" class="bg-red-600 px-4 py-2 rounded">Logout</button>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <div class="max-w-7xl mx-auto p-6">
      <h2 class="text-3xl font-bold mb-6">Panel Administrativo</h2>
      
      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4 mb-6">
        <div class="bg-white p-6 rounded shadow">
          <h3 class="text-gray-600 text-sm">Vendedores</h3>
          <p class="text-3xl font-bold">{{ stats.sellers }}</p>
        </div>
        <div class="bg-white p-6 rounded shadow">
          <h3 class="text-gray-600 text-sm">Clientes</h3>
          <p class="text-3xl font-bold">{{ stats.clients }}</p>
        </div>
        <div class="bg-white p-6 rounded shadow">
          <h3 class="text-gray-600 text-sm">Visitas Hoy</h3>
          <p class="text-3xl font-bold">{{ stats.visitsToday }}</p>
        </div>
        <div class="bg-white p-6 rounded shadow">
          <h3 class="text-gray-600 text-sm">Check-ins Válidos</h3>
          <p class="text-3xl font-bold">{{ stats.validCheckins }}</p>
        </div>
      </div>

      <!-- Manage Buttons -->
      <div class="grid grid-cols-2 gap-4">
        <router-link to="/admin/gestion" class="bg-blue-600 text-white p-6 rounded text-center">
          Gestionar Vendedores
        </router-link>
        <button class="bg-green-600 text-white p-6 rounded">
          Crear Cliente
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Admin',
  data() {
    return {
      stats: {
        sellers: 0,
        clients: 0,
        visitsToday: 0,
        validCheckins: 0
      }
    }
  },
  mounted() {
    this.fetchStats()
  },
  methods: {
    async fetchStats() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/dashboard/stats/`)
        this.stats = await response.json()
      } catch (e) {
        console.error('Error fetching stats:', e)
      }
    },
    logout() {
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>