<template>
   <div class="h-screen flex flex-col bg-slate-50 dark:bg-slate-900 overflow-hidden relative">

      <!-- Header -->
      <header class="bg-white dark:bg-slate-900 z-[50] shadow-sm shrink-0">
         <div class="px-4 py-4 flex justify-between items-center">
            <!-- Sidebar Toggle -->
            <button @click="toggleSidebar" class="md:hidden text-slate-700 dark:text-slate-200">
               <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16">
                  </path>
               </svg>
            </button>

            <div>
               <h1
                  class="text-xl font-bold bg-gradient-to-r from-indigo-600 to-indigo-400 bg-clip-text text-transparent">
                  Alugandia Tracker
               </h1>
               <div class="flex items-center gap-2 mt-1">
                  <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <p class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide">{{ sellerName
                     }}</p>
               </div>
            </div>

            <div class="flex gap-2">
               <button @click="logout"
                  class="h-10 w-10 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 flex items-center justify-center">
                  <span class="text-xl">🚪</span>
               </button>
            </div>
         </div>
      </header>

      <div class="flex-1 flex relative overflow-hidden">

         <!-- Mobile Sidebar Backdrop -->
         <div v-if="showSidebar" @click="showSidebar = false"
            class="absolute inset-0 bg-black/50 z-20 md:hidden backdrop-blur-sm transition-opacity"></div>

         <!-- Sidebar -->
         <aside
            class="absolute md:relative inset-y-0 left-0 w-3/4 md:w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col shadow-2xl z-30 transition-transform duration-300 transform"
            :class="showSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0'">
            <div class="p-4 space-y-2 flex-1">
               <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id; showSidebar = false" :class="[
                  'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-bold text-sm',
                  activeTab === tab.id
                     ? 'bg-indigo-600 text-white shadow-md'
                     : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
               ]">
                  <span class="text-xl">{{ tab.icon }}</span>
                  <span>{{ tab.label }}</span>
               </button>
            </div>

            <div class="p-4 border-t border-slate-200 dark:border-slate-700">
               <button @click="logout"
                  class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-bold text-sm text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-900/20">
                  <span class="text-xl">🚪</span>
                  <span>Cerrar Sesión</span>
               </button>
            </div>
         </aside>

         <!-- Main Content -->
         <main class="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-900 w-full relative">
            <div class="max-w-lg mx-auto p-4 md:p-6 pb-24">

               <!-- TAB: HOY (Rutas Activas) -->
               <transition name="fade" mode="out-in">
                  <div v-if="activeTab === 'hoy'" key="hoy">
                     <div class="flex justify-between items-center mb-6">
                        <div>
                           <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Rutas de Hoy</h2>
                           <p class="text-xs text-slate-500 dark:text-slate-400">{{ routesHoy.length }} paradas
                              programadas</p>
                        </div>

                        <button @click="abrirModalParada"
                           class="bg-indigo-600 text-white px-3 py-2 rounded-lg font-bold text-sm shadow-lg active:scale-95 transition-transform flex items-center gap-1">
                           <span>+</span> Parada
                        </button>
                     </div>

                     <!-- Search Bar -->
                     <div class="mb-4">
                        <input v-model="routeSearchQuery" type="text" placeholder="🔍 Buscar por cliente..."
                           class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 font-bold text-slate-900 dark:text-white shadow-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                     </div>

                     <!-- Daily Summary Stats -->
                     <div class="grid grid-cols-3 gap-3 mb-4">
                        <div class="bg-indigo-50 dark:bg-indigo-900/20 p-3 rounded-xl text-center">
                           <span class="block text-2xl font-black text-indigo-600 dark:text-indigo-400">{{
                              todayStats.total }}</span>
                           <span class="text-xs font-bold text-indigo-800 dark:text-indigo-200 uppercase">Total</span>
                        </div>
                        <div class="bg-emerald-50 dark:bg-emerald-900/20 p-3 rounded-xl text-center">
                           <span class="block text-2xl font-black text-emerald-600 dark:text-emerald-400">{{
                              todayStats.completed }}</span>
                           <span
                              class="text-xs font-bold text-emerald-800 dark:text-emerald-200 uppercase">Completadas</span>
                        </div>
                        <div class="bg-slate-50 dark:bg-slate-800 p-3 rounded-xl text-center">
                           <span class="block text-2xl font-black text-slate-900 dark:text-white">{{
                              todayStats.percentage }}%</span>
                           <span class="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase">Progreso</span>
                        </div>
                     </div>

                     <!-- Progress Bar -->
                     <div class="mb-6">
                        <div class="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                           <div class="bg-emerald-500 h-full transition-all duration-500"
                              :style="{ width: todayStats.percentage + '%' }"></div>
                        </div>
                     </div>

                     <div v-if="routesHoy.length > 0" class="space-y-4">
                        <div v-for="(ruta, index) in routesHoy" :key="ruta.id"
                           class="card-driver relative overflow-hidden group">
                           <!-- Status Line -->
                           <div class="absolute left-0 top-0 bottom-0 w-1.5" :class="{
                              'bg-slate-300': ruta.status === 'pending',
                              'bg-emerald-500': ruta.status === 'completed',
                              'bg-indigo-500': ruta.status === 'in_progress',
                              'bg-rose-500': ruta.status === 'cancelled'
                           }"></div>

                           <div class="pl-3 pr-2">
                              <!-- Header: Time, Status & Reorder -->
                              <div class="flex justify-between items-start mb-3">
                                 <div class="flex items-center gap-2">
                                    <span
                                       class="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-2 py-1 rounded text-xs font-bold font-mono">
                                       #{{ index + 1 }}
                                    </span>
                                    <span
                                       class="text-slate-500 dark:text-slate-400 font-mono text-sm font-bold flex items-center gap-1">
                                       {{ formatTime(ruta.planned_date) }}
                                    </span>
                                 </div>

                                 <!-- Reorder Controls -->
                                 <div v-if="ruta.status === 'pending'" class="flex flex-col gap-1">
                                    <button v-if="index > 0" @click.stop="moveRoute(index, -1)"
                                       class="p-1 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded">
                                       ▲
                                    </button>
                                    <button v-if="index < routesHoy.length - 1" @click.stop="moveRoute(index, 1)"
                                       class="p-1 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded">
                                       ▼
                                    </button>
                                 </div>
                              </div>

                              <div class="flex justify-between items-start">
                                 <div>
                                    <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-1 leading-tight">
                                       {{ ruta.client?.name }}
                                    </h3>
                                    <p class="text-slate-600 dark:text-slate-400 text-sm mb-4 flex items-start gap-1">
                                       📍 {{ ruta.client?.address }}
                                    </p>
                                 </div>
                                 <span class="badge-driver mt-1 shrink-0" :class="getStatusBadgeClass(ruta.status)">
                                    {{ getStatusLabel(ruta.status) }}
                                 </span>
                              </div>

                              <!-- Actions Area -->
                              <div class="grid grid-cols-2 gap-3 mt-2">
                                 <template v-if="ruta.status === 'pending'">
                                    <button @click="iniciarCheckin(ruta)" class="btn-driver-primary col-span-2">
                                       📍 CHECK-IN
                                    </button>
                                    <button @click="mostrarAplazar(ruta)" class="btn-driver-secondary text-sm h-12">
                                       ⏰ Aplazar
                                    </button>
                                    <a :href="'tel:' + ruta.client?.phone" class="btn-driver-secondary text-sm h-12">
                                       📞 Llamar
                                    </a>
                                 </template>

                                 <button v-else-if="ruta.status === 'completed'" @click="verDetalleVisita(ruta)"
                                    class="btn-driver-secondary col-span-2 text-sm">
                                    Ver Detalles
                                 </button>
                              </div>
                           </div>
                        </div>
                     </div>

                     <div v-else class="text-center py-12 px-4">
                        <div
                           class="bg-indigo-50 dark:bg-slate-800 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                           <span class="text-4xl">📅</span>
                        </div>
                        <h3 class="text-lg font-bold text-slate-900 dark:text-white mb-2">Todo listo por hoy</h3>
                        <p class="text-slate-500 dark:text-slate-400 max-w-xs mx-auto mb-6">No tienes más rutas
                           programadas.</p>
                        <button @click="abrirModalParada" class="text-indigo-600 font-bold underline">Añadir una parada
                           extra</button>
                     </div>
                  </div>

                  <!-- TAB: HISTORIAL -->
                  <div v-else-if="activeTab === 'historial'" key="historial"
                     class="flex flex-col items-center justify-center py-20 text-center">
                     <div
                        class="w-24 h-24 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6 text-4xl">
                        🚧
                     </div>
                     <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">Próximamente</h2>
                     <p class="text-slate-500 max-w-xs">El historial detallado estará disponible en la próxima
                        actualización.</p>
                  </div>

                  <!-- TAB: CLIENTES (Global Directory) -->
                  <div v-else-if="activeTab === 'clientes'" key="clientes" class="pb-24">
                     <div class="mb-6 sticky top-0 bg-slate-50 dark:bg-slate-900 pt-4 pb-2 z-40">
                        <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-4 px-4">Directorio de Clientes
                        </h2>
                        <div class="px-4">
                           <input v-model="searchQuery" type="text" placeholder="🔍 Buscar cliente..."
                              class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 font-bold text-slate-900 dark:text-white shadow-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                        </div>

                        <!-- Quick Group Nav -->
                        <div v-if="!searchQuery" class="mt-4 px-4 overflow-x-auto no-scrollbar">
                           <div class="flex gap-2 min-w-max">
                              <button v-for="grupo in gruposAlfabeticos" :key="grupo.id"
                                 @click="scrollToGroup(grupo.id)" :class="[
                                    'px-3 py-2 rounded-lg text-sm font-bold transition whitespace-nowrap border',
                                    grupoActivo === grupo.id
                                       ? 'bg-indigo-600 text-white border-indigo-600'
                                       : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700'
                                 ]">
                                 {{ grupo.label }}
                                 <span class="ml-1 text-xs opacity-70">({{ contarClientesEnGrupo(grupo.letras)
                                    }})</span>
                              </button>
                           </div>
                        </div>
                     </div>

                     <div v-if="filteredClients.length > 0">
                        <!-- Grouped View -->
                        <div v-if="!searchQuery">
                           <div v-for="grupo in gruposAlfabeticos" :key="grupo.id" :id="'grupo-' + grupo.id"
                              class="mb-6">
                              <!-- Group Header (Only if has clients) -->
                              <div v-if="clientesEnGrupo(grupo.letras).length > 0"
                                 class="px-4 mb-2 sticky top-36 bg-slate-50/95 dark:bg-slate-900/95 backdrop-blur-sm z-30 py-2">
                                 <h3 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    {{ grupo.label }}
                                    <span
                                       class="bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs px-2 py-0.5 rounded-full">
                                       {{ clientesEnGrupo(grupo.letras).length }}
                                    </span>
                                 </h3>
                              </div>

                              <div class="space-y-3 px-4">
                                 <div v-for="client in clientesEnGrupo(grupo.letras)" :key="client.id"
                                    class="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm border border-slate-200 dark:border-slate-700">
                                    <div class="flex justify-between items-start mb-2">
                                       <h3 class="font-bold text-slate-900 dark:text-white text-lg">{{ client.name }}
                                       </h3>
                                       <span
                                          class="text-xs font-bold px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded text-slate-600 dark:text-slate-300 whitespace-nowrap">
                                          {{ client.client_type || 'Cliente' }}
                                       </span>
                                    </div>
                                    <p class="text-slate-500 dark:text-slate-400 text-sm mb-3">📍 {{ client.address }}
                                    </p>

                                    <div class="flex gap-2">
                                       <button @click="addStopNow(client)"
                                          class="flex-1 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 font-bold text-xs py-2 rounded-lg hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition">
                                          + Añadir a Ruta
                                       </button>
                                       <a :href="'tel:' + client.phone"
                                          class="flex-1 bg-slate-50 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold text-xs py-2 rounded-lg text-center hover:bg-slate-100 dark:hover:bg-slate-600 transition">
                                          📞 Llamar
                                       </a>
                                    </div>
                                 </div>
                              </div>
                           </div>
                        </div>

                        <!-- Search Results (Flat list) -->
                        <div v-else class="space-y-3 px-4">
                           <div v-for="client in filteredClients" :key="client.id"
                              class="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm border border-slate-200 dark:border-slate-700">
                              <div class="flex justify-between items-start mb-2">
                                 <h3 class="font-bold text-slate-900 dark:text-white text-lg">{{ client.name }}</h3>
                                 <span
                                    class="text-xs font-bold px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded text-slate-600 dark:text-slate-300 whitespace-nowrap">
                                    {{ client.client_type || 'Cliente' }}
                                 </span>
                              </div>
                              <p class="text-slate-500 dark:text-slate-400 text-sm mb-3">📍 {{ client.address }}</p>

                              <div class="flex gap-2">
                                 <button @click="addStopNow(client)"
                                    class="flex-1 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 font-bold text-xs py-2 rounded-lg">
                                    + Añadir a Ruta
                                 </button>
                                 <a :href="'tel:' + client.phone"
                                    class="flex-1 bg-slate-50 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold text-xs py-2 rounded-lg text-center">
                                    📞 Llamar
                                 </a>
                              </div>
                           </div>
                        </div>
                     </div>
                     <div v-else class="text-center py-10 text-slate-500">
                        <p>No se encontraron clientes.</p>
                     </div>
                  </div>

                  <!-- TAB: STATS -->
                  <div v-else-if="activeTab === 'resumen'" key="resumen">
                     <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-6">Estadísticas (14 días)</h2>

                     <div v-if="stats" class="grid grid-cols-2 gap-4 mb-6">
                        <!-- Total Visits -->
                        <div
                           class="bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-2xl flex flex-col items-center justify-center text-center">
                           <span class="text-3xl font-black text-indigo-600 dark:text-indigo-400">{{ stats.total_visits
                              }}</span>
                           <span
                              class="text-xs font-bold text-indigo-800 dark:text-indigo-200 uppercase tracking-wide">Visitas
                              Totales</span>
                        </div>

                        <!-- Success Rate -->
                        <div
                           class="bg-emerald-50 dark:bg-emerald-900/20 p-4 rounded-2xl flex flex-col items-center justify-center text-center">
                           <span class="text-3xl font-black text-emerald-600 dark:text-emerald-400">{{
                              stats.completion_rate }}%</span>
                           <span
                              class="text-xs font-bold text-emerald-800 dark:text-emerald-200 uppercase tracking-wide">Tasa
                              Validez</span>
                        </div>

                        <!-- Incidents -->
                        <div class="col-span-2 p-4 rounded-2xl flex items-center justify-between"
                           :class="stats.incidents > 0 ? 'bg-rose-50 dark:bg-rose-900/20' : 'bg-slate-50 dark:bg-slate-800'">
                           <div class="flex items-center gap-3">
                              <span class="text-2xl">{{ stats.incidents > 0 ? '⚠️' : '✅' }}</span>
                              <div>
                                 <h4 class="font-bold text-slate-900 dark:text-white">Incidentes / Errores</h4>
                                 <p class="text-xs text-slate-500">Check-ins inválidos o fuera de rango</p>
                              </div>
                           </div>
                           <span class="text-2xl font-black"
                              :class="stats.incidents > 0 ? 'text-rose-600' : 'text-slate-400'">
                              {{ stats.incidents }}
                           </span>
                        </div>
                     </div>

                     <!-- Detailed List Helper -->
                     <div
                        class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 text-center">
                        <p class="text-slate-500 dark:text-slate-400 text-sm mb-4">
                           Este panel muestra tu rendimiento de las últimas 2 semanas. Si tienes incidentes, revisa tus
                           check-ins
                           anteriores en el detalle de ruta.
                        </p>
                        <button @click="fetchStats" class="text-indigo-600 font-bold text-sm hover:underline">🔄
                           Actualizar datos</button>
                     </div>
                  </div>

               </transition>
            </div>
         </main>
      </div>

      <!-- Modal Checkin -->
      <div v-if="showCheckinModal"
         class="fixed inset-0 z-[60] flex items-end sm:items-center justify-center bg-slate-900/80 backdrop-blur-sm p-0 sm:p-4">
         <div
            class="bg-white dark:bg-slate-900 w-full max-w-lg rounded-t-3xl sm:rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">

            <!-- Modal Header -->
            <div
               class="p-5 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-900">
               <div>
                  <p class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Check-in para</p>
                  <h3 class="text-xl font-bold text-slate-900 dark:text-white truncate max-w-[200px]">{{
                     rutaActual?.client?.name }}</h3>
               </div>
               <button @click="cerrarCheckin"
                  class="bg-slate-200 dark:bg-slate-800 h-10 w-10 rounded-full flex items-center justify-center text-slate-500 dark:text-slate-400 font-bold">✕</button>
            </div>

            <!-- Modal Body -->
            <div class="flex-1 overflow-y-auto p-5 space-y-6">

               <!-- GPS Status -->
               <div
                  class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 flex items-center gap-3 border border-slate-200 dark:border-slate-700">
                  <div
                     class="h-10 w-10 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center flex-shrink-0"
                     v-if="ubicacionActual">
                     📍
                  </div>
                  <div class="h-10 w-10 rounded-full bg-slate-200 animate-pulse flex-shrink-0" v-else></div>

                  <div>
                     <p class="text-sm font-bold text-slate-900 dark:text-white">
                        {{ ubicacionActual ? 'Ubicación Detectada' : 'Buscando satélites...' }}
                     </p>
                     <p class="text-xs text-slate-500 dark:text-slate-400" v-if="ubicacionActual">
                        Precisión: ±{{ ubicacionActual.accuracy.toFixed(0) }}m
                     </p>
                  </div>
               </div>

               <!-- Result Grid -->
               <div>
                  <label class="label-driver">Resultado de la visita</label>
                  <div class="grid grid-cols-2 gap-3">
                     <button v-for="res in resultadosVisita" :key="res.value" @click="visitResult = res.value"
                        class="h-16 rounded-xl border-2 font-bold flex flex-col items-center justify-center transition-all"
                        :class="visitResult === res.value
                           ? 'border-indigo-600 bg-indigo-50 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-200'
                           : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'">
                        <span class="text-xl">{{ res.icon }}</span>
                        <span class="text-sm">{{ res.label }}</span>
                     </button>
                  </div>
               </div>

               <!-- Notes -->
               <div>
                  <label class="label-driver">Notas Rápidas</label>
                  <input v-model="quickNotes" type="text" class="input-driver"
                     placeholder="Ej: Muy interesado, volver lunes" />
               </div>

               <!-- Confirm Check -->
               <label
                  class="flex items-center gap-4 bg-slate-50 dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                  <input type="checkbox" v-model="clienteEncontrado" class="w-6 h-6 accent-indigo-600 rounded">
                  <span class="font-bold text-slate-700 dark:text-slate-200">Cliente encontrado en el sitio</span>
               </label>

            </div>

            <!-- Modal Footer -->
            <div class="p-5 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800">
               <button @click="hacerCheckin" :disabled="!puedeHacerCheckin || cargandoCheckin"
                  class="btn-driver-primary disabled:opacity-50 disabled:bg-slate-300">
                  {{ cargandoCheckin ? 'Guardando...' : 'CONFIRMAR VISITA' }}
               </button>
            </div>
         </div>
      </div>

      <!-- Modal Nueva Parada -->
      <div v-if="showAddStopModal"
         class="fixed inset-0 z-[70] flex items-end sm:items-center justify-center bg-slate-900/80 backdrop-blur-sm p-0 sm:p-4">
         <div
            class="bg-white dark:bg-slate-900 w-full max-w-lg rounded-t-3xl sm:rounded-3xl shadow-2xl h-[85vh] flex flex-col">
            <div class="p-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
               <h3 class="text-lg font-bold text-slate-900 dark:text-white">Añadir Parada</h3>
               <button @click="showAddStopModal = false" class="text-slate-500 font-bold text-lg">✕</button>
            </div>

            <div class="p-4 border-b border-slate-100 dark:border-slate-800 space-y-3">
               <input v-model="searchQuery" type="text" placeholder="🔍 Buscar cliente..."
                  class="w-full bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 rounded-lg px-4 py-3 font-bold outline-none" />
               <div class="grid grid-cols-2 gap-2">
                  <div>
                     <span class="text-xs font-bold text-slate-500 block mb-1">Fecha:</span>
                     <input v-model="selectedDate" type="date"
                        class="w-full bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 rounded-lg px-4 py-3 font-bold outline-none" />
                  </div>
                  <div>
                     <span class="text-xs font-bold text-slate-500 block mb-1">Hora:</span>
                     <input v-model="selectedTime" type="time"
                        class="w-full bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 rounded-lg px-4 py-3 font-bold outline-none" />
                  </div>
               </div>
            </div>

            <div class="flex-1 overflow-y-auto p-4 space-y-2">
               <div v-for="client in filteredClients" :key="client.id" @click="addStopNow(client)"
                  class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 active:bg-indigo-50 dark:active:bg-indigo-900/20 cursor-pointer">
                  <h4 class="font-bold text-slate-900 dark:text-white">{{ client.name }}</h4>
                  <p class="text-xs text-slate-500">{{ client.address }}</p>
               </div>
            </div>
         </div>
      </div>

   </div>
</template>

<script>
export default {
   name: 'ComercialV2',
   data() {
      return {
         // Auth
         seller: null,
         sellerName: 'Vendedor',

         // UI State
         showSidebar: false,
         activeTab: 'hoy',
         tabs: [
            { id: 'hoy', label: 'Hoy', icon: '🚙' },
            { id: 'clientes', label: 'Clientes', icon: '👥' },
            { id: 'historial', label: 'Historial', icon: '📜' },
            { id: 'resumen', label: 'Stats', icon: '📊' }
         ],

         // Data
         routesHoy: [],
         historialRutas: [],
         myClients: [], // Stores all clients assigned to seller
         searchQuery: '',
         routeSearchQuery: '', // Separate search for routes in Hoy tab
         selectedDate: '',
         selectedTime: '', // Time for new route stops
         stats: null,

         // Directory Grouping
         grupoActivo: 'ac',
         gruposAlfabeticos: [
            { id: 'ac', label: 'A–C', letras: ['A', 'B', 'C'] },
            { id: 'df', label: 'D–F', letras: ['D', 'E', 'F'] },
            { id: 'gi', label: 'G–I', letras: ['G', 'H', 'I'] },
            { id: 'jl', label: 'J–L', letras: ['J', 'K', 'L'] },
            { id: 'mo', label: 'M–O', letras: ['M', 'N', 'O'] },
            { id: 'pr', label: 'P–R', letras: ['P', 'Q', 'R'] },
            { id: 'st', label: 'S–T', letras: ['S', 'T'] },
            { id: 'uz', label: 'U–Z', letras: ['U', 'V', 'W', 'X', 'Y', 'Z'] }
         ],

         // Modal State
         showCheckinModal: false,
         showAddStopModal: false,

         rutaActual: null,
         ubicacionActual: null,
         visitResult: null,
         quickNotes: '',
         clienteEncontrado: false,
         cargandoCheckin: false,

         resultadosVisita: [
            { value: 'venta', label: 'Venta', icon: '💰' },
            { value: 'interesado', label: 'Interesado', icon: '👍' },
            { value: 'seguimiento', label: 'Seguimiento', icon: '👋' },
            { value: 'no_venta', label: 'No Venta', icon: '❌' },
            { value: 'ausente', label: 'Ausente', icon: '🚪' }
         ]
      }
   },
   computed: {
      puedeHacerCheckin() {
         return this.visitResult && this.quickNotes.length > 3 && this.ubicacionActual
      },
      filteredClients() {
         if (!this.searchQuery) return this.myClients
         const lower = this.searchQuery.toLowerCase()
         return this.myClients.filter(c =>
            c.name.toLowerCase().includes(lower) ||
            c.address.toLowerCase().includes(lower)
         )
      },
      filteredRoutesHoy() {
         if (!this.routeSearchQuery) return this.routesHoy
         const lower = this.routeSearchQuery.toLowerCase()
         return this.routesHoy.filter(r =>
            r.client?.name?.toLowerCase().includes(lower)
         )
      },
      todayStats() {
         const total = this.routesHoy.length
         const completed = this.routesHoy.filter(r => r.status === 'completed').length
         const percentage = total > 0 ? Math.round((completed / total) * 100) : 0
         return { total, completed, percentage }
      }
   },
   mounted() {
      const sellerData = localStorage.getItem('seller')
      if (!sellerData) return this.$router.push('/login')

      this.seller = JSON.parse(sellerData)
      this.sellerName = this.seller.name

      this.fetchData()
      this.fetchMyClients()
      this.fetchStats()
      this.startGPS()
   },
   methods: {
      toggleSidebar() {
         this.showSidebar = !this.showSidebar
      },

      async fetchData() {
         try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/?seller_id=${this.seller.id}`)
            const all = await response.json()
            const hoy = new Date().toISOString().split('T')[0]
            // Sort already handled by backend but double check or resort local if needed
            this.routesHoy = all.filter(r => r.planned_date?.startsWith(hoy))
         } catch (e) { console.error(e) }
      },

      async fetchMyClients() {
         try {
            // Fetch ALL clients as requested, to allow adding any client to route
            const response = await fetch(`${import.meta.env.VITE_API_URL}/clients/`)
            if (response.ok) {
               this.myClients = await response.json()
            } else {
               console.error("Failed to fetch clients")
            }
         } catch (e) { console.error(e) }
      },

      async fetchStats() {
         try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/sellers/${this.seller.id}/stats`)
            if (response.ok) {
               this.stats = await response.json()
            }
         } catch (e) { console.error("Stats error", e) }
      },

      // --- REORDER LOGIC ---
      async moveRoute(index, direction) {
         if (index + direction < 0 || index + direction >= this.routesHoy.length) return;

         // Swap locally
         const temp = this.routesHoy[index];
         this.routesHoy[index] = this.routesHoy[index + direction];
         this.routesHoy[index + direction] = temp;

         // Push update to backend
         try {
            const routeIds = this.routesHoy.map(r => r.id);
            await fetch(`${import.meta.env.VITE_API_URL}/routes/reorder/`, {
               method: 'PUT',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ route_ids: routeIds })
            });
         } catch (e) {
            console.error("Failed to reorder", e);
            // Revert on error could be implemented here
         }
      },

      // --- ADD STOP LOGIC ---
      abrirModalParada() {
         this.showAddStopModal = true
         this.searchQuery = ''
         this.selectedDate = new Date().toISOString().split('T')[0] // Default to today
         // Default time to 1 hour from now
         const now = new Date()
         now.setHours(now.getHours() + 1)
         this.selectedTime = now.toTimeString().slice(0, 5) // HH:MM format
      },

      async addStopNow(client) {
         if (!this.selectedDate) {
            this.selectedDate = new Date().toISOString().split('T')[0]
         }

         if (!confirm(`¿Añadir parada para ${client.name} el ${this.selectedDate}?`)) return;

         try {
            // ✅ Combine date and time into datetime string
            let plannedDate = this.selectedDate
            if (this.selectedTime) {
               plannedDate = `${this.selectedDate}T${this.selectedTime}:00`
            }

            const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/`, {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({
                  seller_id: this.seller.id,
                  client_id: client.id,
                  planned_date: plannedDate,
                  status: 'pending'
               })
            });

            if (response.ok) {
               this.showAddStopModal = false
               // Only switch tab if date is today
               const today = new Date().toISOString().split('T')[0]
               if (this.selectedDate === today) {
                  this.activeTab = 'hoy'
               } else {
                  alert("Ruta añadida exitosamente para " + this.selectedDate)
               }
               this.fetchData() // Refresh list
            } else {
               alert("Error al añadir la ruta")
            }
         } catch (e) {
            alert("Error de red al añadir parada")
         }
      },

      startGPS() {
         if ("geolocation" in navigator) {
            navigator.geolocation.watchPosition(
               pos => {
                  this.ubicacionActual = {
                     latitude: pos.coords.latitude,
                     longitude: pos.coords.longitude,
                     accuracy: pos.coords.accuracy
                  }
               },
               err => console.error(err),
               { enableHighAccuracy: true }
            )
         }
      },

      iniciarCheckin(ruta) {
         this.rutaActual = ruta
         this.showCheckinModal = true
         this.quickNotes = ''
         this.visitResult = null
         this.clienteEncontrado = false
      },

      cerrarCheckin() {
         this.showCheckinModal = false
      },

      async hacerCheckin() {
         this.cargandoCheckin = true
         try {
            const payload = {
               route_id: this.rutaActual.id,
               seller_id: this.seller.id,
               client_id: this.rutaActual.client_id,
               latitude: this.ubicacionActual.latitude,
               longitude: this.ubicacionActual.longitude,
               visit_result: this.visitResult,
               quick_notes: this.quickNotes,
               client_found: this.clienteEncontrado
            }

            await fetch(`${import.meta.env.VITE_API_URL}/visits/checkin/v2/`, {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify(payload)
            })

            this.showCheckinModal = false
            this.fetchData() // refresh
         } catch (e) {
            alert("Error en check-in")
         } finally {
            this.cargandoCheckin = false
         }
      },

      // Helpers
      formatTime(dateStr) {
         if (!dateStr) return '--:--'
         return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      },
      formatDateShort(dateStr) {
         return new Date(dateStr).toLocaleDateString([], { month: 'short', day: 'numeric' })
      },
      getStatusLabel(status) {
         const map = { pending: 'Pendiente', completed: 'Completada', in_progress: 'En curso', cancelled: 'Cancelada' }
         return map[status] || status
      },
      getStatusBadgeClass(status) {
         const map = {
            pending: 'bg-slate-100 text-slate-600',
            completed: 'bg-emerald-100 text-emerald-800',
            in_progress: 'bg-indigo-100 text-indigo-800',
            cancelled: 'bg-rose-100 text-rose-800'
         }
         return map[status] || 'bg-gray-100'
      },
      clientesEnGrupo(letras) {
         return this.filteredClients.filter(c => {
            const inicial = c.name.charAt(0).toUpperCase()
            return letras.includes(inicial)
         })
      },

      contarClientesEnGrupo(letras) {
         return this.clientesEnGrupo(letras).length
      },

      scrollToGroup(grupoId) {
         this.grupoActivo = grupoId
         const element = document.getElementById('grupo-' + grupoId)
         if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' })
         }
      },

      logout() {
         localStorage.removeItem('seller')
         localStorage.removeItem('token')
         this.$router.push('/login')
      },
      mostrarAplazar(ruta) {
         alert("Funcionalidad de aplazar (TODO)")
      },
      verDetalleVisita(ruta) {
         alert("Detalle visita (TODO)")
      }
   }
}
</script>

<style scoped>
.animate-fade-in-up {
   animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
   from {
      opacity: 0;
      transform: translateY(20px);
   }

   to {
      opacity: 1;
      transform: translateY(0);
   }
}

/* Hide scrollbar for Chrome, Safari and Opera */
.no-scrollbar::-webkit-scrollbar {
   display: none;
}

/* Hide scrollbar for IE, Edge and Firefox */
.no-scrollbar {
   -ms-overflow-style: none;
   /* IE and Edge */
   scrollbar-width: none;
   /* Firefox */
}
</style>
