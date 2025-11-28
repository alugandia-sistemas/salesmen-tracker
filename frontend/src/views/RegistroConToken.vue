<template>
  <div class="min-h-screen bg-white flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900">Alugandia</h1>
        <p class="text-gray-600 mt-2">Completar Registro</p>
      </div>

      <!-- Card -->
      <div class="bg-white border-2 border-gray-200 rounded-2xl p-8 shadow-lg">
        <!-- Sin Token -->
        <div v-if="!token" class="text-center">
          <div class="bg-red-50 border-2 border-red-200 rounded-lg p-6 mb-6">
            <p class="text-red-900 font-semibold mb-2">❌ Token no proporcionado</p>
            <p class="text-red-800 text-sm">Necesitas un link de invitación para registrarte</p>
          </div>
          <p class="text-gray-600 text-sm">Solicita una invitación al administrador de Alugandia</p>
        </div>

        <!-- Validando Token -->
        <div v-else-if="validandoToken" class="text-center">
          <p class="text-gray-600">⏳ Validando invitación...</p>
        </div>

        <!-- Token Inválido -->
        <div v-else-if="tokenInvalido" class="text-center">
          <div class="bg-red-50 border-2 border-red-200 rounded-lg p-6 mb-6">
            <p class="text-red-900 font-semibold mb-2">❌ {{ tokenInvalido }}</p>
          </div>
          <p class="text-gray-600 text-sm mb-6">El link de invitación es inválido, expirado o ya ha sido usado.</p>
          <router-link to="/login" class="text-gray-900 font-semibold hover:underline">
            Volver a inicio de sesión
          </router-link>
        </div>

        <!-- Formulario Válido -->
        <div v-else-if="tokenValido">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Registrarse</h2>

          <form @submit.prevent="registrar" class="space-y-5">
            <!-- Email (readonly) -->
            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">Email</label>
              <div class="px-4 py-3 bg-gray-100 border-2 border-gray-300 rounded-lg text-gray-900 font-semibold">
                {{ emailToken }}
              </div>
              <p class="text-gray-500 text-xs mt-1">✅ Confirmado en tu invitación</p>
            </div>

            <!-- Nombre (readonly) -->
            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">Nombre</label>
              <div class="px-4 py-3 bg-gray-100 border-2 border-gray-300 rounded-lg text-gray-900 font-semibold">
                {{ nombreToken }}
              </div>
              <p class="text-gray-500 text-xs mt-1">✅ Confirmado en tu invitación</p>
            </div>

            <!-- Teléfono (readonly) -->
            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">Teléfono</label>
              <div class="px-4 py-3 bg-gray-100 border-2 border-gray-300 rounded-lg text-gray-900 font-semibold">
                {{ telefonoToken }}
              </div>
              <p class="text-gray-500 text-xs mt-1">✅ Confirmado en tu invitación</p>
            </div>

            <!-- Contraseña -->
            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">Contraseña</label>
              <input 
                v-model="password" 
                type="password"
                placeholder="••••••••"
                class="w-full px-4 py-3 text-lg text-gray-900 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 placeholder-gray-500"
                required
              />
              <p class="text-gray-500 text-xs mt-1">Mínimo 6 caracteres</p>
            </div>

            <!-- Confirmar Contraseña -->
            <div>
              <label class="block text-sm font-semibold text-gray-900 mb-2">Confirmar Contraseña</label>
              <input 
                v-model="passwordConfirm" 
                type="password"
                placeholder="••••••••"
                class="w-full px-4 py-3 text-lg text-gray-900 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 placeholder-gray-500"
                required
              />
            </div>

            <!-- Botón Submit -->
            <button 
              type="submit"
              :disabled="loading"
              class="w-full bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {{ loading ? '⏳ Registrando...' : '✅ Crear Cuenta' }}
            </button>
          </form>

          <!-- Error -->
          <div v-if="error" class="mt-4 p-4 bg-red-50 border-2 border-red-200 rounded-lg">
            <p class="text-red-900 font-semibold text-sm">❌ {{ error }}</p>
          </div>

          <!-- Info -->
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
  </div>
</template>

<script>
export default {
  name: 'RegistroConToken',
  data() {
    return {
      token: null,
      tokenValido: false,
      tokenInvalido: null,
      validandoToken: false,
      
      emailToken: '',
      nombreToken: '',
      telefonoToken: '',
      
      password: '',
      passwordConfirm: '',
      
      loading: false,
      error: null
    }
  },
  mounted() {
    this.obtenerToken()
  },
  methods: {
    obtenerToken() {
      // Obtener token de la URL
      const params = new URLSearchParams(window.location.search)
      this.token = params.get('token')
      
      if (!this.token) {
        this.tokenInvalido = 'No se proporcionó un token de invitación'
        return
      }
      
      // Validar token en backend
      this.validarToken()
    },

    async validarToken() {
      this.validandoToken = true
      this.error = null

      try {
        // En una implementación real, validarías el token en el backend
        // Por ahora, simulamos una respuesta exitosa
        
        // IMPORTANTE: Aquí debería hacer un GET a /admin/invitations/validate/{token}
        // pero como no lo implementamos, asumimos que es válido
        
        // En producción descomentar:
        /*
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/invitations/validate/${this.token}`
        )
        
        if (!response.ok) {
          const data = await response.json()
          this.tokenInvalido = data.detail || 'Token inválido o expirado'
          return
        }
        
        const data = await response.json()
        this.emailToken = data.email
        this.nombreToken = data.seller_name
        this.telefonoToken = data.seller_phone
        */
        
        // DEMO: Simular datos del token
        this.emailToken = 'vendedor@alugandia.com'
        this.nombreToken = 'Nuevo Vendedor'
        this.telefonoToken = '+34 600 000 000'
        
        this.tokenValido = true
      } catch (e) {
        this.tokenInvalido = 'Error al validar el token: ' + e.message
      } finally {
        this.validandoToken = false
      }
    },

    async registrar() {
      this.error = null

      // Validaciones
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
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/auth/register-with-token/`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              token: this.token,
              password: this.password
            })
          }
        )

        if (!response.ok) {
          const errorData = await response.json()
          this.error = errorData.detail || 'Error al registrarse'
          return
        }

        const data = await response.json()

        // Registro exitoso
        alert('✅ Cuenta creada exitosamente. Inicia sesión con tu email.')
        
        // Guardar datos para el login
        localStorage.setItem('lastEmail', this.emailToken)
        
        // Redirigir a login
        this.$router.push('/login')
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
