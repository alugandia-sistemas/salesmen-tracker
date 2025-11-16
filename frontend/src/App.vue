<!-- App.vue -->
<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-blue-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-4">
        <h1 class="text-2xl font-bold">Sistema de Seguimiento de Vendedores</h1>
        <p class="text-blue-100 text-sm mt-1">Gestión de rutas y visitas en tiempo real</p>
      </div>
    </header>

    <!-- Navigation -->
    <nav class="bg-white border-b shadow-sm">
      <div class="container mx-auto">
        <div class="flex overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="currentView = tab.id"
            :class="[
              'px-6 py-3 font-medium whitespace-nowrap transition-colors',
              currentView === tab.id
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            {{ tab.icon }} {{ tab.label }}
          </button>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <main class="container mx-auto px-4 py-6">
      <!-- Dashboard View -->
      <div v-if="currentView === 'dashboard'" class="space-y-6">
        <h2 class="text-2xl font-bold">Panel de Control</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            title="Vendedores Activos"
            :value="stats.active_sellers"
            icon="👥"
            color="blue"
          />
          <StatCard
            title="Visitas Hoy"
            :value="stats.total_visits_today"
            icon="📍"
            color="green"
          />
          <StatCard
            title="Rutas Pendientes"
            :value="stats.pending_routes"
            icon="⏰"
            color="yellow"
          />
          <StatCard
            title="Oportunidades"
            :value="stats.open_opportunities"
            icon="💼"
            color="purple"
          />
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-xl font-bold mb-4">Vendedores</h3>
          <div class="space-y-3">
            <div
              v-for="seller in sellers"
              :key="seller.id"
              class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center gap-3">
                <div
                  :class="[
                    'w-3 h-3 rounded-full',
                    seller.active ? 'bg-green-500' : 'bg-gray-400'
                  ]"
                ></div>
                <div>
                  <p class="font-semibold">{{ seller.name }}</p>
                  <p class="text-sm text-gray-600">{{ seller.email }}</p>
                </div>
              </div>
              <span
                :class="[
                  'px-3 py-1 rounded-full text-sm',
                  seller.active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-200 text-gray-600'
                ]"
              >
                {{ seller.active ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Routes View -->
      <div v-if="currentView === 'routes'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-bold">Gestión de Rutas</h2>
          <button
            @click="showRouteForm = !showRouteForm"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            ➕ Nueva Ruta
          </button>
        </div>

        <!-- Form -->
        <div v-if="showRouteForm" class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-bold mb-4">Agregar Nueva Ruta</h3>
          <form @submit.prevent="createRoute" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Vendedor</label>
                <select
                  v-model="newRoute.seller_id"
                  required
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="">Seleccionar...</option>
                  <option v-for="seller in sellers" :key="seller.id" :value="seller.id">
                    {{ seller.name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Cliente</label>
                <select
                  v-model="newRoute.client_id"
                  required
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="">Seleccionar...</option>
                  <option v-for="client in clients" :key="client.id" :value="client.id">
                    {{ client.name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Fecha y Hora</label>
                <input
                  v-model="newRoute.scheduled_date"
                  type="datetime-local"
                  required
                  class="w-full border rounded px-3 py-2"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Notas</label>
                <input
                  v-model="newRoute.notes"
                  type="text"
                  class="w-full border rounded px-3 py-2"
                  placeholder="Notas opcionales..."
                />
              </div>
            </div>

            <div class="flex gap-2">
              <button
                type="submit"
                class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                Crear Ruta
              </button>
              <button
                type="button"
                @click="showRouteForm = false"
                class="bg-gray-300 text-gray-700 px-6 py-2 rounded hover:bg-gray-400"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>

        <!-- Routes List -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-bold mb-4">Rutas Programadas</h3>
          <div class="space-y-3">
            <div
              v-for="route in routes"
              :key="route.id"
              class="p-4 border rounded-lg"
            >
              <div class="flex justify-between items-start">
                <div>
                  <p class="font-semibold">{{ getClientName(route.client_id) }}</p>
                  <p class="text-sm text-gray-600">
                    Vendedor: {{ getSellerName(route.seller_id) }}
                  </p>
                  <p class="text-sm text-gray-500">
                    📅 {{ formatDate(route.scheduled_date) }}
                  </p>
                </div>
                <span
                  :class="[
                    'px-3 py-1 rounded-full text-sm',
                    getStatusColor(route.status)
                  ]"
                >
                  {{ getStatusText(route.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Clients View -->
      <div v-if="currentView === 'clients'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-bold">Gestión de Clientes</h2>
          <button
            @click="showClientForm = !showClientForm"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            ➕ Nuevo Cliente
          </button>
        </div>

        <!-- Client Form -->
        <div v-if="showClientForm" class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-bold mb-4">Agregar Nuevo Cliente</h3>
          <form @submit.prevent="createClient" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Nombre *</label>
                <input
                  v-model="newClient.name"
                  type="text"
                  required
                  class="w-full border rounded px-3 py-2"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Teléfono</label>
                <input
                  v-model="newClient.phone"
                  type="tel"
                  class="w-full border rounded px-3 py-2"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Email</label>
                <input
                  v-model="newClient.email"
                  type="email"
                  class="w-full border rounded px-3 py-2"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Dirección</label>
                <input
                  v-model="newClient.address"
                  type="text"
                  class="w-full border rounded px-3 py-2"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Latitud *</label>
                <input
                  v-model.number="newClient.latitude"
                  type="number"
                  step="any"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="19.4326"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Longitud *</label>
                <input
                  v-model.number="newClient.longitude"
                  type="number"
                  step="any"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="-99.1332"
                />
              </div>
            </div>

            <button
              type="button"
              @click="getCurrentLocation"
              class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 flex items-center gap-2"
            >
              📍 Usar Mi Ubicación Actual
            </button>

            <div class="flex gap-2">
              <button
                type="submit"
                class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                Crear Cliente
              </button>
              <button
                type="button"
                @click="showClientForm = false"
                class="bg-gray-300 text-gray-700 px-6 py-2 rounded hover:bg-gray-400"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>

        <!-- Clients List -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-bold mb-4">Lista de Clientes</h3>
          <div class="space-y-3">
            <div
              v-for="client in clients"
              :key="client.id"
              class="p-4 border rounded-lg flex justify-between items-center"
            >
              <div>
                <p class="font-semibold">{{ client.name }}</p>
                <p class="text-sm text-gray-600">📍 {{ client.address || 'Sin dirección' }}</p>
                <p class="text-xs text-gray-500" v-if="client.latitude">
                  Coords: {{ client.latitude?.toFixed(4) }}, {{ client.longitude?.toFixed(4) }}
                </p>
              </div>
              <span
                :class="[
                  'px-3 py-1 rounded-full text-sm',
                  client.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                ]"
              >
                {{ client.status === 'active' ? 'Activo' : 'Pendiente' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Check-in View -->
      <div v-if="currentView === 'checkin'" class="space-y-6">
        <h2 class="text-2xl font-bold">Check-in de Visitas</h2>

        <div v-if="currentLocation" class="bg-green-50 border border-green-200 rounded-lg p-4">
          <p class="text-green-800 font-semibold flex items-center gap-2">
            🧭 Ubicación detectada
          </p>
          <p class="text-sm text-green-700">
            Lat: {{ currentLocation.latitude.toFixed(6) }}, Lng: {{ currentLocation.longitude.toFixed(6) }}
          </p>
        </div>

        <!-- Pending Routes -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-bold mb-4">Rutas Pendientes de Hoy</h3>
          <div class="space-y-3">
            <div
              v-for="route in pendingRoutes"
              :key="route.id"
              class="p-4 border rounded-lg"
            >
              <div class="mb-3">
                <p class="font-semibold">{{ getClientName(route.client_id) }}</p>
                <p class="text-sm text-gray-600">
                  Hora programada: {{ formatTime(route.scheduled_date) }}
                </p>
              </div>
              <textarea
                v-model="checkInNotes[route.id]"
                class="w-full border rounded px-3 py-2 mb-2"
                placeholder="Notas de la visita..."
                rows="2"
              ></textarea>
              <button
                @click="doCheckIn(route.id)"
                class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 flex items-center gap-2"
              >
                📍 Hacer Check-in
              </button>
            </div>
            <p v-if="pendingRoutes.length === 0" class="text-gray-500 text-center py-4">
              No hay rutas pendientes para hoy
            </p>
          </div>
        </div>

        <!-- Active Visits -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-bold mb-4">Visitas en Progreso</h3>
          <div class="space-y-3">
            <div
              v-for="visit in activeVisits"
              :key="visit.id"
              class="p-4 border border-blue-200 bg-blue-50 rounded-lg"
            >
              <p class="font-semibold">{{ getClientName(visit.client_id) }}</p>
              <p class="text-sm text-gray-600">Check-in: {{ formatTime(visit.check_in_time) }}</p>
              <p class="text-sm text-gray-600 mb-2">Notas: {{ visit.notes || 'Sin notas' }}</p>
              <p v-if="visit.distance_to_client" class="text-xs text-gray-500 mb-2">
                Distancia al cliente: {{ visit.distance_to_client.toFixed(0) }} metros
              </p>
              <button
                @click="doCheckOut(visit.id)"
                class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 flex items-center gap-2"
              >
                ✅ Hacer Check-out
              </button>
            </div>
            <p v-if="activeVisits.length === 0" class="text-gray-500 text-center py-4">
              No hay visitas en progreso
            </p>
          </div>
        </div>

        <!-- Completed Visits -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-bold mb-4">Visitas Completadas Hoy</h3>
          <div class="space-y-3">
            <div
              v-for="visit in completedVisits"
              :key="visit.id"
              class="p-4 border border-green-200 bg-green-50 rounded-lg"
            >
              <p class="font-semibold">{{ getClientName(visit.client_id) }}</p>
              <div class="text-sm text-gray-600">
                <p>Check-in: {{ formatTime(visit.check_in_time) }}</p>
                <p>Check-out: {{ formatTime(visit.check_out_time) }}</p>
                <p v-if="visit.notes">Notas: {{ visit.notes }}</p>
              </div>
            </div>
            <p v-if="completedVisits.length === 0" class="text-gray-500 text-center py-4">
              No hay visitas completadas hoy
            </p>
          </div>
        </div>
      </div>

      <!-- Opportunities View -->
      <div v-if="currentView === 'opportunities'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-bold">Oportunidades de Negocio</h2>
          <button
            @click="showOpportunityForm = !showOpportunityForm"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            ➕ Nueva Oportunidad
          </button>
        </div>

        <!-- Opportunity Form -->
        <div v-if="showOpportunityForm" class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-bold mb-4">Agregar Nueva Oportunidad</h3>
          <form @submit.prevent="createOpportunity" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Cliente *</label>
                <select
                  v-model="newOpportunity.client_id"
                  required
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="">Seleccionar...</option>
                  <option v-for="client in clients" :key="client.id" :value="client.id">
                    {{ client.name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Vendedor *</label>
                <select
                  v-model="newOpportunity.seller_id"
                  required
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="">Seleccionar...</option>
                  <option v-for="seller in sellers" :key="seller.id" :value="seller.id">
                    {{ seller.name }}
                  </option>
                </select>
              </div>

              <div class="md:col-span-2">
                <label class="block text-sm font-medium mb-1">Título *</label>
                <input
                  v-model="newOpportunity.title"
                  type="text"
                  required
                  class="w-full border rounded px-3 py-2"
                />
              </div>

              <div class="md:col-span-2">
                <label class="block text-sm font-medium mb-1">Descripción</label>
                <textarea
                  v-model="newOpportunity.description"
                  class="w-full border rounded px-3 py-2"
                  rows="3"
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Valor Estimado</label>
                <input
                  v-model.number="newOpportunity.estimated_value"
                  type="number"
                  step="0.01"
                  class="w-full border rounded px-3 py-2"
                  placeholder="15000.00"
                />
              </div>
            </div>

            <div class="flex gap-2">
              <button
                type="submit"
                class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                Crear Oportunidad
              </button>
              <button
                type="button"
                @click="showOpportunityForm = false"
                class="bg-gray-300 text-gray-700 px-6 py-2 rounded hover:bg-gray-400"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>

        <!-- Opportunities List -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="space-y-4">
            <div
              v-for="opp in opportunities"
              :key="opp.id"
              class="p-4 border rounded-lg"
            >
              <div class="flex justify-between items-start mb-2">
                <div>
                  <p class="font-bold text-lg">{{ opp.title }}</p>
                  <p class="text-sm text-gray-600">Cliente: {{ getClientName(opp.client_id) }}</p>
                  <p class="text-sm text-gray-600">Vendedor: {{ getSellerName(opp.seller_id) }}</p>
                  <p class="text-sm text-gray-500 mt-1">{{ opp.description }}</p>
                </div>
                <div class="text-right">
                  <p class="text-2xl font-bold text-green-600">
                    ${{ opp.estimated_value?.toLocaleString() || '0' }}
                  </p>
                  <p class="text-xs text-gray-500">{{ formatDate(opp.created_at) }}</p>
                </div>
              </div>
              <span
                :class="[
                  'inline-block px-3 py-1 rounded-full text-sm',
                  opp.status === 'open' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'
                ]"
              >
                {{ opp.status === 'open' ? 'Abierta' : 'En Negociación' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

// API Base URL
const API_URL = 'http://localhost:8000';

// State
const currentView = ref('dashboard');
const currentLocation = ref(null);

// Data
const sellers = ref([]);
const clients = ref([]);
const routes = ref([]);
const visits = ref([]);
const opportunities = ref([]);
const stats = ref({
  active_sellers: 0,
  total_visits_today: 0,
  pending_routes: 0,
  open_opportunities: 0
});

// Forms visibility
const showRouteForm = ref(false);
const showClientForm = ref(false);
const showOpportunityForm = ref(false);

// Form data
const newRoute = ref({
  seller_id: '',
  client_id: '',
  scheduled_date: '',
  notes: ''
});

const newClient = ref({
  name: '',
  address: '',
  phone: '',
  email: '',
  latitude: null,
  longitude: null
});

const newOpportunity = ref({
  client_id: '',
  seller_id: '',
  title: '',
  description: '',
  estimated_value: null
});

const checkInNotes = ref({});

// Tabs
const tabs = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'routes', label: 'Rutas', icon: '🗺️' },
  { id: 'clients', label: 'Clientes', icon: '👥' },
  { id: 'checkin', label: 'Check-in', icon: '📍' },
  { id: 'opportunities', label: 'Oportunidades', icon: '💼' }
];

// Computed
const pendingRoutes = computed(() => 
  routes.value.filter(r => r.status === 'pending')
);

const activeVisits = computed(() => 
  visits.value.filter(v => !v.check_out_time)
);

const completedVisits = computed(() => 
  visits.value.filter(v => v.check_out_time)
);

// Methods
const fetchData = async () => {
  try {
    const [sellersRes, clientsRes, routesRes, visitsRes, oppsRes, statsRes] = await Promise.all([
      fetch(`${API_URL}/sellers/`),
      fetch(`${API_URL}/clients/`),
      fetch(`${API_URL}/routes/`),
      fetch(`${API_URL}/visits/`),
      fetch(`${API_URL}/opportunities/`),
      fetch(`${API_URL}/dashboard/stats`)
    ]);

    sellers.value = await sellersRes.json();
    clients.value = await clientsRes.json();
    routes.value = await routesRes.json();
    visits.value = await visitsRes.json();
    opportunities.value = await oppsRes.json();
    stats.value = await statsRes.json();
  } catch (error) {
    console.error('Error fetching data:', error);
    alert('Error al cargar los datos');
  }
};

const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    alert('Geolocalización no soportada por el navegador');
    return;
  }

  // Mostrar mensaje de espera
  const loadingMsg = 'Obteniendo ubicación precisa...';
  console.log(loadingMsg);

  // Opciones de alta precisión
  const options = {
    enableHighAccuracy: true,  // ⭐ Usar GPS de alta precisión
    timeout: 30000,            // Esperar hasta 30 segundos
    maximumAge: 0              // No usar caché, siempre obtener nueva ubicación
  };

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const accuracy = position.coords.accuracy; // Precisión en metros
      
      currentLocation.value = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: accuracy,
        altitude: position.coords.altitude,
        altitudeAccuracy: position.coords.altitudeAccuracy,
        heading: position.coords.heading,
        speed: position.coords.speed,
        timestamp: position.timestamp
      };

      // Validar precisión
      if (accuracy > 50) {
        alert(`⚠️ Ubicación obtenida con baja precisión: ±${accuracy.toFixed(0)}m. Intenta moverte a un lugar con mejor señal GPS.`);
      } else if (accuracy > 20) {
        alert(`✓ Ubicación obtenida con precisión moderada: ±${accuracy.toFixed(0)}m`);
      } else {
        alert(`✅ Ubicación obtenida con alta precisión: ±${accuracy.toFixed(0)}m`);
      }

      console.log('Ubicación obtenida:', {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
        accuracy: `±${accuracy.toFixed(1)}m`,
        timestamp: new Date(position.timestamp).toLocaleString()
      });
    },
    (error) => {
      console.error('Error getting location:', error);
      
      let errorMsg = 'No se pudo obtener la ubicación. ';
      switch(error.code) {
        case error.PERMISSION_DENIED:
          errorMsg += 'Permiso denegado. Habilita la ubicación en tu navegador.';
          break;
        case error.POSITION_UNAVAILABLE:
          errorMsg += 'Información de ubicación no disponible. Verifica tu conexión GPS.';
          break;
        case error.TIMEOUT:
          errorMsg += 'Timeout. La solicitud tardó demasiado. Intenta de nuevo.';
          break;
        default:
          errorMsg += 'Error desconocido.';
      }
      
      alert(errorMsg);
    },
    options  // ⭐ Pasar opciones de alta precisión
  );
};

const createRoute = async () => {
  try {
    const response = await fetch(`${API_URL}/routes/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newRoute.value)
    });

    if (response.ok) {
      alert('Ruta creada exitosamente');
      newRoute.value = { seller_id: '', client_id: '', scheduled_date: '', notes: '' };
      showRouteForm.value = false;
      fetchData();
    }
  } catch (error) {
    console.error('Error creating route:', error);
    alert('Error al crear la ruta');
  }
};

const createClient = async () => {
  try {
    const response = await fetch(`${API_URL}/clients/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newClient.value)
    });

    if (response.ok) {
      alert('Cliente creado exitosamente');
      newClient.value = { name: '', address: '', phone: '', email: '', latitude: null, longitude: null };
      showClientForm.value = false;
      fetchData();
    }
  } catch (error) {
    console.error('Error creating client:', error);
    alert('Error al crear el cliente');
  }
};

const createOpportunity = async () => {
  try {
    const response = await fetch(`${API_URL}/opportunities/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newOpportunity.value)
    });

    if (response.ok) {
      alert('Oportunidad creada exitosamente');
      newOpportunity.value = { client_id: '', seller_id: '', title: '', description: '', estimated_value: null };
      showOpportunityForm.value = false;
      fetchData();
    }
  } catch (error) {
    console.error('Error creating opportunity:', error);
    alert('Error al crear la oportunidad');
  }
};

const doCheckIn = async (routeId) => {
  if (!currentLocation.value) {
    alert('Obteniendo ubicación...');
    getCurrentLocation();
    return;
  }

  try {
    const response = await fetch(`${API_URL}/visits/checkin/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        route_id: routeId,
        latitude: currentLocation.value.latitude,
        longitude: currentLocation.value.longitude,
        notes: checkInNotes.value[routeId] || ''
      })
    });

    if (response.ok) {
      alert('Check-in realizado exitosamente');
      checkInNotes.value[routeId] = '';
      fetchData();
    }
  } catch (error) {
    console.error('Error doing check-in:', error);
    alert('Error al hacer check-in');
  }
};

const doCheckOut = async (visitId) => {
  if (!currentLocation.value) {
    alert('Obteniendo ubicación...');
    getCurrentLocation();
    return;
  }

  try {
    const response = await fetch(`${API_URL}/visits/checkout/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        visit_id: visitId,
        latitude: currentLocation.value.latitude,
        longitude: currentLocation.value.longitude
      })
    });

    if (response.ok) {
      alert('Check-out realizado exitosamente');
      fetchData();
    }
  } catch (error) {
    console.error('Error doing check-out:', error);
    alert('Error al hacer check-out');
  }
};

// Helper functions
const getClientName = (clientId) => {
  const client = clients.value.find(c => c.id === clientId);
  return client ? client.name : 'Cliente desconocido';
};

const getSellerName = (sellerId) => {
  const seller = sellers.value.find(s => s.id === sellerId);
  return seller ? seller.name : 'Vendedor desconocido';
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const formatTime = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getStatusColor = (status) => {
  const colors = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'in_progress': 'bg-blue-100 text-blue-800',
    'completed': 'bg-green-100 text-green-800',
    'cancelled': 'bg-red-100 text-red-800'
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
};

const getStatusText = (status) => {
  const texts = {
    'pending': 'Pendiente',
    'in_progress': 'En Progreso',
    'completed': 'Completada',
    'cancelled': 'Cancelada'
  };
  return texts[status] || status;
};

// Lifecycle
onMounted(() => {
  fetchData();
  getCurrentLocation();
});
</script>

<script>
// StatCard Component
export const StatCard = {
  props: ['title', 'value', 'icon', 'color'],
  template: `
    <div class="bg-white p-6 rounded-lg shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-gray-500 text-sm">{{ title }}</p>
          <p :class="'text-3xl font-bold text-' + color + '-600'">{{ value }}</p>
        </div>
        <div class="text-4xl">{{ icon }}</div>
      </div>
    </div>
  `
};
</script>

<style>
@import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');

* {
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>