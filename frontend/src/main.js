import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

// ============================================================================
// 📊 VERCEL ANALYTICS & WEB VITALS - IMPORTS CORRECTOS
// ============================================================================

import { inject } from '@vercel/analytics'
inject()

// ✅ IMPORTS CORRECTOS: web-vitals exporta getCLS, getFID, etc.
// ❌ NO existe: import { webVitals }
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

// Reportar Web Vitals a consola
getCLS(metric => console.log(`[Web Vital] CLS: ${metric.value.toFixed(3)}`))
getFID(metric => console.log(`[Web Vital] FID: ${metric.value.toFixed(2)}ms`))
getFCP(metric => console.log(`[Web Vital] FCP: ${metric.value.toFixed(2)}ms`))
getLCP(metric => console.log(`[Web Vital] LCP: ${metric.value.toFixed(2)}ms`))
getTTFB(metric => console.log(`[Web Vital] TTFB: ${metric.value.toFixed(2)}ms`))

// Helper global para tracking de eventos
window.analytics = {
  trackEvent: (eventName, eventData) => {
    console.log(`[Analytics] ${eventName}`, eventData)
    // En producción, aquí irían los datos a Vercel Analytics
  },
  trackCheckin: (distance, isValid) => {
    window.analytics.trackEvent('checkin', {
      distance_meters: distance,
      is_valid: isValid,
      timestamp: new Date().toISOString()
    })
  }
}

const app = createApp(App)

app.use(router)

app.mount('#app')
