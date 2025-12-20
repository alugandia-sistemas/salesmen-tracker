<template>
  <div class="min-h-screen bg-white pb-20">
    <!-- Header -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-30">
      <div class="px-4 py-4">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">¡Hola, {{ sellerName }}!</h1>
            <h2 class="text-green-700 mt-1">{{ currentSectionTitle }}</h2>
          </div>
          <button @click="logout" class="text-gray-600 hover:text-gray-900 text-sm">
            Salir
          </button>
        </div>
        <p class="text-gray-500 text-sm mt-1">{{ todayDate }}</p>
      </div>
    </nav>

    <!-- Content Area -->
    <div class="px-4 py-6">
      <!-- ROUTE SECTION -->
      <div v-if="activeSection === 'route'">
        <h2 class="text-lg font-bold text-gray-900 mb-4">RUTA DE HOY</h2>

        <!-- Loading -->
        <div v-if="loadingRoutes" class="text-center py-10">
          <p class="text-gray-500">Cargando rutas...</p>
        </div>

        <!-- Today's Routes -->
        <div v-else-if="routesToday.length > 0" class="space-y-4">
          <div v-for="route in routesToday" :key="route.id" class="bg-white border-2 border-gray-200 rounded-xl p-4">
            <!-- Time and Status -->
            <div class="flex items-center justify-between mb-3">
              <span class="text-lg font-bold text-gray-900">{{ formatTime(route.planned_date) }}</span>
              <span :class="[
                'px-3 py-1 rounded-full text-xs font-semibold uppercase',
                route.status === 'completed' ? 'bg-green-100 text-green-800' : 
                route.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                route.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                'bg-orange-100 text-orange-800'
              ]">
                {{ route.status === 'completed' ? 'COMPLETADA' : 
                   route.status === 'in_progress' ? 'EN PROGRESO' :
                   route.status === 'cancelled' ? 'CANCELADA' :
                   'PENDIENTE' }}
              </span>
            </div>

            <!-- Client Info -->
            <div class="flex items-start gap-3 mb-3">
              <div class="w-10 h-10 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold">{{ getClientName(route.client_id).charAt(0) }}</span>
              </div>
              <div class="flex-1">
                <h3 class="font-bold text-gray-900">{{ getClientName(route.client_id) }}</h3>
                <p class="text-sm text-gray-600">📍 {{ getClientAddress(route.client_id) }}</p>
              </div>
            </div>

            <!-- Visit Type Badge -->
            <div class="mb-3">
              <span class="inline-block px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded">
                {{ route.visit_type || 'DELIVERY' }}
              </span>
            </div>

            <!-- Outcome (if completed) -->
            <div v-if="route.status === 'completed' && route.outcome" class="mb-3">
              <p class="text-sm text-gray-600">Resultado: <span class="font-semibold">{{ route.outcome }}</span></p>
            </div>

            <!-- Action Button -->
            <button v-if="route.status === 'pending' || route.status === 'in_progress'" @click="iniciarCheckin(route)"
              class="w-full bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition">
              📍 Iniciar Check-in
            </button>
            <button v-else-if="route.status === 'completed'"
              class="w-full bg-green-600 text-white py-3 rounded-lg font-semibold cursor-not-allowed opacity-75">
              ✅ Completada
            </button>
            <button v-else-if="route.status === 'cancelled'"
              class="w-full bg-red-600 text-white py-3 rounded-lg font-semibold cursor-not-allowed opacity-75">
              ❌ Cancelada
            </button>
          </div>
        </div>

        <!-- No routes -->
        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-500">No hay rutas programadas para hoy</p>
        </div>

        <!-- Add Unplanned Visit Button -->
        <button @click="showAddVisitModal = true"
          class="w-full mt-4 bg-white border-2 border-gray-300 text-gray-900 py-3 rounded-lg font-semibold hover:bg-gray-50 transition flex items-center justify-center gap-2">
          <span class="text-xl">+</span> Agregar Visita No Planificada
        </button>
      </div>

      <!-- SCHEDULE SECTION -->
      <div v-if="activeSection === 'schedule'">
        <h2 class="text-lg font-bold text-gray-900 mb-4">📊 RESUMEN DE LA SEMANA</h2>

        <div v-if="loadingStats" class="text-center py-10">
          <p class="text-gray-500">Cargando estadísticas...</p>
        </div>

        <div v-else class="space-y-4">
          <!-- Total Visits -->
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-xl p-6">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-semibold text-blue-900">Total de Visitas</h4>
              <span class="text-2xl">📍</span>
            </div>
            <p class="text-4xl font-bold text-blue-900 mb-1">{{ stats.total_visits }}</p>
            <p class="text-xs text-blue-700">Todas las visitas programadas</p>
          </div>

          <!-- Completed Visits -->
          <div class="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 rounded-xl p-6">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-semibold text-green-900">Visitas Completadas</h4>
              <span class="text-2xl">✅</span>
            </div>
            <p class="text-4xl font-bold text-green-900 mb-1">{{ stats.completed_visits }}</p>
            <div class="flex items-center gap-2">
              <div class="flex-1 bg-green-200 rounded-full h-2">
                <div class="bg-green-600 h-2 rounded-full" :style="{ width: stats.visits_completion_percentage + '%' }">
                </div>
              </div>
              <span class="text-xs font-bold text-green-700">{{ stats.visits_completion_percentage }}%</span>
            </div>
          </div>

          <!-- Total Routes -->
          <div class="bg-gradient-to-br from-purple-50 to-purple-100 border-2 border-purple-200 rounded-xl p-6">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-semibold text-purple-900">Total de Rutas</h4>
              <span class="text-2xl">🗺️</span>
            </div>
            <p class="text-4xl font-bold text-purple-900 mb-1">{{ stats.total_routes }}</p>
            <p class="text-xs text-purple-700">Rutas creadas</p>
          </div>
        </div>
      </div>

      <!-- CALENDAR SECTION (Weekly Events) -->
      <div v-if="activeSection === 'calendar'">
        <div class="mb-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4">📅 VISITAS DE LA SEMANA</h2>
          
          <!-- Week Navigation -->
          <div class="flex items-center justify-between mb-6 gap-2">
            <button @click="previousWeek"
              class="px-3 py-2 rounded-lg font-semibold text-sm bg-gray-100 text-gray-900 hover:bg-gray-200 transition">
              ← Anterior
            </button>
            <div class="text-center flex-1">
              <p class="font-semibold text-gray-900">{{ currentWeekDisplay }}</p>
            </div>
            <button @click="nextWeek"
              class="px-3 py-2 rounded-lg font-semibold text-sm bg-gray-100 text-gray-900 hover:bg-gray-200 transition">
              Siguiente →
            </button>
          </div>
        </div>

        <!-- Stats for the week -->
        <div class="space-y-3 mb-6">
          <!-- Total Visits this week -->
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-xl p-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-semibold text-blue-900">Visitas esta semana</p>
                <p class="text-2xl font-bold text-blue-900">{{ weekStats.total_visits }}</p>
              </div>
              <span class="text-3xl">📍</span>
            </div>
          </div>

          <!-- Completed this week -->
          <div class="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 rounded-xl p-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-semibold text-green-900">Completadas</p>
                <p class="text-2xl font-bold text-green-900">{{ weekStats.completed_visits }}</p>
              </div>
              <span class="text-3xl">✅</span>
            </div>
          </div>

          <!-- Pending this week -->
          <div class="bg-gradient-to-br from-orange-50 to-orange-100 border-2 border-orange-200 rounded-xl p-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-semibold text-orange-900">Pendientes</p>
                <p class="text-2xl font-bold text-orange-900">{{ weekStats.pending_visits }}</p>
              </div>
              <span class="text-3xl">⏳</span>
            </div>
          </div>
        </div>

        <!-- Events grouped by day -->
        <h3 class="text-md font-bold text-gray-900 mb-4">Eventos de la semana</h3>
        
        <div v-if="loadingWeekEvents" class="text-center py-10">
          <p class="text-gray-500">Cargando eventos...</p>
        </div>

        <div v-else-if="Object.keys(weekEvents).length > 0" class="space-y-4">
          <div v-for="(dayEvents, dateStr) in weekEvents" :key="dateStr" class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
            
            <!-- Day Header (Accordion Toggle) -->
            <button @click="expandedDates[dateStr] = !expandedDates[dateStr]" 
              class="w-full bg-gray-100 px-4 py-3 border-b border-gray-200 flex items-center justify-between hover:bg-gray-200 transition">
              <div class="flex items-center gap-3 flex-1 text-left">
                <span class="text-xl transition-transform" :style="{ transform: expandedDates[dateStr] ? 'rotate(90deg)' : 'rotate(0)' }">▶️</span>
                <h3 class="text-lg font-bold text-gray-900">
                  📅 {{ formatDateHeader(dateStr) }}
                </h3>
              </div>
              <span class="text-sm font-bold text-gray-600">
                {{ dayEvents.length }} {{ dayEvents.length === 1 ? 'visita' : 'visitas' }}
              </span>
            </button>

            <!-- Events List (Collapsible) -->
            <div v-show="expandedDates[dateStr]" class="divide-y divide-gray-100">
              <div v-for="route in dayEvents" :key="route.id" class="p-3">
                <div class="bg-gray-50 border border-gray-200 rounded-lg p-3 hover:border-gray-900 transition">
                  <div class="flex items-start justify-between mb-2">
                    <div>
                      <p class="font-bold text-gray-900">{{ formatTime(route.planned_date) }}</p>
                      <p class="text-sm text-gray-600">{{ getClientName(route.client_id) }}</p>
                    </div>
                    <span :class="[
                      'px-2 py-1 rounded text-xs font-semibold whitespace-nowrap',
                      route.status === 'completed' ? 'bg-green-100 text-green-800' :
                      route.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                      route.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                      'bg-orange-100 text-orange-800'
                    ]">
                      {{ route.status === 'completed' ? 'COMPLETADA' : 
                         route.status === 'in_progress' ? 'EN PROGRESO' :
                         route.status === 'cancelled' ? 'CANCELADA' : 'PENDIENTE' }}
                    </span>
                  </div>

                  <!-- Notes Section (if exists) -->
                  <div v-if="route.notes" class="mt-2 pt-2 border-t border-gray-200">
                    <p class="text-xs font-semibold text-gray-600 mb-1">📝 Notas:</p>
                    <p class="text-sm text-gray-700">{{ route.notes }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- No events -->
        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-500">No hay visitas programadas para esta semana</p>
        </div>
      </div>

      <!-- CLIENTS SECTION -->
      <div v-if="activeSection === 'clients'">
        <h2 class="text-lg font-bold text-gray-900 mb-4">👥 CLIENTES</h2>

        <!-- Search Bar -->
        <div class="mb-4">
          <div class="relative">
            <input v-model="searchQuery" type="text" placeholder="Buscar clientes..." @input="handleSearch"
              class="w-full px-4 py-3 pl-10 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900" />
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <button v-if="searchQuery" type="button" @click="searchQuery = ''; handleSearch();" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" aria-label="Limpiar búsqueda">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <p class="text-gray-500 text-xs mt-2">{{ clientsMetadata.total }} clientes encontrados</p>
        </div>

        <!-- Loading -->
        <div v-if="loadingClients" class="text-center py-10">
          <p class="text-gray-500">Cargando clientes...</p>
        </div>

        <!-- Client List -->
        <div v-else-if="clients.length > 0" class="space-y-3">
          <div v-for="client in clients" :key="client.id" @click="selectClient(client)"
            class="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-gray-900 cursor-pointer transition">
            <div class="flex items-start gap-3">
              <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold text-lg">{{ client.name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="flex-1">
                <h3 class="font-bold text-gray-900">{{ client.name }}</h3>
                <p class="text-sm text-gray-600">📍 {{ client.address }}</p>
                <p class="text-sm text-gray-600 mt-1">📞 {{ client.phone }}</p>
              </div>
              <span class="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full">
                {{ client.client_type }}
              </span>
            </div>
          </div>
        </div>

        <!-- No results -->
        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-500">No se encontraron clientes</p>
        </div>

        <!-- Pagination -->
        <div v-if="clients.length > 0" class="flex items-center justify-between mt-6">
          <button @click="previousPage" :disabled="!clientsMetadata.has_prev"
            class="px-4 py-2 rounded-lg font-semibold text-sm bg-gray-900 text-white disabled:bg-gray-400 transition">
            ← Anterior
          </button>
          <div class="text-center text-sm">
            <p class="font-semibold text-gray-900">Página {{ clientsMetadata.page }} de {{ clientsMetadata.total_pages}}</p>
            <p class="text-gray-600 text-xs mt-1">Mostrando {{ clients.length }} de {{ clientsMetadata.total }}</p>
          </div>
          <button @click="nextPage" :disabled="!clientsMetadata.has_next"
            class="px-4 py-2 rounded-lg font-semibold text-sm bg-gray-900 text-white disabled:bg-gray-400 transition">
            Siguiente →
          </button>
        </div>
      </div>
    </div>

    <!-- Bottom Navigation -->
    <div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-40">
      <div class="flex items-center justify-around py-3">
        <button @click="activeSection = 'route'" :class="['flex flex-col items-center gap-1 px-4 py-2 transition',
          activeSection === 'route' ? 'text-gray-900' : 'text-gray-400']">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span class="text-xs font-semibold">Ruta</span>
        </button>

        <button @click="activeSection = 'schedule'" :class="['flex flex-col items-center gap-1 px-4 py-2 transition',
          activeSection === 'schedule' ? 'text-gray-900' : 'text-gray-400']">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span class="text-xs font-semibold">Resumen</span>
        </button>

        <button @click="activeSection = 'calendar'" :class="['flex flex-col items-center gap-1 px-4 py-2 transition',
          activeSection === 'calendar' ? 'text-gray-900' : 'text-gray-400']">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
          <span class="text-xs font-semibold">Semana</span>
        </button>

        <button @click="activeSection = 'clients'" :class="['flex flex-col items-center gap-1 px-4 py-2 transition',
          activeSection === 'clients' ? 'text-gray-900' : 'text-gray-400']">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <span class="text-xs font-semibold">Clientes</span>
        </button>
      </div>
    </div>

    <!-- Visit Definition Modal -->
    <div v-if="showVisitModal" class="fixed inset-0 bg-black/40 flex items-end z-50" @click.self="closeVisitModal">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[85vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-gray-900">Definir Visita</h3>
          <button @click="closeVisitModal" class="text-gray-500 hover:text-gray-900 text-2xl">×</button>
        </div>

        <!-- Client Info -->
        <div v-if="selectedClient" class="bg-gray-50 rounded-xl p-4 mb-6">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center">
              <span class="text-white font-bold text-lg">{{ selectedClient.name.charAt(0) }}</span>
            </div>
            <div>
              <h4 class="font-bold text-gray-900">{{ selectedClient.name }}</h4>
              <p class="text-sm text-gray-600">{{ selectedClient.address }}</p>
            </div>
          </div>
        </div>

        <!-- Visit Form -->
        <div class="space-y-4">
          <!-- Date Picker -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Fecha de Visita</label>
            <input v-model="visitForm.date" type="date"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900">
          </div>

          <!-- Time Picker -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Hora de Visita</label>
            <input v-model="visitForm.time" type="time"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900">
          </div>

          <!-- Visit Type -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Tipo de Visita</label>
            <select v-model="visitForm.visitType"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900">
              <option value="DELIVERY">Entrega</option>
              <option value="PROSPECT_INTRO">Presentación de Prospecto</option>
              <option value="FOLLOW_UP">Seguimiento</option>
              <option value="MAINTENANCE">Mantenimiento</option>
              <option value="OTHER">Otro</option>
            </select>
          </div>

          <!-- Notes (Optional) -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">Notas (Opcional)</label>
            <textarea v-model="visitForm.notes" rows="3" placeholder="Agrega notas sobre esta visita..."
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"></textarea>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3 mt-6">
          <button @click="closeVisitModal"
            class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold hover:bg-gray-200 transition">
            Cancelar
          </button>
          <button @click="createVisit" :disabled="!visitForm.date || !visitForm.time"
            class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold hover:bg-gray-800 transition disabled:bg-gray-400">
            {{ creatingVisit ? 'Creando...' : 'Crear Visita' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add Unplanned Visit Modal -->
    <div v-if="showAddVisitModal" class="fixed inset-0 bg-black/40 flex items-end z-50"
      @click.self="showAddVisitModal = false">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[85vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-gray-900">Agregar Visita No Planificada</h3>
          <button @click="showAddVisitModal = false" class="text-gray-500 hover:text-gray-900 text-2xl">×</button>
        </div>

        <!-- Search Client -->
        <div class="mb-4">
          <label class="block text-sm font-semibold text-gray-900 mb-2">Buscar Cliente</label>
          <div class="relative">
            <input v-model="unplannedSearchQuery" type="text" placeholder="Escribe el nombre del cliente..."
              @input="searchClientsForUnplanned"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 pl-3" />
            <button v-if="unplannedSearchQuery" type="button" @click="unplannedSearchQuery=''; unplannedSearchResults=[];" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" aria-label="Limpiar búsqueda no planificada">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
        </div>

        <!-- Client Results -->
        <div v-if="unplannedSearchResults.length > 0" class="mb-4 max-h-60 overflow-y-auto space-y-2">
          <div v-for="client in unplannedSearchResults" :key="client.id" @click="selectClientForUnplanned(client)"
            class="bg-gray-50 border border-gray-200 rounded-lg p-3 hover:bg-gray-100 cursor-pointer">
            <p class="font-semibold text-gray-900">{{ client.name }}</p>
            <p class="text-sm text-gray-600">{{ client.address }}</p>
          </div>
        </div>

        <p v-if="unplannedSearchQuery && unplannedSearchResults.length === 0" class="text-gray-500 text-sm mb-4">
          No se encontraron clientes
        </p>
      </div>
    </div>

    <!-- Check-in Modal (reused from existing implementation) -->
    <div v-if="showCheckinModal" class="fixed inset-0 bg-black/40 flex items-end z-50">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-2xl font-bold text-gray-900 mb-6">
          Check-in: {{ getClientName(currentRoute.client_id) }}
        </h3>

        <div class="bg-gray-100 rounded-lg p-4 mb-6 text-center">
          <p class="text-gray-600 text-sm mb-4">📍 Esperando ubicación...</p>
          <div v-if="currentLocation" class="text-left space-y-2">
            <p class="text-gray-900 font-semibold">Ubicación detectada:</p>
            <p class="text-gray-700 text-sm">Latitud: {{ currentLocation.latitude.toFixed(5) }}</p>
            <p class="text-gray-700 text-sm">Longitud: {{ currentLocation.longitude.toFixed(5) }}</p>
            <p class="text-gray-700 text-sm">Precisión: ±{{ currentLocation.accuracy.toFixed(0) }}m</p>
          </div>
        </div>

        <div class="mb-6">
          <label class="flex items-center gap-4 p-4 border-2 border-gray-300 rounded-lg cursor-pointer hover:border-gray-900">
            <input v-model="clientFound" type="checkbox" class="w-6 h-6 accent-gray-900" />
            <span class="text-gray-900 font-semibold">✓ Cliente confirmado en la ubicación</span>
          </label>
        </div>

        <div class="mb-6">
          <label class="block text-sm font-semibold text-gray-900 mb-2">Notas (opcional)</label>
          <textarea v-model="checkinNotes" placeholder="Ej: Cliente no estaba disponible..."
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 text-sm"
            rows="3"></textarea>
        </div>

        <div class="flex gap-3">
          <button @click="closeCheckinModal"
            class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold text-lg hover:bg-gray-200 transition">
            Cancel
          </button>
          <button @click="performCheckin" :disabled="!currentLocation"
            class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg hover:bg-gray-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed">
            {{ performingCheckin ? '⏳ Guardando...' : '📍 Confirmar Check-in' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SellerDashboard',
  data() {
    return {
      activeSection: 'route', // 'route', 'schedule', 'clients'
      seller: null,
      sellerName: 'Vendedor',

      // Route section
      routesToday: [],
      loadingRoutes: false,
      allClients: [],

      // Schedule section
      stats: {
        total_routes: 0,
        completed_routes: 0,
        routes_completion_percentage: 0,
        total_visits: 0,
        completed_visits: 0,
        visits_completion_percentage: 0
      },
      loadingStats: false,
      expandedDates: {}, // Track expanded dates for accordion

      // Clients section
      clients: [],
      loadingClients: false,
      searchQuery: '',
      searchTimeout: null,
      clientsMetadata: {
        page: 1,
        limit: 25,
        total: 0,
        total_pages: 0,
        has_next: false,
        has_prev: false
      },

      // Visit modal
      showVisitModal: false,
      selectedClient: null,
      visitForm: {
        date: '',
        time: '',
        visitType: 'DELIVERY',
        notes: ''
      },
      creatingVisit: false,

      // Add unplanned visit
      showAddVisitModal: false,
      unplannedSearchQuery: '',
      unplannedSearchResults: [],

      // Check-in
      showCheckinModal: false,
      currentRoute: null,
      currentLocation: null,
      clientFound: false,
      checkinNotes: '',
      performingCheckin: false,
      geoWatcher: null,

      // Calendar section
      weekOffset: 0, // 0 = current week, -1 = previous, 1 = next
      weekEvents: {}, // { dateStr: [routes] }
      loadingWeekEvents: false,
      weekStats: {
        total_visits: 0,
        completed_visits: 0,
        pending_visits: 0
      }
    }
  },
  computed: {
    currentWeekDisplay() {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const weekStart = new Date(today)
      const dayOfWeek = today.getDay()
      const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1)
      weekStart.setDate(diff)
      weekStart.setDate(weekStart.getDate() + (this.weekOffset * 7))
      
      const weekEnd = new Date(weekStart.getTime() + 6 * 24 * 60 * 60 * 1000)
      
      // Calculate ISO week number
      const date = new Date(weekStart)
      date.setDate(date.getDate() + 4)
      const yearStart = new Date(date.getFullYear(), 0, 1)
      const weekNum = Math.ceil((((date - yearStart) / 86400000) + 1) / 7)
      const year = weekStart.getFullYear()
      
      const options = { month: 'short', day: 'numeric' }
      const startStr = weekStart.toLocaleDateString('es-ES', options)
      const endStr = weekEnd.toLocaleDateString('es-ES', options)
      
      return `Semana ${weekNum} (${year}) - ${startStr} - ${endStr}`
    },
    currentSectionTitle() {
      if (this.activeSection === 'route') {
        return 'Ruta de hoy'
      }
      const titles = {
        schedule: 'Agenda',
        calendar: 'Semana',
        clients: 'Clientes'
      }
      return titles[this.activeSection] || 'Dashboard'
    },
    todayDate() {
      if (this.activeSection === 'route') {
        const now = new Date()
        const time = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', hour12: false })
        const days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        const day = days[now.getDay()]
        const date = now.getDate()
        const month = months[now.getMonth()]
        return `${time} · ${day}, ${date} ${month}`
      }
      const days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
      const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
      const now = new Date()
      return `${days[now.getDay()]}, ${now.getDate()} de ${months[now.getMonth()]}`
    }
  },
  async mounted() {
    const sellerData = localStorage.getItem('seller')
    if (sellerData) {
      this.seller = JSON.parse(sellerData)
      this.sellerName = this.seller.name || 'Vendedor'
      
      // 🔑 CRÍTICO: Cargar clientes PRIMERO
      await this.fetchAllClients()
      
      this.fetchTodayRoutes()
      this.fetchStats()
      this.fetchWeekEvents()
      this.fetchClients()
    } else {
      this.$router.push('/login')
    }
  },
  beforeUnmount() {
    if (this.geoWatcher) {
      navigator.geolocation.clearWatch(this.geoWatcher)
    }
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout)
    }
  },
  methods: {
    // Utility
    getOrdinalSuffix(day) {
      if (day > 3 && day < 21) return 'th'
      switch (day % 10) {
        case 1: return 'st'
        case 2: return 'nd'
        case 3: return 'rd'
        default: return 'th'
      }
    },
    formatTime(datetime) {
      const date = new Date(datetime)
      return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
    },
    getClientName(clientId) {
      const client = this.allClients.find(c => c.id === clientId)
      return client ? client.name : 'Desconocido'
    },
    getClientAddress(clientId) {
      const client = this.allClients.find(c => c.id === clientId)
      return client ? client.address : 'Sin dirección'
    },

    // API calls
    async fetchTodayRoutes() {
      try {
        this.loadingRoutes = true
        const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/?seller_id=${this.seller.id}`)
        const allRoutes = await response.json()

        const today = new Date().toISOString().split('T')[0]
        this.routesToday = allRoutes.filter(r => r.planned_date.split('T')[0] === today)
        this.routesToday.sort((a, b) => new Date(a.planned_date) - new Date(b.planned_date))
      } catch (e) {
        console.error('Error fetching routes:', e)
      } finally {
        this.loadingRoutes = false
      }
    },

    async fetchStats() {
      try {
        this.loadingStats = true
        const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/stats/?seller_id=${this.seller.id}`)
        this.stats = await response.json()
      } catch (e) {
        console.error('Error fetching stats:', e)
      } finally {
        this.loadingStats = false
      }
    },

    async fetchWeekEvents() {
      try {
        this.loadingWeekEvents = true
        
        // Calcular los días de la semana actual
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        const weekStart = new Date(today)
        const dayOfWeek = today.getDay()
        const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1)
        weekStart.setDate(diff)
        weekStart.setDate(weekStart.getDate() + (this.weekOffset * 7))
        
        const weekEnd = new Date(weekStart.getTime() + 7 * 24 * 60 * 60 * 1000)

        // Obtener todas las rutas
        const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/?seller_id=${this.seller.id}`)
        const allRoutes = await response.json()

        // Filtrar por semana
        const grouped = {}
        let totalVisits = 0
        let completedVisits = 0
        let pendingVisits = 0

        allRoutes.forEach(route => {
          const routeDate = new Date(route.planned_date)
          const dateStr = routeDate.toISOString().split('T')[0]
          const routeDateObj = new Date(dateStr)
          routeDateObj.setHours(0, 0, 0, 0)

          if (routeDateObj >= weekStart && routeDateObj < weekEnd) {
            if (!grouped[dateStr]) {
              grouped[dateStr] = []
            }
            grouped[dateStr].push(route)
            
            totalVisits++
            if (route.status === 'completed') {
              completedVisits++
            } else if (route.status === 'pending' || route.status === 'in_progress') {
              pendingVisits++
            }
          }
        })

        // Ordenar fechas
        const sortedGrouped = {}
        Object.keys(grouped).sort((a, b) => new Date(a) - new Date(b)).forEach(date => {
          sortedGrouped[date] = grouped[date]
        })

        this.weekEvents = sortedGrouped
        this.weekStats = {
          total_visits: totalVisits,
          completed_visits: completedVisits,
          pending_visits: pendingVisits
        }
      } catch (e) {
        console.error('Error fetching week events:', e)
      } finally {
        this.loadingWeekEvents = false
      }
    },

    formatDateHeader(dateStr) {
      const date = new Date(dateStr + 'T00:00:00')
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      
      const dateOnly = new Date(date)
      dateOnly.setHours(0, 0, 0, 0)

      if (dateOnly.getTime() === today.getTime()) {
        return 'Hoy'
      } else if (dateOnly.getTime() === tomorrow.getTime()) {
        return 'Mañana'
      } else {
        return new Date(dateStr + 'T00:00:00').toLocaleDateString('es-ES', { weekday: 'long', month: 'short', day: 'numeric' })
      }
    },

    previousWeek() {
      this.weekOffset--
      this.fetchWeekEvents()
    },

    nextWeek() {
      this.weekOffset++
      this.fetchWeekEvents()
    },

    async fetchClients(page = 1) {
      try {
        this.loadingClients = true
        const params = new URLSearchParams({
          page: page,
          limit: this.clientsMetadata.limit,
          ...(this.searchQuery && { search: this.searchQuery })
        })

        const response = await fetch(`${import.meta.env.VITE_API_URL}/clients/?${params.toString()}`)
        const data = await response.json()

        this.clients = data.data || []
        this.clientsMetadata = data.pagination || {}
      } catch (e) {
        console.error('Error fetching clients:', e)
        this.clients = []
      } finally {
        this.loadingClients = false
      }
    },

    async fetchAllClients() {
      try {
        // Usar endpoint optimizado
        const response = await fetch(`${import.meta.env.VITE_API_URL}/clients/sync/`)
        
        if (response.ok) {
          const data = await response.json()
          this.allClients = data.clients || []
        } else {
          // Fallback
          const resp2 = await fetch(`${import.meta.env.VITE_API_URL}/clients/?limit=500`)
          const data2 = await resp2.json()
          this.allClients = Array.isArray(data2) ? data2 : (data2.data || [])
        }
        
        console.log(`✅ ${this.allClients.length} clientes cargados`)
      } catch (e) {
        console.error('Error:', e)
        this.allClients = []
      }
    },

    // Client search
    handleSearch() {
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      this.searchTimeout = setTimeout(() => {
        this.fetchClients(1)
      }, 500)
    },

    // Pagination
    nextPage() {
      if (this.clientsMetadata.has_next) {
        this.fetchClients(this.clientsMetadata.page + 1)
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    previousPage() {
      if (this.clientsMetadata.has_prev) {
        this.fetchClients(this.clientsMetadata.page - 1)
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },

    // Visit modal
    selectClient(client) {
      this.selectedClient = client
      this.showVisitModal = true
    },
    closeVisitModal() {
      this.showVisitModal = false
      this.selectedClient = null
      this.visitForm = {
        date: new Date().toISOString().split('T')[0],
        time: '',
        visitType: 'DELIVERY',
        notes: ''
      }
    },
    async createVisit() {
      if (!this.visitForm.date || !this.visitForm.time || !this.selectedClient) {
        return
      }

      try {
        this.creatingVisit = true

        // Combine date and time
        const plannedDate = `${this.visitForm.date}T${this.visitForm.time}:00`

        const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            seller_id: this.seller.id,
            client_id: this.selectedClient.id,
            planned_date: plannedDate,
            visit_type: this.visitForm.visitType,
            notes: this.visitForm.notes || null,
            status: 'pending'
          })
        })

        if (response.ok) {
          alert(`✅ Visita creada para ${this.selectedClient.name}`)
          this.closeVisitModal()
          this.fetchTodayRoutes()
          this.fetchStats()
        } else {
          const error = await response.json()
          alert(`Error: ${error.detail}`)
        }
      } catch (e) {
        console.error('Error al crear visita:', e)
        alert('Error al crear visita')
      } finally {
        this.creatingVisit = false
      }
    },

    // Visita no planificada
    searchClientsForUnplanned() {
      if (!this.unplannedSearchQuery) {
        this.unplannedSearchResults = []
        return
      }

      const query = this.unplannedSearchQuery.toLowerCase()
      this.unplannedSearchResults = this.allClients
        .filter(c => c.name.toLowerCase().includes(query))
        .slice(0, 10)
    },
    selectClientForUnplanned(client) {
      this.showAddVisitModal = false
      this.selectedClient = client
      this.showVisitModal = true
      this.unplannedSearchQuery = ''
      this.unplannedSearchResults = []
    },

    // Check-in
    initGPS() {
      if (!navigator.geolocation) {
        alert('Geolocalización no disponible en este navegador')
        return
      }

      console.log('🔍 Starting GPS initialization...')

      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log('✅ GPS location obtained:', position.coords)
          this.currentLocation = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          }
        },
        (error) => {
          console.error('❌ GPS error:', error.code, error.message)
          let message = 'Error de ubicación: '
          switch(error.code) {
            case 1:
              message += 'Permiso denegado'
              break
            case 2:
              message += 'Posición no disponible'
              break
            case 3:
              message += 'Tiempo agotado'
              break
            default:
              message += 'Error desconocido'
          }
          alert(message)
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      )

      this.geoWatcher = navigator.geolocation.watchPosition(
        (position) => {
          this.currentLocation = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          }
        },
        (error) => console.error('GPS watch error:', error.message),
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      )
    },

    iniciarCheckin(route) {
      this.currentRoute = route
      this.clientFound = false
      this.checkinNotes = ''
      this.showCheckinModal = true
      this.initGPS()
    },

    closeCheckinModal() {
      this.showCheckinModal = false
      this.currentRoute = null
      this.clientFound = false
      this.checkinNotes = ''
    },

    async performCheckin() {
      if (!this.currentLocation) {
        alert('Ubicación no disponible')
        return
      }

      try {
        this.performingCheckin = true
        console.log('📍 Iniciando check-in para ruta:', this.currentRoute.id)

        const response = await fetch(`${import.meta.env.VITE_API_URL}/visits/checkin/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            route_id: this.currentRoute.id,
            seller_id: this.currentRoute.seller_id,
            client_id: this.currentRoute.client_id,
            latitude: this.currentLocation.latitude,
            longitude: this.currentLocation.longitude,
            client_found: this.clientFound,
            notes: this.checkinNotes || null
          })
        })

        const result = await response.json()
        console.log('✅ Resultado del check-in:', result)
        console.log('📊 Validity status:', result.validity_status)

        // Determinar el estado basado en validity_status
        let newStatus = 'pending'
        let alertMessage = ''
        
        if (result.validity_status === 'valid_1') {
          newStatus = 'completed'
          alertMessage = '✅ Check-in válido dentro de horario comercial. Ruta completada.'
        } else if (result.validity_status === 'valid_2') {
          newStatus = 'completed'
          alertMessage = '✅ Check-in válido pero fuera de horario comercial. Ruta completada (con incidente).'
        } else if (result.validity_status === 'invalid') {
          newStatus = 'completed'  // Se marca como completada pero con incidente
          alertMessage = '❌ Check-in inválido. Ruta marcada como realizada con incidente:\n' + result.validation_error
        }

        // Actualizar estado de la ruta localmente
        this.currentRoute.status = newStatus
        
        // Encontrar y actualizar en routesToday
        const routeIndex = this.routesToday.findIndex(r => r.id === this.currentRoute.id)
        if (routeIndex !== -1) {
          this.routesToday[routeIndex].status = newStatus
          console.log('✅ Ruta actualizada localmente. Nuevo estado:', this.routesToday[routeIndex].status)
        }

        alert(alertMessage)
        
        this.closeCheckinModal()
        
        // Refrescar datos después de un breve delay
        setTimeout(() => {
          console.log('🔄 Refrescando datos...')
          this.fetchTodayRoutes()
          this.fetchStats()
          this.fetchWeekEvents()
        }, 500)
        
      } catch (e) {
        console.error('Error during check-in:', e)
        alert('Error durante el check-in')
      } finally {
        this.performingCheckin = false
      }
    },

    logout() {
      localStorage.removeItem('seller')
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>