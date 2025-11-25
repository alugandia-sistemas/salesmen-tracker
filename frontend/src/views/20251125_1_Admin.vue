<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
    <!-- Header -->
    <nav class="bg-gradient-to-r from-red-600 to-red-700 text-white shadow-lg sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-white rounded-lg flex items-center justify-center">
            <span class="text-red-600 font-bold text-xl">AT</span>
          </div>
          <h1 class="text-2xl font-bold">Alugandia Tracker</h1>
        </div>
        <div class="flex items-center gap-6">
          <router-link to="/admin/gestion" class="hover:bg-red-500 px-4 py-2 rounded-lg transition">
            Gestión
          </router-link>
          <button @click="logout" class="bg-white text-red-600 px-4 py-2 rounded-lg font-bold hover:bg-red-50 transition">
            Logout
          </button>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- Greeting -->
      <div class="mb-8">
        <h2 class="text-4xl font-bold text-white mb-2">¡Hola, Director!</h2>
        <p class="text-gray-400">{{ new Date().toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
      </div>

      <!-- KPI Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Vendedores Card -->
        <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl hover:shadow-2xl transition">
          <div class="flex justify-between items-start mb-4">
            <div>
              <p class="text-blue-100 text-sm font-semibold">VENDEDORES ACTIVOS</p>
              <p class="text-4xl font-bold mt-2">{{ stats.sellers }}</p>
            </div>
            <div class="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.856-1.487M15 10a3 3 0 11-6 0 3 3 0 016 0zM6 20h12v-2a9 9 0 00-18 0v2z"/>
              </svg>
            </div>
          </div>
          <p class="text-blue-100 text-sm">↑ 2 esta semana</p>
        </div>

        <!-- Clientes Card -->
        <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl p-6 text-white shadow-xl hover:shadow-2xl transition">
          <div class="flex justify-between items-start mb-4">
            <div>
              <p class="text-emerald-100 text-sm font-semibold">CLIENTES TOTALES</p>
              <p class="text-4xl font-bold mt-2">{{ stats.clients }}</p>
            </div>
            <div class="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
          <p class="text-emerald-100 text-sm">↑ 15 este mes</p>
        </div>

        <!-- Visitas Hoy Card -->
        <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-white shadow-xl hover:shadow-2xl transition">
          <div class="flex justify-between items-start mb-4">
            <div>
              <p class="text-orange-100 text-sm font-semibold">VISITAS HOY</p>
              <p class="text-4xl font-bold mt-2">{{ stats.visitsToday }}</p>
            </div>
            <div class="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
          <p class="text-orange-100 text-sm">{{ Math.round((stats.validCheckins / (stats.visitsToday || 1)) * 100) }}% validadas</p>
        </div>

        <!-- Alertas Fraude Card -->
        <div class="bg-gradient-to-br from-red-500 to-red-600 rounded-2xl p-6 text-white shadow-xl hover:shadow-2xl transition">
          <div class="flex justify-between items-start mb-4">
            <div>
              <p class="text-red-100 text-sm font-semibold">ALERTAS FRAUDE</p>
              <p class="text-4xl font-bold mt-2">{{ stats.fraudDetections }}</p>
            </div>
            <div class="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4v2m0 4v2M7.08 6.47A9.002 9.002 0 1012 21c2.485 0 4.82-.652 6.842-1.794M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </div>
          </div>
          <p class="text-red-100 text-sm">⚠️ Revisar inmediatamente</p>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <!-- Crear Vendedor -->
        <router-link to="/admin/gestion" class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8 hover:shadow-xl transition cursor-pointer border-2 border-blue-200">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 bg-blue-500 rounded-xl flex items-center justify-center text-white">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">Gestionar Vendedores</h3>
              <p class="text-gray-600 text-sm">Crear, editar o eliminar vendedores</p>
            </div>
          </div>
        </router-link>

        <!-- Crear Cliente -->
        <button @click="showCreateClient = true" class="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-2xl p-8 hover:shadow-xl transition text-left border-2 border-emerald-200">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 bg-emerald-500 rounded-xl flex items-center justify-center text-white">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">Nuevo Cliente</h3>
              <p class="text-gray-600 text-sm">Agregar cliente a la base de datos</p>
            </div>
          </div>
        </button>
      </div>

      <!-- Stats Section -->
      <div class="bg-white rounded-2xl shadow-lg p-8">
        <h3 class="text-2xl font-bold text-gray-900 mb-6">Rendimiento del Equipo</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Quality Score -->
          <div class="border-l-4 border-blue-500 pl-6">
            <p class="text-gray-600 text-sm font-semibold">CALIDAD DE CHECK-IN</p>
            <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.quality_score }}</p>
            <p class="text-gray-500 text-sm mt-2">Validaciones exitosas</p>
          </div>

          <!-- Avg Distance -->
          <div class="border-l-4 border-emerald-500 pl-6">
            <p class="text-gray-600 text-sm font-semibold">DISTANCIA PROMEDIO</p>
            <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.average_distance_meters }}m</p>
            <p class="text-gray-500 text-sm mt-2">Proximidad a clientes</p>
          </div>

          <!-- Total Visits -->
          <div class="border-l-4 border-orange-500 pl-6">
            <p class="text-gray-600 text-sm font-semibold">VISITAS TOTALES</p>
            <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.total_visits_this_month || 0 }}</p>
            <p class="text-gray-500 text-sm mt-2">Este mes</p>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-8 text-center text-gray-500 text-sm">
        <p>Última actualización: {{ lastUpdate }}</p>
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
        validCheckins: 0,
        fraudDetections: 0,
        quality_score: '0%',
        average_distance_meters: 0,
        total_visits_this_month: 0
      },
      showCreateClient: false,
      lastUpdate: new Date().toLocaleTimeString('es-ES')
    }
  },
  mounted() {
    this.fetchStats()
    // Actualizar cada 30 segundos
    setInterval(() => this.fetchStats(), 30000)
  },
  methods: {
    async fetchStats() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/dashboard/stats/`)
        const data = await response.json()
        this.stats = {
          ...data,
          total_visits_this_month: Math.floor(data.total_visits_today * 4.3) // Estimación
        }
        this.lastUpdate = new Date().toLocaleTimeString('es-ES')
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

<style scoped>
/* Smooth transitions */
* {
  transition: all 0.3s ease;
}
</style>
