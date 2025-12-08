// ============================================================================
// 📊 ANALYTICS HELPERS PARA SALESMEN TRACKER
// ============================================================================

/**
 * Monitorear CHECK-IN de vendedor
 */
export const trackCheckin = (routeId, clientId, distance, isValid) => {
  try {
    if (window.analytics?.trackCheckin) {
      window.analytics.trackCheckin(distance, isValid)
    }
    
    console.log('✅ [Analytics] Check-in registrado', {
      route_id: routeId,
      client_id: clientId,
      distance_meters: distance,
      is_valid: isValid,
      timestamp: new Date().toISOString()
    })
  } catch (e) {
    console.error('Error tracking checkin:', e)
  }
}

/**
 * Monitorear VISITA COMPLETADA
 */
export const trackVisitCompleted = (clientName, duration) => {
  try {
    if (window.analytics?.trackVisit) {
      window.analytics.trackVisit(clientName, duration)
    }
    
    console.log('✅ [Analytics] Visita completada', {
      client: clientName,
      duration_seconds: duration,
      timestamp: new Date().toISOString()
    })
  } catch (e) {
    console.error('Error tracking visit:', e)
  }
}

/**
 * Monitorear ERRORES DE GPS/GEOLOCALIZACIÓN
 */
export const trackGPSError = (error, context) => {
  try {
    if (window.analytics?.trackEvent) {
      window.analytics.trackEvent('gps_error', {
        error_message: error,
        context: context,
        timestamp: new Date().toISOString()
      })
    }
    
    console.error('⚠️ [Analytics] Error GPS', { error, context })
  } catch (e) {
    console.error('Error tracking gps error:', e)
  }
}

/**
 * Monitorear LOGIN
 */
export const trackLogin = (sellerId, sellerName) => {
  try {
    if (window.analytics?.trackEvent) {
      window.analytics.trackEvent('seller_login', {
        seller_id: sellerId,
        seller_name: sellerName,
        timestamp: new Date().toISOString()
      })
    }
    
    console.log('✅ [Analytics] Login de vendedor', { sellerId, sellerName })
  } catch (e) {
    console.error('Error tracking login:', e)
  }
}

/**
 * Monitorear ERRORES DE RED/API
 */
export const trackAPIError = (endpoint, statusCode, error) => {
  try {
    if (window.analytics?.trackEvent) {
      window.analytics.trackEvent('api_error', {
        endpoint: endpoint,
        status_code: statusCode,
        error_message: error,
        timestamp: new Date().toISOString()
      })
    }
    
    console.error('🔴 [Analytics] Error API', { endpoint, statusCode, error })
  } catch (e) {
    console.error('Error tracking api error:', e)
  }
}

/**
 * Monitorear RUTAS DEL DÍA
 */
export const trackDailyRoutes = (totalRoutes, completedRoutes) => {
  try {
    if (window.analytics?.trackEvent) {
      window.analytics.trackEvent('daily_routes_summary', {
        total_routes: totalRoutes,
        completed_routes: completedRoutes,
        completion_rate: totalRoutes > 0 ? (completedRoutes / totalRoutes * 100) : 0,
        timestamp: new Date().toISOString()
      })
    }
    
    console.log('📊 [Analytics] Rutas del día', { totalRoutes, completedRoutes })
  } catch (e) {
    console.error('Error tracking daily routes:', e)
  }
}

/**
 * Monitorear FRAUD ALERT
 */
export const trackFraudAlert = (visitId, fraudFlags) => {
  try {
    if (window.analytics?.trackEvent) {
      window.analytics.trackEvent('fraud_alert', {
        visit_id: visitId,
        fraud_flags: fraudFlags,
        timestamp: new Date().toISOString()
      })
    }
    
    console.warn('🚨 [Analytics] Alerta de fraude', { visitId, fraudFlags })
  } catch (e) {
    console.error('Error tracking fraud alert:', e)
  }
}
