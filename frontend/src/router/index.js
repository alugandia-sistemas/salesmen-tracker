import { createRouter, createWebHistory } from 'vue-router'

import Login from '../views/Login.vue'
import Registro from '../views/Registro.vue'
import Comercial from '../views/Comercial.vue'
import AdminGestion from '../views/AdminGestion.vue'

const routes = [
  // Auth
  { 
    path: '/login', 
    component: Login,
    meta: { requiresAuth: false }
  },
  { 
    path: '/registro', 
    component: Registro,
    meta: { requiresAuth: false }
  },

  // Vendedor
  { 
    path: '/comercial', 
    component: Comercial,
    meta: { requiresAuth: true }
  },

  // Admin
  { 
    path: '/admin/gestion', 
    component: AdminGestion,
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
  } else if ((to.path === '/login' || to.path === '/registro') && token) {
    next('/comercial')
  } else {
    next()
  }
})

export default router
