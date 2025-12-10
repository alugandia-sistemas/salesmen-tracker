#!/bin/bash
# ============================================================================
# TEST DE RENDIMIENTO: /clients/ endpoint
# ============================================================================
# 
# Ejecutar antes y después del fix para comparar
#
# Uso:
#   chmod +x test_performance.sh
#   ./test_performance.sh http://localhost:8000
#   ./test_performance.sh https://tu-backend.railway.app
#
# ============================================================================

API_URL="${1:-http://localhost:8000}"

echo "=============================================="
echo "📊 TEST DE RENDIMIENTO - Endpoint /clients/"
echo "=============================================="
echo "API: $API_URL"
echo ""

# Test 1: Tiempo de respuesta /clients/
echo "🔄 Test 1: Cargando todos los clientes..."
START=$(date +%s.%N)
RESPONSE=$(curl -s -w "\n%{http_code}\n%{time_total}" "$API_URL/clients/")
END=$(date +%s.%N)

HTTP_CODE=$(echo "$RESPONSE" | tail -2 | head -1)
CURL_TIME=$(echo "$RESPONSE" | tail -1)
CLIENT_COUNT=$(echo "$RESPONSE" | head -1 | grep -o '"id"' | wc -l)

echo "   HTTP Status: $HTTP_CODE"
echo "   Clientes cargados: $CLIENT_COUNT"
echo "   ⏱️  Tiempo total: ${CURL_TIME}s"
echo ""

# Test 2: Endpoint de conteo (si existe)
echo "🔄 Test 2: Conteo rápido..."
COUNT_RESPONSE=$(curl -s -w "\n%{time_total}" "$API_URL/clients/count/" 2>/dev/null)
if [ $? -eq 0 ]; then
    COUNT_TIME=$(echo "$COUNT_RESPONSE" | tail -1)
    COUNT=$(echo "$COUNT_RESPONSE" | head -1 | grep -o '"count":[0-9]*' | cut -d: -f2)
    echo "   Conteo: $COUNT clientes"
    echo "   ⏱️  Tiempo: ${COUNT_TIME}s"
else
    echo "   ⚠️  Endpoint /clients/count/ no disponible (añádelo con el fix)"
fi
echo ""

# Test 3: Búsqueda (si existe)
echo "🔄 Test 3: Búsqueda 'garcia'..."
SEARCH_RESPONSE=$(curl -s -w "\n%{time_total}" "$API_URL/clients/search/?q=garcia" 2>/dev/null)
if [ $? -eq 0 ] && [[ "$SEARCH_RESPONSE" != *"Not Found"* ]]; then
    SEARCH_TIME=$(echo "$SEARCH_RESPONSE" | tail -1)
    SEARCH_COUNT=$(echo "$SEARCH_RESPONSE" | head -1 | grep -o '"id"' | wc -l)
    echo "   Resultados: $SEARCH_COUNT"
    echo "   ⏱️  Tiempo: ${SEARCH_TIME}s"
else
    echo "   ⚠️  Endpoint /clients/search/ no disponible"
fi
echo ""

# Test 4: Sync endpoint (si existe)
echo "🔄 Test 4: Sync completo..."
SYNC_RESPONSE=$(curl -s -w "\n%{time_total}" "$API_URL/clients/sync/" 2>/dev/null)
if [ $? -eq 0 ] && [[ "$SYNC_RESPONSE" != *"Not Found"* ]]; then
    SYNC_TIME=$(echo "$SYNC_RESPONSE" | tail -1)
    SYNC_COUNT=$(echo "$SYNC_RESPONSE" | head -1 | grep -o '"synced_count":[0-9]*' | cut -d: -f2)
    echo "   Sincronizados: $SYNC_COUNT"
    echo "   ⏱️  Tiempo: ${SYNC_TIME}s"
else
    echo "   ⚠️  Endpoint /clients/sync/ no disponible"
fi
echo ""

# Resumen
echo "=============================================="
echo "📈 RESUMEN"
echo "=============================================="
echo ""
if (( $(echo "$CURL_TIME < 1.0" | bc -l) )); then
    echo "✅ EXCELENTE: Respuesta en menos de 1 segundo"
    echo "   El fix N+1 está funcionando correctamente"
elif (( $(echo "$CURL_TIME < 3.0" | bc -l) )); then
    echo "⚠️  ACEPTABLE: Respuesta entre 1-3 segundos"
    echo "   Considera aplicar el fix N+1"
else
    echo "❌ LENTO: Respuesta mayor a 3 segundos"
    echo "   URGENTE: Aplica el fix N+1 del archivo patch_clients_endpoint.py"
fi
echo ""
echo "=============================================="

# Benchmark comparativo
echo ""
echo "📊 BENCHMARK ESPERADO:"
echo "┌─────────────────┬────────────┬────────────┐"
echo "│ Métrica         │ Sin fix    │ Con fix    │"
echo "├─────────────────┼────────────┼────────────┤"
echo "│ Queries DB      │ 1.746      │ 1          │"
echo "│ Tiempo respuesta│ 8-12s      │ 0.2-0.4s   │"
echo "│ Mejora          │ -          │ 20-60x     │"
echo "└─────────────────┴────────────┴────────────┘"
echo ""
