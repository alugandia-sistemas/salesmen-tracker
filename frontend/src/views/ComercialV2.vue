<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="px-4 py-4">
        <div class="flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Alugandia</h1>
          <button @click="logout" class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-semibold">
            Salir
          </button>
        </div>
        <p class="text-gray-600 text-sm mt-2">{{ sellerName }}</p>
      </div>
    </nav>

    <!-- Tabs -->
    <div class="bg-white border-b border-gray-200 sticky top-16 z-40">
      <div class="px-4 flex gap-0 overflow-x-auto">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-4 py-3 font-semibold text-sm border-b-2 transition whitespace-nowrap',
            activeTab === tab.id 
              ? 'border-gray-900 text-gray-900' 
              : 'border-transparent text-gray-500'
          ]"
        >
          {{ tab.icon }} {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="px-4 py-6 pb-24">
      
      <!-- TAB: HOY -->
      <div v-if="activeTab === 'hoy'">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Rutas de Hoy</h2>
        
        <div v-if="routesHoy.length > 0" class="space-y-3">
          <div 
            v-for="ruta in routesHoy" 
            :key="ruta.id" 
            class="bg-gray-50 border-2 border-gray-200 rounded-xl p-4"
          >
            <!-- Cliente -->
            <div class="flex items-start gap-3 mb-3">
              <div class="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold">{{ ruta.client?.name?.charAt(0) || '?' }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="text-lg font-bold text-gray-900 truncate">{{ ruta.client?.name }}</h4>
                <p class="text-gray-600 text-sm truncate">📍 {{ ruta.client?.address }}</p>
                <p class="text-gray-500 text-sm">📞 {{ ruta.client?.phone }}</p>
              </div>
            </div>

            <!-- Status -->
            <div class="flex flex-wrap gap-2 mb-3">
              <span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-200 text-gray-900">
                {{ formatTime(ruta.planned_date) }}
              </span>
              <span 
                class="px-3 py-1 rounded-full text-xs font-semibold"
                :class="getStatusClass(ruta.status)"
              >
                {{ getStatusLabel(ruta.status) }}
              </span>
              <span 
                v-if="ruta.times_postponed > 0"
                class="px-3 py-1 rounded-full text-xs font-semibold bg-orange-100 text-orange-800"
              >
                🔄 Aplazada {{ ruta.times_postponed }}x
              </span>
            </div>

            <!-- Botones -->
            <div class="flex gap-2">
              <button 
                v-if="ruta.status === 'pending'"
                @click="iniciarCheckin(ruta)" 
                class="flex-1 bg-gray-900 text-white py-3 rounded-lg font-semibold text-sm"
              >
                📍 Check-in
              </button>
              <button 
                v-if="ruta.status === 'pending'"
                @click="mostrarAplazar(ruta)" 
                class="flex-1 bg-gray-100 text-gray-900 py-3 rounded-lg font-semibold text-sm border border-gray-300"
              >
                ⏰ Aplazar
              </button>
              <button 
                v-if="ruta.status === 'completed'"
                @click="verDetalleVisita(ruta)"
                class="flex-1 bg-gray-100 text-gray-900 py-3 rounded-lg font-semibold text-sm"
              >
                Ver detalles
              </button>
            </div>
          </div>
        </div>

        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-500 text-lg mb-2">📅</p>
          <p class="text-gray-600">Sin rutas programadas para hoy</p>
        </div>
      </div>

      <!-- TAB: HISTORIAL -->
      <div v-if="activeTab === 'historial'">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold text-gray-900">Historial</h2>
          <select 
            v-model="historialMeses" 
            @change="cargarHistorial"
            class="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option :value="1">Último mes</option>
            <option :value="3">3 meses</option>
            <option :value="6">6 meses</option>
          </select>
        </div>

        <!-- Filtro por resultado -->
        <div class="flex gap-2 mb-4 overflow-x-auto pb-2">
          <button 
            v-for="filtro in filtrosResultado" 
            :key="filtro.value"
            @click="filtroResultado = filtro.value"
            :class="[
              'px-3 py-2 rounded-full text-xs font-semibold whitespace-nowrap border transition',
              filtroResultado === filtro.value 
                ? 'bg-gray-900 text-white border-gray-900' 
                : 'bg-white text-gray-700 border-gray-300'
            ]"
          >
            {{ filtro.icon }} {{ filtro.label }}
          </button>
        </div>

        <!-- Lista historial -->
        <div v-if="historialRutas.length > 0" class="space-y-3">
          <div 
            v-for="ruta in historialFiltrado" 
            :key="ruta.id" 
            class="bg-white border border-gray-200 rounded-xl p-4"
          >
            <div class="flex justify-between items-start mb-2">
              <div>
                <h4 class="font-bold text-gray-900">{{ ruta.client?.name }}</h4>
                <p class="text-gray-500 text-sm">{{ formatDate(ruta.planned_date) }}</p>
              </div>
              <span 
                v-if="ruta.visit?.result"
                class="px-3 py-1 rounded-full text-xs font-semibold"
                :class="getResultClass(ruta.visit.result)"
              >
                {{ getResultIcon(ruta.visit.result) }} {{ getResultLabel(ruta.visit.result) }}
              </span>
            </div>
            
            <!-- Notas rápidas -->
            <p v-if="ruta.visit?.quick_notes" class="text-gray-700 text-sm bg-gray-50 p-2 rounded mb-2">
              "{{ ruta.visit.quick_notes }}"
            </p>
            
            <!-- Métricas -->
            <div class="flex gap-3 text-xs text-gray-500">
              <span v-if="ruta.visit?.checkin_distance_meters">
                📍 {{ Math.round(ruta.visit.checkin_distance_meters) }}m
              </span>
              <span :class="ruta.visit?.checkin_is_valid ? 'text-green-600' : 'text-red-600'">
                {{ ruta.visit?.checkin_is_valid ? '✓ Válido' : '✗ Inválido' }}
              </span>
            </div>
          </div>
        </div>

        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-600">Sin visitas en este período</p>
        </div>

        <!-- Paginación -->
        <div v-if="historialTotal > historialLimit" class="flex justify-center gap-2 mt-4">
          <button 
            @click="historialPage--" 
            :disabled="historialPage <= 1"
            class="px-4 py-2 bg-gray-100 rounded-lg disabled:opacity-50"
          >
            ← Anterior
          </button>
          <span class="px-4 py-2 text-gray-600">
            {{ historialPage }} / {{ Math.ceil(historialTotal / historialLimit) }}
          </span>
          <button 
            @click="historialPage++" 
            :disabled="historialPage >= Math.ceil(historialTotal / historialLimit)"
            class="px-4 py-2 bg-gray-100 rounded-lg disabled:opacity-50"
          >
            Siguiente →
          </button>
        </div>
      </div>

      <!-- TAB: CLIENTES -->
      <div v-if="activeTab === 'clientes'">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Mis Clientes</h2>
        
        <!-- Búsqueda -->
        <input 
          v-model="busquedaCliente"
          type="text"
          placeholder="🔍 Buscar cliente..."
          class="w-full px-4 py-3 border border-gray-300 rounded-lg mb-4 text-base"
        />

        <div v-if="clientesFiltrados.length > 0" class="space-y-3">
          <div 
            v-for="item in clientesFiltrados" 
            :key="item.client.id" 
            class="bg-white border border-gray-200 rounded-xl p-4"
            @click="verDetalleCliente(item)"
          >
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold text-sm">{{ item.client.name.charAt(0) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="font-bold text-gray-900 truncate">{{ item.client.name }}</h4>
                <p class="text-gray-600 text-sm truncate">{{ item.client.address }}</p>
                <div class="flex gap-3 mt-2 text-xs text-gray-500">
                  <span>📊 {{ item.stats.total_visits }} visitas</span>
                  <span class="text-green-600">🟢 {{ item.stats.ventas }} ventas</span>
                  <span>📈 {{ item.stats.conversion_rate }}%</span>
                </div>
              </div>
              <span class="text-gray-400">→</span>
            </div>
          </div>
        </div>

        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
          <p class="text-gray-600">No se encontraron clientes</p>
        </div>
      </div>

      <!-- TAB: RESUMEN -->
      <div v-if="activeTab === 'resumen'">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Mi Rendimiento</h2>
        
        <div class="grid grid-cols-2 gap-3 mb-6">
          <div class="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <p class="text-gray-600 text-xs font-semibold uppercase">Total Visitas</p>
            <p class="text-3xl font-bold text-gray-900">{{ resumen.visits?.total || 0 }}</p>
          </div>
          <div class="bg-green-50 rounded-xl p-4 border border-green-200">
            <p class="text-green-700 text-xs font-semibold uppercase">Ventas</p>
            <p class="text-3xl font-bold text-green-900">{{ resumen.visits?.ventas || 0 }}</p>
          </div>
          <div class="bg-yellow-50 rounded-xl p-4 border border-yellow-200">
            <p class="text-yellow-700 text-xs font-semibold uppercase">Interesados</p>
            <p class="text-3xl font-bold text-yellow-900">{{ resumen.visits?.interesados || 0 }}</p>
          </div>
          <div class="bg-blue-50 rounded-xl p-4 border border-blue-200">
            <p class="text-blue-700 text-xs font-semibold uppercase">Conversión</p>
            <p class="text-3xl font-bold text-blue-900">{{ resumen.metrics?.conversion_rate || '0%' }}</p>
          </div>
        </div>

        <!-- Desglose -->
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <h3 class="font-bold text-gray-900 mb-3">Desglose de Visitas</h3>
          <div class="space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-gray-600">🟢 Ventas</span>
              <span class="font-semibold">{{ resumen.visits?.ventas || 0 }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">🟡 Interesados</span>
              <span class="font-semibold">{{ resumen.visits?.interesados || 0 }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">🔵 Seguimiento</span>
              <span class="font-semibold">{{ resumen.visits?.seguimientos || 0 }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">🔴 No venta</span>
              <span class="font-semibold">{{ resumen.visits?.no_ventas || 0 }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">⚫ Ausentes</span>
              <span class="font-semibold">{{ resumen.visits?.ausentes || 0 }}</span>
            </div>
            <div class="flex justify-between items-center pt-2 border-t">
              <span class="text-gray-600">🔄 Rutas aplazadas</span>
              <span class="font-semibold">{{ resumen.metrics?.routes_postponed || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- MODAL CHECK-IN v2 -->
    <!-- ========================================== -->
    <div v-if="showCheckinModal" class="fixed inset-0 bg-black/50 flex items-end z-50">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[95vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-bold text-gray-900">
            Check-in: {{ rutaActual?.client?.name }}
          </h3>
          <button @click="cerrarCheckin" class="text-gray-500 text-2xl">&times;</button>
        </div>

        <!-- GPS -->
        <div class="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <span class="font-semibold text-gray-900">📍 Ubicación GPS</span>
            <span v-if="ubicacionActual" class="text-green-600 text-sm font-semibold">✓ Capturada</span>
          </div>
          <div v-if="ubicacionActual" class="text-sm text-gray-600">
            <p>Lat: {{ ubicacionActual.latitude.toFixed(5) }}</p>
            <p>Lng: {{ ubicacionActual.longitude.toFixed(5) }}</p>
            <p>Precisión: ±{{ ubicacionActual.accuracy.toFixed(0) }}m</p>
          </div>
          <p v-else class="text-gray-500 text-sm">Obteniendo ubicación...</p>
        </div>

        <!-- RESULTADO DE VISITA (OBLIGATORIO) -->
        <div class="mb-4">
          <label class="block text-sm font-bold text-gray-900 mb-2">
            Resultado de la visita <span class="text-red-500">*</span>
          </label>
          <div class="grid grid-cols-2 gap-2">
            <button 
              v-for="resultado in resultadosVisita"
              :key="resultado.value"
              @click="visitResult = resultado.value"
              :class="[
                'p-3 rounded-lg font-semibold text-sm border-2 transition',
                visitResult === resultado.value 
                  ? resultado.selectedClass 
                  : 'bg-white border-gray-200 text-gray-700'
              ]"
            >
              {{ resultado.icon }} {{ resultado.label }}
            </button>
          </div>
        </div>

        <!-- CLIENTE ENCONTRADO -->
        <div class="mb-4">
          <label class="flex items-center gap-3 p-3 border-2 border-gray-200 rounded-lg cursor-pointer"
            :class="clienteEncontrado ? 'border-gray-900 bg-gray-50' : ''"
          >
            <input 
              v-model="clienteEncontrado" 
              type="checkbox" 
              class="w-5 h-5 accent-gray-900"
            />
            <span class="text-gray-900 font-semibold">✓ Cliente confirmado en ubicación</span>
          </label>
        </div>

        <!-- NOTAS RÁPIDAS (OBLIGATORIO) -->
        <div class="mb-4">
          <label class="block text-sm font-bold text-gray-900 mb-2">
            Notas rápidas <span class="text-red-500">*</span>
            <span class="text-gray-500 font-normal">({{ quickNotes.length }}/100)</span>
          </label>
          <input 
            v-model="quickNotes"
            type="text"
            maxlength="100"
            placeholder="Ej: Pidió precio serie S-76 corredera"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg text-base focus:border-gray-900 focus:outline-none"
            :class="quickNotes.length < 5 && quickNotes.length > 0 ? 'border-red-300' : ''"
          />
          <p v-if="quickNotes.length > 0 && quickNotes.length < 5" class="text-red-500 text-xs mt-1">
            Mínimo 5 caracteres
          </p>
        </div>

        <!-- NOTAS DETALLADAS (OPCIONAL) -->
        <div class="mb-6">
          <label class="block text-sm font-bold text-gray-900 mb-2">
            Notas detalladas <span class="text-gray-500 font-normal">(opcional)</span>
          </label>
          <textarea 
            v-model="detailedNotes"
            rows="3"
            placeholder="Descripción más detallada de la visita..."
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg text-base focus:border-gray-900 focus:outline-none"
          ></textarea>
        </div>

        <!-- BOTONES -->
        <div class="flex gap-3">
          <button 
            @click="cerrarCheckin"
            class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold text-lg"
          >
            Cancelar
          </button>
          <button 
            @click="hacerCheckin"
            :disabled="!puedeHacerCheckin || cargandoCheckin"
            class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold text-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ cargandoCheckin ? '⏳ Guardando...' : '✓ Confirmar' }}
          </button>
        </div>

        <!-- Mensaje de validación -->
        <p v-if="!puedeHacerCheckin && ubicacionActual" class="text-orange-600 text-sm mt-3 text-center">
          Completa todos los campos obligatorios (*)
        </p>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- MODAL APLAZAR RUTA -->
    <!-- ========================================== -->
    <div v-if="showAplazarModal" class="fixed inset-0 bg-black/50 flex items-end z-50">
      <div class="w-full bg-white rounded-t-2xl p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-bold text-gray-900">Aplazar Visita</h3>
          <button @click="showAplazarModal = false" class="text-gray-500 text-2xl">&times;</button>
        </div>

        <p class="text-gray-600 mb-4">
          Cliente: <strong>{{ rutaActual?.client?.name }}</strong>
        </p>

        <!-- Razón -->
        <div class="mb-4">
          <label class="block text-sm font-bold text-gray-900 mb-2">Razón del aplazamiento</label>
          <div class="space-y-2">
            <label 
              v-for="razon in razonesAplazamiento" 
              :key="razon.value"
              class="flex items-start gap-3 p-3 border-2 rounded-lg cursor-pointer transition"
              :class="aplazarRazon === razon.value ? 'border-gray-900 bg-gray-50' : 'border-gray-200'"
            >
              <input 
                type="radio" 
                v-model="aplazarRazon" 
                :value="razon.value"
                class="w-4 h-4 mt-1 accent-gray-900"
              />
              <div>
                <span class="font-semibold text-gray-900">{{ razon.icon }} {{ razon.label }}</span>
                <p class="text-gray-500 text-xs">{{ razon.description }}</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Nueva fecha (si aplica) -->
        <div v-if="aplazarRazon === 'cliente_ocupado'" class="mb-4">
          <label class="block text-sm font-bold text-gray-900 mb-2">Nueva fecha</label>
          <input 
            type="date" 
            v-model="aplazarFecha"
            :min="fechaMinima"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg text-base"
          />
        </div>

        <!-- Notas -->
        <div class="mb-6">
          <label class="block text-sm font-bold text-gray-900 mb-2">Notas adicionales</label>
          <textarea 
            v-model="aplazarNotas"
            rows="2"
            placeholder="Información adicional..."
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg text-base"
          ></textarea>
        </div>

        <!-- Botones -->
        <div class="flex gap-3">
          <button 
            @click="showAplazarModal = false"
            class="flex-1 bg-gray-100 text-gray-900 py-4 rounded-lg font-semibold"
          >
            Cancelar
          </button>
          <button 
            @click="confirmarAplazamiento"
            :disabled="!aplazarRazon || cargandoAplazar"
            class="flex-1 bg-gray-900 text-white py-4 rounded-lg font-semibold disabled:bg-gray-400"
          >
            {{ cargandoAplazar ? '⏳...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- MODAL RESULTADO CHECK-IN -->
    <!-- ========================================== -->
    <div v-if="showResultado" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-6 max-w-sm w-full text-center">
        <div class="text-5xl mb-4">{{ resultadoCheckin.is_valid ? '✅' : '⚠️' }}</div>
        <h3 class="text-xl font-bold text-gray-900 mb-2">
          {{ resultadoCheckin.is_valid ? 'Check-in Válido' : 'Check-in con Advertencias' }}
        </h3>
        <p class="text-gray-600 mb-4">{{ resultadoCheckin.message }}</p>
        
        <div class="bg-gray-50 rounded-lg p-3 mb-4">
          <p class="text-gray-600 text-sm">Distancia al cliente</p>
          <p class="text-2xl font-bold text-gray-900">{{ resultadoCheckin.distance_meters?.toFixed(0) }}m</p>
        </div>

        <!-- Acciones automáticas -->
        <div v-if="resultadoCheckin.auto_actions?.length > 0" class="bg-blue-50 rounded-lg p-3 mb-4 text-left">
          <p class="text-blue-800 font-semibold text-sm mb-2">📋 Acciones generadas:</p>
          <ul class="text-blue-700 text-sm space-y-1">
            <li v-for="action in resultadoCheckin.auto_actions" :key="action.type">
              {{ action.description }}
            </li>
          </ul>
        </div>

        <button 
          @click="cerrarResultado"
          class="w-full bg-gray-900 text-white py-3 rounded-lg font-semibold"
        >
          Continuar
        </button>
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
      
      // Tabs
      activeTab: 'hoy',
      tabs: [
        { id: 'hoy', label: 'Hoy', icon: '📅' },
        { id: 'historial', label: 'Historial', icon: '📋' },
        { id: 'clientes', label: 'Clientes', icon: '👥' },
        { id: 'resumen', label: 'Resumen', icon: '📊' }
      ],
      
      // Rutas hoy
      routesHoy: [],
      
      // Historial
      historialRutas: [],
      historialMeses: 3,
      historialPage: 1,
      historialLimit: 20,
      historialTotal: 0,
      filtroResultado: 'todos',
      filtrosResultado: [
        { value: 'todos', label: 'Todos', icon: '📋' },
        { value: 'venta', label: 'Ventas', icon: '🟢' },
        { value: 'interesado', label: 'Interesados', icon: '🟡' },
        { value: 'seguimiento', label: 'Seguimiento', icon: '🔵' },
        { value: 'no_venta', label: 'No venta', icon: '🔴' },
        { value: 'ausente', label: 'Ausentes', icon: '⚫' }
      ],
      
      // Clientes
      clientes: [],
      busquedaCliente: '',
      
      // Resumen
      resumen: {},
      
      // Check-in modal
      showCheckinModal: false,
      rutaActual: null,
      ubicacionActual: null,
      geoWatcher: null,
      visitResult: null,
      clienteEncontrado: false,
      quickNotes: '',
      detailedNotes: '',
      cargandoCheckin: false,
      
      // Resultados de visita
      resultadosVisita: [
        { value: 'venta', label: 'Venta', icon: '🟢', selectedClass: 'bg-green-100 border-green-500 text-green-800' },
        { value: 'no_venta', label: 'No venta', icon: '🔴', selectedClass: 'bg-red-100 border-red-500 text-red-800' },
        { value: 'interesado', label: 'Interesado', icon: '🟡', selectedClass: 'bg-yellow-100 border-yellow-500 text-yellow-800' },
        { value: 'seguimiento', label: 'Seguimiento', icon: '🔵', selectedClass: 'bg-blue-100 border-blue-500 text-blue-800' },
        { value: 'ausente', label: 'Ausente', icon: '⚫', selectedClass: 'bg-gray-200 border-gray-500 text-gray-800' }
      ],
      
      // Resultado modal
      showResultado: false,
      resultadoCheckin: null,
      
      // Aplazar modal
      showAplazarModal: false,
      aplazarRazon: null,
      aplazarFecha: '',
      aplazarNotas: '',
      cargandoAplazar: false,
      razonesAplazamiento: [
        { value: 'cliente_ausente', label: 'Cliente cerrado', icon: '🚪', description: 'Se reprograma +1 día hábil' },
        { value: 'cliente_ocupado', label: 'Cliente ocupado', icon: '👤', description: 'Tú eliges nueva fecha' },
        { value: 'emergencia_personal', label: 'Emergencia personal', icon: '🆘', description: 'Admin reprogramará' },
        { value: 'prioridad_otro_cliente', label: 'Otra prioridad', icon: '⚡', description: 'Se reprograma +2 días' },
        { value: 'condiciones_meteorologicas', label: 'Mal tiempo', icon: '🌧️', description: 'Se reprograma +1 día' },
        { value: 'problema_vehiculo', label: 'Problema vehículo', icon: '🚗', description: 'Admin reprogramará' },
        { value: 'cliente_inactivo', label: 'Cliente cerró/inactivo', icon: '❌', description: 'Se marca inactivo' }
      ]
    }
  },
  computed: {
    puedeHacerCheckin() {
      return (
        this.ubicacionActual &&
        this.visitResult &&
        this.quickNotes.trim().length >= 5
      )
    },
    historialFiltrado() {
      if (this.filtroResultado === 'todos') {
        return this.historialRutas
      }
      return this.historialRutas.filter(r => r.visit?.result === this.filtroResultado)
    },
    clientesFiltrados() {
      if (!this.busquedaCliente.trim()) {
        return this.clientes
      }
      const busqueda = this.busquedaCliente.toLowerCase()
      return this.clientes.filter(c => 
        c.client.name.toLowerCase().includes(busqueda) ||
        c.client.address?.toLowerCase().includes(busqueda)
      )
    },
    fechaMinima() {
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      return tomorrow.toISOString().split('T')[0]
    }
  },
  mounted() {
    const sellerData = localStorage.getItem('seller')
    if (!sellerData) {
      this.$router.push('/login')
      return
    }
    this.seller = JSON.parse(sellerData)
    this.sellerName = this.seller.name
    
    this.cargarRutasHoy()
    this.cargarHistorial()
    this.cargarClientes()
    this.cargarResumen()
    this.iniciarGPS()
  },
  beforeUnmount() {
    if (this.geoWatcher) {
      navigator.geolocation.clearWatch(this.geoWatcher)
    }
  },
  methods: {
    // ========== CARGA DE DATOS ==========
    async cargarRutasHoy() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/?seller_id=${this.seller.id}`)
        const todas = await response.json()
        const hoy = new Date().toISOString().split('T')[0]
        this.routesHoy = todas.filter(r => r.planned_date?.split('T')[0] === hoy)
      } catch (e) {
        console.error('Error:', e)
      }
    },
    
    async cargarHistorial() {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/seller/${this.seller.id}/history/?months=${this.historialMeses}&page=${this.historialPage}&limit=${this.historialLimit}`
        )
        const data = await response.json()
        this.historialRutas = data.routes || []
        this.historialTotal = data.total || 0
      } catch (e) {
        console.error('Error cargando historial:', e)
        // Fallback al endpoint actual
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL}/routes/?seller_id=${this.seller.id}`)
          this.historialRutas = await response.json()
        } catch (e2) {
          console.error('Error fallback:', e2)
        }
      }
    },
    
    async cargarClientes() {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/seller/${this.seller.id}/clients/?months=${this.historialMeses}`
        )
        const data = await response.json()
        this.clientes = data.clients || []
      } catch (e) {
        console.error('Error cargando clientes:', e)
      }
    },
    
    async cargarResumen() {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/seller/${this.seller.id}/summary/?months=3`
        )
        this.resumen = await response.json()
      } catch (e) {
        console.error('Error cargando resumen:', e)
      }
    },
    
    // ========== GPS ==========
    iniciarGPS() {
      if (!navigator.geolocation) return
      
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          this.ubicacionActual = {
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            accuracy: pos.coords.accuracy
          }
        },
        (err) => console.error('GPS error:', err),
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      )
      
      this.geoWatcher = navigator.geolocation.watchPosition(
        (pos) => {
          this.ubicacionActual = {
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            accuracy: pos.coords.accuracy
          }
        },
        (err) => console.error('GPS watch error:', err),
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      )
    },
    
    // ========== CHECK-IN ==========
    iniciarCheckin(ruta) {
      this.rutaActual = ruta
      this.visitResult = null
      this.clienteEncontrado = false
      this.quickNotes = ''
      this.detailedNotes = ''
      this.showCheckinModal = true
    },
    
    cerrarCheckin() {
      this.showCheckinModal = false
      this.rutaActual = null
    },
    
    async hacerCheckin() {
      if (!this.puedeHacerCheckin) return
      this.cargandoCheckin = true
      
      try {
        // Intentar endpoint v2
        let response = await fetch(`${import.meta.env.VITE_API_URL}/visits/checkin/v2/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            route_id: this.rutaActual.id,
            seller_id: this.rutaActual.seller_id,
            client_id: this.rutaActual.client_id,
            latitude: this.ubicacionActual.latitude,
            longitude: this.ubicacionActual.longitude,
            visit_result: this.visitResult,
            quick_notes: this.quickNotes.trim(),
            detailed_notes: this.detailedNotes.trim() || null,
            client_found: this.clienteEncontrado
          })
        })
        
        // Fallback a endpoint v1 si v2 no existe
        if (response.status === 404) {
          response = await fetch(`${import.meta.env.VITE_API_URL}/visits/checkin/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              route_id: this.rutaActual.id,
              seller_id: this.rutaActual.seller_id,
              client_id: this.rutaActual.client_id,
              latitude: this.ubicacionActual.latitude,
              longitude: this.ubicacionActual.longitude,
              client_found: this.clienteEncontrado,
              notes: `[${this.visitResult?.toUpperCase()}] ${this.quickNotes} | ${this.detailedNotes}`
            })
          })
        }
        
        this.resultadoCheckin = await response.json()
        this.showCheckinModal = false
        this.showResultado = true
        this.cargarRutasHoy()
        this.cargarHistorial()
        this.cargarResumen()
      } catch (e) {
        console.error('Error check-in:', e)
        alert('Error al hacer check-in')
      } finally {
        this.cargandoCheckin = false
      }
    },
    
    cerrarResultado() {
      this.showResultado = false
      this.resultadoCheckin = null
    },
    
    // ========== APLAZAR ==========
    mostrarAplazar(ruta) {
      this.rutaActual = ruta
      this.aplazarRazon = null
      this.aplazarFecha = ''
      this.aplazarNotas = ''
      this.showAplazarModal = true
    },
    
    async confirmarAplazamiento() {
      if (!this.aplazarRazon) return
      this.cargandoAplazar = true
      
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/routes/${this.rutaActual.id}/postpone/`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              reason: this.aplazarRazon,
              new_date: this.aplazarFecha || null,
              notes: this.aplazarNotas || null
            })
          }
        )
        
        if (response.ok) {
          const data = await response.json()
          alert(data.message)
          this.showAplazarModal = false
          this.cargarRutasHoy()
        } else {
          const error = await response.json()
          alert(`Error: ${error.detail}`)
        }
      } catch (e) {
        console.error('Error aplazando:', e)
        alert('Error al aplazar la ruta')
      } finally {
        this.cargandoAplazar = false
      }
    },
    
    // ========== HELPERS ==========
    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString('es-ES', { 
        day: 'numeric', 
        month: 'short',
        year: 'numeric'
      })
    },
    
    formatTime(date) {
      if (!date) return ''
      return new Date(date).toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit'
      })
    },
    
    getStatusClass(status) {
      const classes = {
        pending: 'bg-orange-100 text-orange-800',
        completed: 'bg-green-100 text-green-800',
        cancelled: 'bg-red-100 text-red-800',
        postponed: 'bg-gray-100 text-gray-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    },
    
    getStatusLabel(status) {
      const labels = {
        pending: '⏳ Pendiente',
        completed: '✅ Completada',
        cancelled: '❌ Cancelada',
        postponed: '🔄 Aplazada'
      }
      return labels[status] || status
    },
    
    getResultClass(result) {
      const classes = {
        venta: 'bg-green-100 text-green-800',
        no_venta: 'bg-red-100 text-red-800',
        interesado: 'bg-yellow-100 text-yellow-800',
        seguimiento: 'bg-blue-100 text-blue-800',
        ausente: 'bg-gray-200 text-gray-700'
      }
      return classes[result] || 'bg-gray-100 text-gray-800'
    },
    
    getResultIcon(result) {
      const icons = { venta: '🟢', no_venta: '🔴', interesado: '🟡', seguimiento: '🔵', ausente: '⚫' }
      return icons[result] || '•'
    },
    
    getResultLabel(result) {
      const labels = { venta: 'Venta', no_venta: 'No venta', interesado: 'Interesado', seguimiento: 'Seguimiento', ausente: 'Ausente' }
      return labels[result] || result
    },
    
    verDetalleVisita(ruta) {
      // TODO: Modal con detalles completos
      console.log('Ver detalle:', ruta)
    },
    
    verDetalleCliente(item) {
      // TODO: Modal/vista con historial del cliente
      console.log('Ver cliente:', item)
    },
    
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('seller')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
* {
  -webkit-font-smoothing: antialiased;
}
input, textarea, select {
  font-size: 16px; /* Evita zoom en iOS */
}
</style>
