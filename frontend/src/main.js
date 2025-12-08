import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

// ============================================================================
// 📊 VERCEL ANALYTICS & WEB VITALS INTEGRATION
// ============================================================================

import { inject } from '@vercel/analytics'
inject()

import { webVitals } from '@vercel/web-vitals'

webVitals({
  path: '/_vercel/insights/event',
  params: {
    beforeSend: (webVital) => {
      console.log(
        `[Web Vital] ${webVital.name}: ${webVital.value.toFixed(2)}ms`
      )
    }
  }
})

// ============================================================================
// EVENTOS PERSONALIZADOS
// ============================================================================

window.analytics = {
  trackEvent: (eventName, eventData) => {
    const { Analytics } = window
    if (Analytics && Analytics.event) {
      Analytics.event(eventName, eventData)
      console.log(`[Analytics Event] ${eventName}`, eventData)
    }
  },
  trackCheckin: (distance, isValid) => {
    window.analytics.trackEvent('checkin', {
      distance_meters: distance,
      is_valid: isValid,
      timestamp: new Date().toISOString()
    })
  },
  trackVisit: (clientId, duration) => {
    window.analytics.trackEvent('visit_completed', {
      client_id: clientId,
      duration_seconds: duration
    })
  }
}

// ============================================================================
// CREAR APP
// ============================================================================

const app = createApp(App)

app.use(router)

app.mount('#app')
