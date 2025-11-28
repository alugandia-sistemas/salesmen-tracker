<template>
  <div class="min-h-screen bg-white flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900">Alugandia</h1>
        <p class="text-gray-600 mt-2">Crear Cuenta</p>
      </div>

      <!-- Card -->
      <div class="bg-white border-2 border-gray-200 rounded-2xl p-8 shadow-lg">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Registro</h2>

        <form @submit.prevent="registrar" class="space-y-5">
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Nombre Completo</label>
            <input 
              v-model="nombre" 
              type="text" 
              placeholder="Ej: Ernesto Arocas"
              class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Email</label>
            <input 
              v-model="email" 
              type="email" 
              placeholder="tu@email.com"
              class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Teléfono</label>
            <input 
              v-model="phone" 
              type="tel"
              placeholder="+34 600 123 456"
              class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Contraseña</label>
            <input 
              v-model="password" 
              type="password"
              placeholder="••••••••"
              class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
              required
            />
            <p class="text-gray-500 text-xs mt-1">Mínimo 6 caracteres</p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Confirmar Contraseña</label>
            <input 
              v-model="passwordConfirm" 
              type="password"
              placeholder="••••••••"
              class="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
              required
            />
          </div>

          <button 
            type="submit"
            :disabled="loading"
            class="w-full bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ loading ? '⏳ Registrando...' : 'Crear Cuenta' }}
          </button>
        </form>

        <!-- Error -->
        <div v-if="error" class="mt-4 p-4 bg-red-50 border-2 border-red-200 rounded-lg">
          <p class="text-red-900 font-semibold text-sm">❌ {{ error }}</p>
        </div>

        <!-- Link Login -->
        <div class="mt-6 text-center">
          <p class="text-gray-600 text-sm">
            ¿Ya tienes cuenta?
            <router-link to="/login" class="text-gray-900 font-semibold hover:underline">
              Inicia sesión
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Registro',
  data() {
    return {
      nombre: '',
      email: '',
      phone: '',
      password: '',
      passwordConfirm: '',
      loading: false,
      error: null
    }
  },
  methods: {
    async registrar() {
      this.error = null

      // Validar
      if (this.password.length < 6) {
        this.error = 'La contraseña debe tener mínimo 6 caracteres'
        return
      }

      if (this.password !== this.passwordConfirm) {
        this.error = 'Las contraseñas no coinciden'
        return
      }

      this.loading = true

      try {
        // En producción, aquí iría a la API
        // Por ahora, lo guardamos localmente
        const seller = {
          id: 'seller-' + Date.now(),
          name: this.nombre,
          email: this.email,
          phone: this.phone,
          is_active: true
        }

        // Guardar en localStorage
        localStorage.setItem('seller', JSON.stringify(seller))
        localStorage.setItem('token', 'demo-token-' + Date.now())

        // Redirigir a dashboard
        this.$router.push('/comercial')
      } catch (e) {
        this.error = 'Error al registrarse: ' + e.message
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
