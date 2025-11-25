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
        <p class="text-gray-600 text-sm">Dashboard de Ventas</p>
      </div>
    </nav>

    <!-- Content -->
    <div class="px-4 py-6 pb-20">
      <!-- Greeting -->
      <div class="mb-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-1">¡Hola!</h2>
        <p class="text-gray-600 text-base">{{ getDayGreeting() }}</p>
      </div>

      <!-- KPI Cards - Mobile Optimized -->
      <div class="space-y-4 mb-8">
        <!-- Card 1: Vendedores -->
        <div class="bg-gray-50 rounded-xl p-5 border border-gray-200">
          <div class="flex justify-between items-start">
            <div>
              <p class="text-gray-600 text-xs font-semibold uppercase tracking-wide">Vendedores Activos</p>
              <p class="text-4xl font-bold text-gray-900 mt-2">{{ stats.sellers }}</p>
            </div>
            <div class="w-12 h-12 bg-gray-900 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.856-1.487M15 10a3 3 0 11-6 0 3 3 0 016 0zM6 20h12v-2a9 9 0 00-18 0v2z"/>
              </svg>
            </div>
          </div>
          <p class="text-gray-500 text-sm mt-3">↑ 2 esta semana</p>
        </div>

        <!-- Card 2: Clientes -->
        <div class="bg-gray-50 rounded-xl p-5 border border-gray-200">
          <div class="flex justify-between items-start">
            <div>
              <p class="text-gray-600 text-xs font-semibold uppercase tracking-wide">Clientes Totales</p>
              <p class="text-4xl font-bold text-gray-900 mt-2">{{ stats.clients }}</p>
            </div>
            <div class="w-12 h-12 bg-gray-900 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
          <p class="text-gray-500 text-sm mt-3">↑ 15 este mes</p>
        </div>

        <!-- Card 3: Visitas -->
        <div class="bg-gray-50 rounded-xl p-5 border border-gray-200">
          <div class="flex justify-between items-start">
            <div>
              <p class="text-gray-600 text-xs font-semibold uppercase tracking-wide">Visitas Hoy</p>
              <p class="text-4xl font-bold text-gray-900 mt-2">{{ stats.visitsToday }}</p>
            </div>
            <div class="w-12 h-12 bg-gray-900 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
          <p class="text-gray-500 text-sm mt-3">{{ Math.round((stats.validCheckins / (stats.visitsToday || 1)) * 100) }}% válidas</p>
        </div>

        <!-- Card 4: Alertas -->
        <div class="bg-gray-50 rounded-xl p-5 border border-gray-200">
          <div class="flex justify-between items-start">
            <div>
              <p class="text-gray-600 text-xs font-semibold uppercase tracking-wide">Alertas de Fraude</p>
              <p class="text-4xl font-bold text-gray-900 mt-2">{{ stats.fraudDetections }}</p>
            </div>
            <div class="w-12 h-12 bg-gray-900 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4v2m0 4v2"/>
              </svg>
            </div>
          </div>
          <p class="text-gray-500 text-sm mt-3" v-if="stats.fraudDetections > 0">⚠️ Revisar</p>
          <p class="text-gray-500 text-sm mt-3" v-else>✓ Todo bien</p>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="space-y-3 mb-8">
        <router-link to="/admin/gestion" class="block bg-gray-900 text-white rounded-xl p-5 text-center font-semibold text-lg hover:bg-gray-800 transition">
          Gestionar Vendedores
        </router-link>
        <button @click="showCreateClient = true" class="w-full bg-gray-100 text-gray-900 border-2 border-gray-900 rounded-xl p-5 font-semibold text-lg hover:bg-gray-200 transition">
          Nuevo Cliente
        </button>
      </div>

      <!-- Stats Section -->
      <div class="bg-gray-50 rounded-xl border border-gray-200 p-5 mb-8">
        <h3 class="text-lg font-bold text-gray-900 mb-5">Rendimiento</h3>
        
        <div class="space-y-4">
          <!-- Quality Score -->
          <div>
            <div class="flex justify-between items-center mb-2">
              <p class="text-gray-700 font-semibold text-sm">Calidad de Check-in</p>
              <p class="text-gray-900 font-bold text-lg">{{ stats.quality_score }}</p>
            </div>
            <div class="w-full bg-gray-300 rounded-full h-2">
              <div class="bg-gray-900 h-2 rounded-full" :style="{ width: stats.quality_score }"></div>
            </div>
          </div>

          <!-- Avg Distance -->
          <div>
            <p class="text-gray-700 font-semibold text-sm mb-2">Distancia Promedio</p>
            <p class="text-gray-900 font-bold text-2xl">{{ stats.average_distance_meters }}m</p>
            <p class="text-gray-500 text-sm">Proximidad a clientes</p>
          </div>

          <!-- Last Update -->
          <div class="pt-3 border-t border-gray-300">
            <p class="text-gray-600 text-xs">Actualizado: {{ lastUpdate }}</p>
          </div>
        </div>
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
      },
      showCreateClient: false,
      lastUpdate: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
    }
  },
  mounted() {
    this.fetchStats()
    setInterval(() => this.fetchStats(), 30000)
  },
  methods: {
    async fetchStats() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/dashboard/stats/`)
        const data = await response.json()
        this.stats = data
        this.lastUpdate = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
      } catch (e) {
        console.error('Error fetching stats:', e)
      }
    },
    getDayGreeting() {
      const hour = new Date().getHours()
      if (hour < 12) return '✓ Buenos días'
      if (hour < 18) return '✓ Buenas tardes'
      return '✓ Buenas noches'
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

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
}
</style>
