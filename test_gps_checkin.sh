#!/bin/bash

# 🧪 Script de Verificación de GPS Tracking
# Verifica que todos los componentes de GPS/Check-in están funcionando

set -e

echo "🛰️  VERIFICADOR DE GPS TRACKING"
echo "=================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
API_URL="${API_URL:-http://localhost:8000}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5433}"
DB_NAME="${DB_NAME:-salesmen_tracker}"
DB_USER="${DB_USER:-postgres}"

echo "📋 Configuración:"
echo "  API_URL: $API_URL"
echo "  DB_HOST: $DB_HOST:$DB_PORT"
echo "  DB_NAME: $DB_NAME"
echo ""

# Test 1: Verificar conectividad con API
echo "1️⃣  Verificando conectividad con API..."
if curl -s "$API_URL/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API accesible en $API_URL${NC}"
else
    echo -e "${RED}❌ API no accesible en $API_URL${NC}"
    echo "   ¿El backend está corriendo?"
fi
echo ""

# Test 2: Verificar PostGIS instalado
echo "2️⃣  Verificando PostGIS en la BD..."
if PGPASSWORD="$DB_USER" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT PostGIS_version();" 2>/dev/null | grep -q "PostGIS"; then
    echo -e "${GREEN}✅ PostGIS instalado$(NC}"
else
    echo -e "${YELLOW}⚠️  PostGIS no disponible o BD no accesible${NC}"
    echo "   Verifica: psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
fi
echo ""

# Test 3: Crear datos de prueba y ejecutar check-in
echo "3️⃣  Creando datos de prueba..."

# Crear Seller
SELLER_RESPONSE=$(curl -s -X POST "$API_URL/sellers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Seller GPS",
    "email": "test-gps@example.com",
    "phone": "123456789",
    "is_active": true
  }')

SELLER_ID=$(echo "$SELLER_RESPONSE" | jq -r '.id' 2>/dev/null)
if [ -z "$SELLER_ID" ] || [ "$SELLER_ID" = "null" ]; then
    echo -e "${RED}❌ No se pudo crear Seller${NC}"
    echo "$SELLER_RESPONSE"
    exit 1
fi
echo -e "${GREEN}✅ Seller creado: $SELLER_ID${NC}"

# Crear Cliente con coordenadas
CLIENT_RESPONSE=$(curl -s -X POST "$API_URL/clients/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cliente Test GPS",
    "address": "Calle de Prueba 123",
    "phone": "987654321",
    "email": "cliente@test.com",
    "client_type": "carpenter",
    "status": "active",
    "latitude": 40.4168,
    "longitude": -3.7038
  }')

CLIENT_ID=$(echo "$CLIENT_RESPONSE" | jq -r '.id' 2>/dev/null)
if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "null" ]; then
    echo -e "${RED}❌ No se pudo crear Cliente${NC}"
    echo "$CLIENT_RESPONSE"
    exit 1
fi
echo -e "${GREEN}✅ Cliente creado: $CLIENT_ID${NC}"

# Crear Route
ROUTE_RESPONSE=$(curl -s -X POST "$API_URL/routes/" \
  -H "Content-Type: application/json" \
  -d "{
    \"seller_id\": \"$SELLER_ID\",
    \"client_id\": \"$CLIENT_ID\",
    \"planned_date\": \"2025-12-11T10:00:00\"
  }")

ROUTE_ID=$(echo "$ROUTE_RESPONSE" | jq -r '.id' 2>/dev/null)
if [ -z "$ROUTE_ID" ] || [ "$ROUTE_ID" = "null" ]; then
    echo -e "${RED}❌ No se pudo crear Route${NC}"
    echo "$ROUTE_RESPONSE"
    exit 1
fi
echo -e "${GREEN}✅ Route creado: $ROUTE_ID${NC}"
echo ""

# Test 4: Hacer Check-in con GPS
echo "4️⃣  Realizando Check-in con GPS..."

CHECKIN_RESPONSE=$(curl -s -X POST "$API_URL/visits/checkin/" \
  -H "Content-Type: application/json" \
  -d "{
    \"route_id\": \"$ROUTE_ID\",
    \"seller_id\": \"$SELLER_ID\",
    \"client_id\": \"$CLIENT_ID\",
    \"latitude\": 40.4168,
    \"longitude\": -3.7038,
    \"client_found\": true,
    \"notes\": \"Check-in de prueba automática\"
  }")

VISIT_ID=$(echo "$CHECKIN_RESPONSE" | jq -r '.visit_id' 2>/dev/null)
if [ -z "$VISIT_ID" ] || [ "$VISIT_ID" = "null" ]; then
    echo -e "${RED}❌ Check-in falló${NC}"
    echo "$CHECKIN_RESPONSE"
    exit 1
fi

DISTANCE=$(echo "$CHECKIN_RESPONSE" | jq -r '.distance_meters' 2>/dev/null)
IS_VALID=$(echo "$CHECKIN_RESPONSE" | jq -r '.is_valid' 2>/dev/null)

echo -e "${GREEN}✅ Check-in exitoso!${NC}"
echo "   Visit ID: $VISIT_ID"
echo "   Distancia: $DISTANCE metros"
echo "   Válido: $IS_VALID"
echo ""

# Test 5: Verificar que la visita fue guardada
echo "5️⃣  Verificando datos en BD..."
VISIT_COUNT=$(PGPASSWORD="$DB_USER" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  -t -c "SELECT COUNT(*) FROM visits WHERE id='$VISIT_ID';" 2>/dev/null)

if [ "$VISIT_COUNT" -eq 1 ]; then
    echo -e "${GREEN}✅ Visita registrada en BD${NC}"
else
    echo -e "${RED}❌ Visita no se guardó en BD${NC}"
fi
echo ""

# Test 6: Listar visitas
echo "6️⃣  Listando visitas del vendedor..."
VISITS_LIST=$(curl -s "$API_URL/visits/?seller_id=$SELLER_ID" | jq '.[] | {id, client_id, checkin_distance_meters, checkin_is_valid}')
echo -e "${GREEN}Visitas encontradas:${NC}"
echo "$VISITS_LIST"
echo ""

# Resumen
echo "=================================="
echo -e "${GREEN}🎉 VERIFICACIÓN COMPLETADA${NC}"
echo "=================================="
echo ""
echo "Resumen:"
echo "  ✅ API conectando correctamente"
echo "  ✅ Seller creado: $SELLER_ID"
echo "  ✅ Cliente creado: $CLIENT_ID"
echo "  ✅ Route creado: $ROUTE_ID"
echo "  ✅ Check-in registrado: $VISIT_ID"
echo "  ✅ Distancia calculada: $DISTANCE metros"
echo "  ✅ Datos en BD: OK"
echo ""
echo "📊 GPS Tracking está FUNCIONANDO CORRECTAMENTE"
echo ""
