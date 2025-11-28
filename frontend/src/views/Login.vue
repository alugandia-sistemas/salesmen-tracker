<template>
  <div class="min-h-screen bg-white flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900">Alugandia</h1>
        <p class="text-gray-600 mt-2">App de Vendedor</p>
      </div>

      <!-- Card -->
      <div class="bg-white border-2 border-gray-200 rounded-2xl p-8 shadow-lg">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Iniciar Sesión</h2>

        <form @submit.prevent="login" class="space-y-5">
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Email</label>
            <input 
              v-model="email" 
              type="email" 
              placeholder="tu@email.com"
              class="w-full px-4 py-3 text-lg text-gray-900 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 placeholder-gray-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Contraseña</label>
            <input 
              v-model="password" 
              type="password"
              placeholder="••••••••"
              class="w-full px-4 py-3 text-lg text-gray-900 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 placeholder-gray-500"
              required
            />
          </div>

          <button 
            type="submit"
            :disabled="loading"
            class="w-full bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ loading ? '⏳ Ingresando...' : 'Ingresar' }}
          </button>
        </form>

        <!-- Error -->
        <div v-if="error" class="mt-4 p-4 bg-red-50 border-2 border-red-200 rounded-lg">
          <p class="text-red-900 font-semibold text-sm">❌ {{ error }}</p>
        </div>

        <!-- Link Registro -->
        <div class="mt-6 text-center">
          <p class="text-gray-600 text-sm">
            ¿No tienes cuenta?
            <router-link to="/registro" class="text-gray-900 font-semibold hover:underline">
              Regístrate aquí
            </router-link>
          </p>
        </div>
      </div>

      <!-- Info -->
      <div class="mt-8 text-center text-gray-600 text-sm">
        <p>Demo: usa cualquier email y contraseña</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: null
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.error = null

      try {
        // En producción, aquí iría autenticación real
        // Por ahora, guardamos datos de demo
        const seller = {
          id: 'cc328cdb-7969-48c5-838a-f90d0f998c7b',
          name: this.email.split('@')[0],
          email: this.email,
          is_active: true
        }

        // Guardar en localStorage
        localStorage.setItem('seller', JSON.stringify(seller))
        localStorage.setItem('token', 'demo-token-' + Date.now())

        // Redirigir a dashboard
        this.$router.push('/comercial')
      } catch (e) {
        this.error = 'Error al iniciar sesión: ' + e.message
      } finally {
        this.loading = false
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
