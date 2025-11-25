// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
// import Login from '../views/Login.vue'
import Admin from '../views/Admin.vue'
import AdminGestion from '../views/AdminGestion.vue'
import Comercial from '../views/Comercial.vue'

const routes = [
  // { path: '/', redirect: '/login' },
  // { path: '/login', component: Login },
  
  { path: '/', redirect: '/comercial' },
  { 
    path: '/admin', 
    component: Admin,
    meta: { requiresAuth: true, role: 'admin' }
  },
  { 
    path: '/admin/gestion', 
    component: AdminGestion,
    meta: { requiresAuth: true, role: 'admin' }
  },
  { 
    path: '/comercial', 
    component: Comercial,
    meta: { requiresAuth: true, role: 'comercial' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router