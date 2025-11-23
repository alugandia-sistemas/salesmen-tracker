// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Admin from '../views/Admin.vue'
import Comercial from '../views/Comercial.vue'
import AdminGestion from '../views/AdminGestion.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/admin',
      component: Admin,
      meta: { role: 'admin' }
    },
    {
      path: '/admin/gestion',
      component: AdminGestion,
    },
    {
      path: '/comercial',
      component: Comercial,
      meta: { role: 'comercial' }
    },
    {
      path: '/',
      redirect: '/comercial'  // Por defecto, comercial
    }
  ]
})

export default router