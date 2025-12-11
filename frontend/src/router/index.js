import { createRouter, createWebHistory } from 'vue-router'

import Login from '../views/Login.vue'
import Registro from '../views/Registro.vue'
import RegistroConToken from '../views/RegistroConToken.vue'
import SellerDashboard from '../views/SellerDashboard.vue'
import AdminGestion from '../views/AdminGestion.vue'
import AdminInvitaciones from '../views/AdminInvitaciones.vue'
import DirectorioClientes from '../views/DirectorioClientes.vue'
import MyRoute from '../views/MyRoute.vue'
import AdminZones from '../views/AdminZones.vue'
// import ComercialDashboard from '../views/Comercial.vue'

const routes = [
  // Auth
  { 
    path: '/login', 
    component: Login,
    meta: { requiresAuth: false }
  },
  { 
    path: '/registro', 
    component: RegistroConToken,
    meta: { requiresAuth: false }
  },
  { 
    path: '/registro-simple', 
    component: Registro,
    meta: { requiresAuth: false }
  },

  // Vendedor
  { 
    path: '/comercial', 
    component: SellerDashboard,
    meta: { requiresAuth: true }
  },

  // Admin
  { 
    path: '/admin/gestion', 
    component: AdminGestion,
    meta: { requiresAuth: true }
  },
  { 
    path: '/admin/invitaciones', 
    component: AdminInvitaciones,
    meta: { requiresAuth: true }
  },
  // ✅ NUEVO: Directorio de Clientes
  { 
    path: '/admin/clientes', 
    component: DirectorioClientes,
    meta: { requiresAuth: true }
  },
  { 
    path: '/admin/zones', 
    component: AdminZones,
    meta: { requiresAuth: true }
  },
  {
    path: '/my-route',
    component: MyRoute,
    meta: { requiresAuth: true }
  },

  // Redirect
  { 
    path: '/', 
    redirect: '/comercial' 
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Guard: Verificar autenticación
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const requiresAuth = to.meta.requiresAuth

  if (requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/comercial')
  } else if (to.path === '/registro' && token) {
    next()
  } else {
    next()
  }
})

export default router
