<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="px-4 py-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-3">
            <button @click="$router.back()" class="text-gray-600 hover:text-gray-900">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
              </svg>
            </button>
            <h1 class="text-xl font-bold text-gray-900">Mi Ruta (Cartera)</h1>
          </div>
        </div>
      </div>
    </nav>

    <div class="px-4 py-6 pb-20">
      <div v-if="loading" class="text-center py-10">
        <p class="text-gray-500">Cargando clientes asignados...</p>
      </div>

      <div v-else-if="customers.length > 0" class="space-y-3">
        <p class="text-gray-600 mb-4">Tienes {{ customers.length }} clientes asignados en tu cartera.</p>
        
        <div v-for="c in customers" :key="c.id" class="bg-gray-50 border border-gray-200 rounded-xl p-4">
          <div class="flex items-start gap-3">
             <div class="w-10 h-10 bg-blue-900 rounded-full flex items-center justify-center flex-shrink-0 text-white font-bold">
                {{ c.name.charAt(0).toUpperCase() }}
             </div>
             <div class="flex-1">
                <h3 class="font-bold text-gray-900">{{ c.name }}</h3>
                <p class="text-sm text-gray-600">{{ c.address }}</p>
                <div class="flex gap-2 mt-2">
                    <a :href="'tel:' + c.phone" class="text-xs bg-white border border-gray-300 px-2 py-1 rounded">📞 {{ c.phone }}</a>
                </div>
             </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-10 bg-gray-50 rounded-xl">
        <p class="text-gray-500">No tienes clientes asignados a tu ruta permanente.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "MyRoute",
  data() {
    return {
      customers: [],
      loading: true,
      seller: null
    }
  },
  mounted() {
    const sellerData = localStorage.getItem('seller')
    if (sellerData) {
      this.seller = JSON.parse(sellerData)
      this.fetchMyRoute()
    } else {
      this.$router.push('/login')
    }
  },
  methods: {
    async fetchMyRoute() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/my-route-customers/?seller_id=${this.seller.id}`)
        if (response.ok) {
          this.customers = await response.json()
        }
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
