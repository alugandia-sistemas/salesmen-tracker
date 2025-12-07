<template>
  <div class="h-screen flex flex-col bg-slate-50 dark:bg-slate-900 overflow-hidden relative">
    
    <!-- Header -->
    <header class="bg-slate-900 text-white p-4 flex justify-between items-center z-[50] shadow-lg border-b border-slate-800 shrink-0 h-16">
      <div class="flex items-center gap-3">
        <!-- Mobile Sidebar Toggle -->
        <button @click="toggleSidebar" class="md:hidden text-white p-1 rounded hover:bg-slate-800">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
           </svg>
        </button>
        
        <h1 class="text-xl md:text-2xl font-bold bg-gradient-to-r from-indigo-400 to-indigo-200 bg-clip-text text-transparent">
          Alugandia Admin
        </h1>
      </div>
      <div>
        <button @click="logout" class="bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg text-sm font-bold transition-colors border border-slate-700">
          Salir
        </button>
      </div>
    </header>

    <div class="flex-1 flex relative overflow-hidden">
      
      <!-- Mobile Backdrop -->
      <div 
        v-if="showSidebar" 
        @click="showSidebar = false"
        class="absolute inset-0 bg-black/50 z-20 md:hidden backdrop-blur-sm transition-opacity"
      ></div>

      <!-- Sidebar Navigation -->
      <aside 
         class="absolute md:relative inset-y-0 left-0 w-3/4 md:w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col shadow-2xl z-30 transition-transform duration-300 transform"
         :class="showSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
      >
        <div class="p-4 space-y-1 flex-1 overflow-y-auto">
           <p class="px-4 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Gestión</p>
           
           <button 
             @click="activeTab = 'vendedores'; showSidebar = false"
             :class="['w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-bold text-sm', activeTab === 'vendedores' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700']"
           >
             <span class="text-xl">👥</span> Vendedores
           </button>
           
           <button 
             @click="activeTab = 'clientes'; showSidebar = false"
             :class="['w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-bold text-sm', activeTab === 'clientes' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700']"
           >
             <span class="text-xl">🏢</span> Clientes
           </button>
           
           <button 
             @click="activeTab = 'rutas'; showSidebar = false"
             :class="['w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-bold text-sm', activeTab === 'rutas' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700']"
           >
             <span class="text-xl">🗺️</span> Rutas
           </button>
           
           <div class="my-4 border-t border-slate-100 dark:border-slate-700"></div>
           <p class="px-4 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Accesos</p>

           <button 
             @click="$router.push('/admin/invitaciones')"
             class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 font-bold text-sm transition-all"
           >
             <span class="text-xl">📧</span> Invitaciones
           </button>
           
           <button 
             @click="$router.push('/admin/zones')"
             class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 hover:bg-indigo-100 dark:hover:bg-indigo-900/40 font-bold text-sm transition-all"
           >
             <span class="text-xl">🌍</span> Mapa Zonas
           </button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-900 w-full relative">
        <div class="max-w-5xl mx-auto p-4 md:p-8 pb-24 md:pb-8">
          
          <!-- VENDEDORES TAB -->
          <transition name="fade" mode="out-in">
          <div v-if="activeTab === 'vendedores'" key="vendedores">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white">Vendedores</h2>
              <button 
                @click="showVendedorModal = true" 
                class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold shadow-lg hover:bg-indigo-500 transition text-sm flex items-center gap-2"
              >
                <span>+</span> <span class="hidden md:inline">Nuevo Vendedor</span>
              </button>
            </div>
    
            <div v-if="vendedores.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div v-for="vendedor in vendedores" :key="vendedor.id" class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-5 shadow-sm hover:shadow-md transition">
                <div class="flex items-start gap-4 mb-4">
                  <div class="w-12 h-12 bg-slate-900 dark:bg-indigo-900 rounded-full flex items-center justify-center flex-shrink-0 text-white font-bold text-lg">
                    {{ vendedor.name.charAt(0).toUpperCase() }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white truncate">{{ vendedor.name }}</h3>
                    <p class="text-slate-500 dark:text-slate-400 text-sm truncate">{{ vendedor.email }}</p>
                  </div>
                </div>
                <div class="space-y-2 mb-4">
                  <p class="text-slate-700 dark:text-slate-300 text-sm flex items-center gap-2">📞 {{ vendedor.phone }}</p>
                  <span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wide"
                    :class="vendedor.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300' : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'">
                    {{ vendedor.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
                <div class="flex gap-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                  <button @click="editVendedor(vendedor)" class="flex-1 py-2 text-sm font-bold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-lg transition">
                    Editar
                  </button>
                  <button @click="deleteVendedor(vendedor.id)" class="flex-1 py-2 text-sm font-bold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-900/30 rounded-lg transition">
                    Eliminar
                  </button>
                </div>
              </div>
            </div>
            
            <div v-else class="text-center py-12 bg-white dark:bg-slate-800 rounded-xl border border-dashed border-slate-300 dark:border-slate-700">
              <p class="text-slate-500 dark:text-slate-400 mb-4">No hay vendedores registrados</p>
              <button @click="showVendedorModal = true" class="text-indigo-600 font-bold hover:underline">Crear el primero</button>
            </div>
          </div>
    
          <!-- CLIENTES TAB -->
          <div v-else-if="activeTab === 'clientes'" key="clientes">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white">Clientes</h2>
              <div class="flex gap-2">
                 <button 
                  @click="showClienteModal = true" 
                  class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold shadow-lg hover:bg-indigo-500 transition text-sm flex items-center gap-2"
                >
                  <span>+</span> <span class="hidden md:inline">Nuevo Cliente</span>
                </button>
              </div>
            </div>
            
             <!-- Stats Overview -->
             <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                <div class="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700 text-center">
                  <span class="block text-2xl font-bold text-slate-900 dark:text-white">{{ clientes.length }}</span>
                  <span class="text-xs font-bold text-slate-500 uppercase">Total</span>
                </div>
                <div class="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700 text-center">
                  <span class="block text-2xl font-bold text-slate-900 dark:text-white">{{ contarPorTipo('carpintero_metalico') }}</span>
                  <span class="text-xs font-bold text-slate-500 uppercase">Carpinteros</span>
                </div>
                <div class="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700 text-center">
                  <span class="block text-2xl font-bold text-slate-900 dark:text-white">{{ contarPorTipo('cristalero') }}</span>
                  <span class="text-xs font-bold text-slate-500 uppercase">Cristaleros</span>
                </div>
             </div>
    
            <!-- Recientes List -->
            <h3 class="text-sm font-bold text-slate-500 uppercase mb-3 px-1">Añadidos Recientemente</h3>
            <div v-if="clientes.length > 0" class="space-y-3">
              <div v-for="cliente in clientesRecientes" :key="cliente.id" class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-4 shadow-sm hover:shadow-md transition flex items-center justify-between group">
                <div class="flex items-center gap-4 min-w-0">
                  <div class="w-10 h-10 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center flex-shrink-0 text-slate-600 dark:text-slate-300 font-bold">
                    {{ cliente.name.charAt(0).toUpperCase() }}
                  </div>
                  <div class="min-w-0">
                    <h4 class="text-base font-bold text-slate-900 dark:text-white truncate">{{ cliente.name }}</h4>
                    <p class="text-slate-500 dark:text-slate-400 text-sm truncate flex items-center gap-1">📍 {{ cliente.address }}</p>
                  </div>
                </div>
                <button @click="editCliente(cliente)" class="p-2 text-slate-400 hover:text-indigo-600 transition">
                   ✏️
                </button>
              </div>
              
              <button 
                @click="$router.push('/admin/clientes')"
                class="w-full py-3 mt-4 text-center text-indigo-600 font-bold hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-xl transition border border-indigo-100 dark:border-indigo-900/30"
              >
                Ver Directorio Completo →
              </button>
            </div>
            
            <div v-else class="text-center py-12 bg-white dark:bg-slate-800 rounded-xl border border-dashed border-slate-300 dark:border-slate-700">
               <p class="text-slate-500 mb-2">No tienes clientes aún.</p>
               <button @click="showClienteModal = true" class="text-indigo-600 font-bold">Añadir Cliente</button>
            </div>
          </div>
    
          <!-- RUTAS TAB -->
          <div v-else-if="activeTab === 'rutas'" key="rutas">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white">Rutas</h2>
              <button 
                @click="showRutaModal = true" 
                class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold shadow-lg hover:bg-indigo-500 transition text-sm flex items-center gap-2"
              >
                <span>+</span> <span class="hidden md:inline">Nueva Ruta</span>
              </button>
            </div>
    
            <div v-if="rutas.length > 0" class="space-y-3">
              <div v-for="ruta in rutas" :key="ruta.id" class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-4 shadow-sm relative overflow-hidden">
                 <!-- Status Bar -->
                 <div class="absolute left-0 top-0 bottom-0 w-1 bg-slate-200" :class="{
                    'bg-slate-300': ruta.status === 'pending',
                    'bg-emerald-500': ruta.status === 'completed',
                    'bg-indigo-500': ruta.status === 'in_progress',
                    'bg-rose-500': ruta.status === 'cancelled'
                 }"></div>
                 
                 <div class="pl-3">
                    <div class="flex justify-between items-start mb-2">
                       <div>
                          <p class="text-xs font-bold text-slate-500 uppercase tracking-wide">Vendedor</p>
                          <h3 class="text-base font-bold text-slate-900 dark:text-white">{{ getNombreVendedor(ruta.seller_id) }}</h3>
                       </div>
                       <span class="px-2 py-1 rounded-md text-xs font-bold uppercase" :class="{
                             'bg-slate-100 text-slate-600': ruta.status === 'pending',
                             'bg-emerald-100 text-emerald-700': ruta.status === 'completed',
                             'bg-indigo-100 text-indigo-700': ruta.status === 'in_progress',
                             'bg-rose-100 text-rose-700': ruta.status === 'cancelled'
                       }">
                         {{ ruta.status }}
                       </span>
                    </div>
                    
                    <div class="mb-3">
                        <p class="text-xs font-bold text-slate-500 uppercase tracking-wide">Cliente</p>
                        <p class="text-slate-700 dark:text-slate-300 font-medium">📍 {{ getNombreCliente(ruta.client_id) }}</p>
                    </div>
                    
                    <div class="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-700">
                        <span class="text-sm font-mono text-slate-500">{{ formatDate(ruta.planned_date) }}</span>
                        <div class="flex gap-2">
                           <button @click="editRuta(ruta)" class="text-indigo-600 font-bold text-sm hover:underline">Editar</button>
                           <button @click="deleteRuta(ruta.id)" class="text-rose-600 font-bold text-sm hover:underline">Eliminar</button>
                        </div>
                    </div>
                 </div>
              </div>
            </div>
            
            <div v-else class="text-center py-12 bg-white dark:bg-slate-800 rounded-xl border border-dashed border-slate-300 dark:border-slate-700">
              <p class="text-slate-500 mb-2">No hay rutas asignadas.</p>
              <button @click="showRutaModal = true" class="text-indigo-600 font-bold">Crear Ruta Manual</button>
            </div>
          </div>
          </transition>
        </div>
      </main>
    </div>

    <!-- MODALES (Re-styled minimally for consistency) -->
    <!-- Modal Vendedor -->
    <div v-if="showVendedorModal" class="fixed inset-0 bg-black/50 z-[60] flex items-end md:items-center justify-center backdrop-blur-sm p-0 md:p-4">
      <div class="bg-white dark:bg-slate-900 w-full md:max-w-md md:rounded-2xl rounded-t-3xl shadow-2xl p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-6">
          {{ editingVendedor ? 'Editar Vendedor' : 'Nuevo Vendedor' }}
        </h3>
        <form @submit.prevent="saveVendedor" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Nombre</label>
            <input v-model="formVendedor.name" type="text" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-4 py-3 font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none" required />
          </div>

          <div>
             <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Email</label>
             <input v-model="formVendedor.email" type="email" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-4 py-3 font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none" required />
          </div>

          <div>
             <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Teléfono</label>
             <input v-model="formVendedor.phone" type="tel" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-4 py-3 font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none" required />
          </div>

          <div class="flex items-center gap-3 py-2">
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="formVendedor.is_active" class="sr-only peer">
              <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
              <span class="ml-3 text-sm font-bold text-slate-700 dark:text-slate-300">Vendedor Activo</span>
            </label>
          </div>
          
          <div class="flex gap-3 pt-4">
            <button type="button" @click="closeVendedorModal()" class="flex-1 py-3 text-slate-600 dark:text-slate-400 font-bold hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">Cancelar</button>
            <button type="submit" class="flex-1 py-3 bg-indigo-600 text-white font-bold rounded-lg shadow-md hover:bg-indigo-500">{{ editingVendedor ? 'Guardar' : 'Crear' }}</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Modal Cliente (Simplified Styles) -->
    <div v-if="showClienteModal" class="fixed inset-0 bg-black/50 z-[60] flex items-end md:items-center justify-center backdrop-blur-sm p-0 md:p-4">
      <div class="bg-white dark:bg-slate-900 w-full md:max-w-lg md:rounded-2xl rounded-t-3xl shadow-2xl p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-4">
          {{ editingCliente ? 'Editar Cliente' : 'Nuevo Cliente' }}
        </h3>
        <form @submit.prevent="saveCliente" class="space-y-3">
          <!-- Two col grid for basic info -->
          <div class="grid grid-cols-2 gap-3">
             <div class="col-span-2">
                <label class="label-driver-sm">Nombre</label>
                <input v-model="formCliente.name" type="text" class="input-driver-sm" required />
             </div>
             <div class="col-span-2">
                <label class="label-driver-sm">Dirección</label>
                <input v-model="formCliente.address" type="text" class="input-driver-sm" required />
             </div>
             <div>
                <label class="label-driver-sm">Teléfono</label>
                <input v-model="formCliente.phone" type="tel" class="input-driver-sm" required />
             </div>
             <div>
                <label class="label-driver-sm">Tipo</label>
                <select v-model="formCliente.client_type" class="input-driver-sm" required>
                  <option value="">-- Selecciona --</option>
                  <option value="carpintero_metalico">🔧 Carpintero</option>
                  <option value="cristalero">🪟 Cristalero</option>
                  <option value="taller">🏭 Taller</option>
                  <option value="instalador">🔨 Instalador</option>
                  <option value="cerrajero">🔑 Cerrajero</option>
                  <option value="constructor">🏗️ Constructor</option>
                  <option value="otros">📦 Otros</option>
                </select>
             </div>
          </div>
          
          <!-- Geo Section -->
          <div class="bg-indigo-50 dark:bg-slate-800 rounded-xl p-4 border border-indigo-100 dark:border-slate-700">
             <h4 class="text-xs font-bold text-indigo-800 dark:text-indigo-400 uppercase mb-2">📍 Coordenadas</h4>
             <div class="grid grid-cols-2 gap-3">
                <div>
                   <label class="text-xs font-bold text-slate-500">Latitud</label>
                   <input v-model.number="formCliente.latitude" type="number" step="0.0001" class="input-driver-sm bg-white dark:bg-slate-900" required />
                </div>
                <div>
                   <label class="text-xs font-bold text-slate-500">Longitud</label>
                   <input v-model.number="formCliente.longitude" type="number" step="0.0001" class="input-driver-sm bg-white dark:bg-slate-900" required />
                </div>
             </div>
             <p class="text-[10px] text-slate-500 mt-2">Usa Google Maps para obtener las coordenadas exactas.</p>
          </div>

          <div class="flex gap-3 pt-4">
            <button type="button" @click="closeClienteModal()" class="flex-1 py-3 text-slate-600 dark:text-slate-400 font-bold hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">Cancelar</button>
            <button type="submit" class="flex-1 py-3 bg-indigo-600 text-white font-bold rounded-lg shadow-md hover:bg-indigo-500">{{ editingCliente ? 'Guardar' : 'Crear' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Ruta (Simplified) -->
    <div v-if="showRutaModal" class="fixed inset-0 bg-black/50 z-[60] flex items-end md:items-center justify-center backdrop-blur-sm p-0 md:p-4">
      <div class="bg-white dark:bg-slate-900 w-full md:max-w-md md:rounded-2xl rounded-t-3xl shadow-2xl p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-6">
          {{ editingRuta ? 'Editar Ruta' : 'Nueva Ruta' }}
        </h3>
        <form @submit.prevent="saveRuta" class="space-y-4">
           <div>
            <label class="label-driver-sm">Vendedor</label>
            <select v-model="formRuta.seller_id" class="input-driver-sm" required>
              <option value="">-- Selecciona --</option>
              <option v-for="v in vendedores" :key="v.id" :value="v.id">{{ v.name }}</option>
            </select>
          </div>

          <div>
            <label class="label-driver-sm">Cliente</label>
            <select v-model="formRuta.client_id" class="input-driver-sm" required>
              <option value="">-- Selecciona --</option>
              <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>

          <div>
            <label class="label-driver-sm">Fecha</label>
            <input v-model="formRuta.planned_date" type="date" class="input-driver-sm" required />
          </div>

          <div>
            <label class="label-driver-sm">Estado</label>
            <select v-model="formRuta.status" class="input-driver-sm" required>
              <option value="pending">⏳ Pendiente</option>
              <option value="in_progress">🚀 En Progreso</option>
              <option value="completed">✅ Completada</option>
              <option value="cancelled">❌ Cancelada</option>
            </select>
          </div>
          
          <div class="flex gap-3 pt-4">
            <button type="button" @click="closeRutaModal()" class="flex-1 py-3 text-slate-600 dark:text-slate-400 font-bold hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">Cancelar</button>
            <button type="submit" class="flex-1 py-3 bg-indigo-600 text-white font-bold rounded-lg shadow-md hover:bg-indigo-500">{{ editingRuta ? 'Guardar' : 'Crear' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminPanel',
  data() {
    return {
      activeTab: 'vendedores',
      showSidebar: false, // NEW: Sidebar toggle
      vendedores: [],
      clientes: [],
      rutas: [],
      
      showVendedorModal: false,
      showClienteModal: false,
      showRutaModal: false,
      
      editingVendedor: null,
      editingCliente: null,
      editingRuta: null,
      
      formVendedor: { name: '', email: '', phone: '', is_active: true },
      formCliente: { name: '', address: '', phone: '', email: '', latitude: 0, longitude: 0, client_type: '' },
      formRuta: { seller_id: '', client_id: '', planned_date: '', status: 'pending' },
      
      // Mapeo de tipos de cliente
      tiposCliente: {
        'carpintero_metalico': '🔧 Carpintero Metálico',
        'cristalero': '🪟 Cristalero',
        'taller': '🏭 Taller Industrial',
        'instalador': '🔨 Instalador',
        'cerrajero': '🔑 Cerrajero',
        'constructor': '🏗️ Constructor',
        'otros': '📦 Otros',
        // Compatibilidad con tipos antiguos
        'carpenter': '🔧 Carpintero',
        'installer': '🔨 Instalador',
        'industrial': '🏭 Industrial'
      }
    }
  },
  computed: {
    clientesRecientes() {
      // Mostrar solo los 5 más recientes
      return this.clientes.slice(0, 5)
    }
  },
  mounted() {
    this.fetchVendedores()
    this.fetchClientes()
    this.fetchRutas()
    
    // Verificar si viene con tab específico desde query params
    const tab = this.$route.query.tab
    if (tab) {
      this.activeTab = tab
    }
  },
  methods: {
    toggleSidebar() {
      this.showSidebar = !this.showSidebar
    },
    async fetchVendedores() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/sellers/`)
        this.vendedores = await response.json()
      } catch (e) {
        console.error('Error fetching vendedores:', e)
      }
    },
    async fetchClientes() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/clients/`)
        this.clientes = await response.json()
      } catch (e) {
        console.error('Error fetching clientes:', e)
      }
    },
    async fetchRutas() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/`)
        this.rutas = await response.json()
      } catch (e) {
        console.error('Error fetching rutas:', e)
      }
    },
    
    // Contar clientes por tipo
    contarPorTipo(tipo) {
      return this.clientes.filter(c => c.client_type === tipo).length
    },
    
    // VENDEDORES
    editVendedor(v) {
      this.editingVendedor = v.id
      this.formVendedor = { ...v }
      this.showVendedorModal = true
    },
    async saveVendedor() {
      try {
        const url = this.editingVendedor 
          ? `${import.meta.env.VITE_API_URL}/sellers/${this.editingVendedor}`
          : `${import.meta.env.VITE_API_URL}/sellers/`
        const method = this.editingVendedor ? 'PUT' : 'POST'
        
        await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.formVendedor)
        })
        this.fetchVendedores()
        this.closeVendedorModal()
      } catch (e) {
        console.error('Error saving vendedor:', e)
      }
    },
    async deleteVendedor(id) {
      if (!confirm('¿Eliminar?')) return
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/sellers/${id}`, { method: 'DELETE' })
        this.fetchVendedores()
      } catch (e) {
        console.error('Error deleting vendedor:', e)
      }
    },
    closeVendedorModal() {
      this.showVendedorModal = false
      this.editingVendedor = null
      this.formVendedor = { name: '', email: '', phone: '', is_active: true }
    },
    
    // CLIENTES
    editCliente(c) {
      this.editingCliente = c.id
      this.formCliente = {
        name: c.name,
        address: c.address,
        phone: c.phone,
        email: c.email,
        latitude: c.latitude,
        longitude: c.longitude,
        client_type: c.client_type
      }
      this.showClienteModal = true
    },
    async saveCliente() {
      try {
        const url = this.editingCliente 
          ? `${import.meta.env.VITE_API_URL}/clients/${this.editingCliente}`
          : `${import.meta.env.VITE_API_URL}/clients/`
        const method = this.editingCliente ? 'PUT' : 'POST'
        
        await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.formCliente)
        })
        this.fetchClientes()
        this.closeClienteModal()
      } catch (e) {
        console.error('Error saving cliente:', e)
      }
    },
    async deleteCliente(id) {
      if (!confirm('¿Eliminar?')) return
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/clients/${id}`, { method: 'DELETE' })
        this.fetchClientes()
      } catch (e) {
        console.error('Error deleting cliente:', e)
      }
    },
    closeClienteModal() {
      this.showClienteModal = false
      this.editingCliente = null
      this.formCliente = { name: '', address: '', phone: '', email: '', latitude: 0, longitude: 0, client_type: '' }
    },
    
    // RUTAS
    editRuta(r) {
      this.editingRuta = r.id
      this.formRuta = { ...r }
      this.showRutaModal = true
    },
    async saveRuta() {
      try {
        const url = this.editingRuta 
          ? `${import.meta.env.VITE_API_URL}/routes/${this.editingRuta}`
          : `${import.meta.env.VITE_API_URL}/routes/`
        const method = this.editingRuta ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            seller_id: this.formRuta.seller_id,
            client_id: this.formRuta.client_id,
            planned_date: this.formRuta.planned_date,
            status: this.formRuta.status
          })
        })
        
        if (!response.ok) {
          const error = await response.json()
          alert(`Error: ${error.detail || 'Error al guardar ruta'}`)
          return
        }
        
        this.fetchRutas()
        this.closeRutaModal()
      } catch (e) {
        console.error('Error saving ruta:', e)
        alert(`Error: ${e.message}`)
      }
    },
    async deleteRuta(id) {
      if (!confirm('¿Eliminar?')) return
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/routes/${id}`, { method: 'DELETE' })
        this.fetchRutas()
      } catch (e) {
        console.error('Error deleting ruta:', e)
      }
    },
    closeRutaModal() {
      this.showRutaModal = false
      this.editingRuta = null
      this.formRuta = { seller_id: '', client_id: '', planned_date: '', status: 'pending' }
    },
    
    // HELPERS
    getTipoCliente(type) {
      return this.tiposCliente[type] || type
    },
    getNombreVendedor(id) {
      const v = this.vendedores.find(x => x.id === id)
      return v ? v.name : 'Desconocido'
    },
    getNombreCliente(id) {
      const c = this.clientes.find(x => x.id === id)
      return c ? c.name : 'Desconocido'
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    },
    logout() {
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.label-driver-sm {
  @apply block text-xs font-bold text-slate-500 uppercase mb-1;
}
.input-driver-sm {
  @apply w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none;
}
</style>
