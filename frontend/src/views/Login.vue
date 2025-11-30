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
        // Validar contra backend
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/auth/login/`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: this.email,
              password: this.password
            })
          }
        )

        if (!response.ok) {
          const errorData = await response.json()
          this.error = errorData.detail || 'Email o contraseña incorrectos'
          return
        }

        const seller = await response.json()

        // Guardar en localStorage
        localStorage.setItem('seller', JSON.stringify({
          id: seller.id,
          name: seller.name,
          email: seller.email,
          phone: seller.phone,
          is_active: seller.is_active
        }))
        localStorage.setItem('token', 'token-' + seller.id + '-' + Date.now())

        // Redirigir a dashboard
        this.$router.push('/comercial')
      } catch (e) {
        this.error = 'Error de conexión: ' + e.message
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