#!/bin/bash

# 🛰️ Verificación Rápida de GPS Tracking
# Usa este script para verificar que GPS está funcionando

echo "🛰️  VERIFICACIÓN RÁPIDA DE GPS"
echo "=============================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="${API_URL:-http://localhost:8000}"

echo -e "${BLUE}📋 CHECKLIST RÁPIDA:${NC}"
echo ""

# 1. Verificar API
echo -n "1️⃣  API accesible en $API_URL... "
if curl -s "$API_URL/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    echo -e "${YELLOW}   → ¿El backend está corriendo?${NC}"
    exit 1
fi

# 2. Verificar cliente de prueba
echo -n "2️⃣  Creando cliente de prueba... "
CLIENT_RESP=$(curl -s -X POST "$API_URL/clients/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test GPS",
    "address": "Test",
    "phone": "123",
    "client_type": "carpenter",
    "status": "active",
    "latitude": 40.4168,
    "longitude": -3.7038
  }')

CLIENT_ID=$(echo "$CLIENT_RESP" | jq -r '.id' 2>/dev/null)
if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "null" ]; then
    echo -e "${RED}❌${NC}"
    exit 1
fi
echo -e "${GREEN}✅${NC}"

# 3. Verificar seller (usar email único para evitar conflicto)
echo -n "3️⃣  Creando vendedor de prueba... "
SELLER_EMAIL="test+$(date +%s)@test.test"
SELLER_RESP=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_URL/sellers/" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Test Seller\", \"email\": \"$SELLER_EMAIL\", \"phone\": \"456\", \"is_active\": true }")

# Extraer JSON body (antes de la línea HTTP_STATUS)
HTTP_STATUS=$(echo "$SELLER_RESP" | tr '\n' ' ' | sed -E 's/.*HTTP_STATUS:([0-9]{3})/\1/')
HTTP_STATUS=$(echo "$HTTP_STATUS" | tr -d '[:space:]')
SELLER_BODY=$(echo "$SELLER_RESP" | sed -E 's/\n?HTTP_STATUS:[0-9]{3}//')

SELLER_ID=$(echo "$SELLER_BODY" | jq -r '.id' 2>/dev/null)
if [ "$HTTP_STATUS" != "200" ] || [ -z "$SELLER_ID" ] || [ "$SELLER_ID" = "null" ]; then
    echo -e "${RED}❌ (status=$HTTP_STATUS)${NC}"
    echo "$SELLER_BODY" | jq . || echo "$SELLER_BODY"
    exit 1
fi
echo -e "${GREEN}✅ (email=$SELLER_EMAIL)${NC}"

# 4. Verificar ruta
echo -n "4️⃣  Creando ruta de prueba... "
ROUTE_RESP=$(curl -s -X POST "$API_URL/routes/" \
  -H "Content-Type: application/json" \
  -d "{
    \"seller_id\": \"$SELLER_ID\",
    \"client_id\": \"$CLIENT_ID\",
    \"planned_date\": \"2025-12-11T10:00:00\"
  }")

ROUTE_ID=$(echo "$ROUTE_RESP" | jq -r '.id' 2>/dev/null)
if [ -z "$ROUTE_ID" ] || [ "$ROUTE_ID" = "null" ]; then
    echo -e "${RED}❌${NC}"
    exit 1
fi
echo -e "${GREEN}✅${NC}"

# 5. Verificar check-in GPS
echo -n "5️⃣  Probando check-in con GPS... "
CHECKIN_RESP=$(curl -s -X POST "$API_URL/visits/checkin/" \
  -H "Content-Type: application/json" \
  -d "{
    \"route_id\": \"$ROUTE_ID\",
    \"seller_id\": \"$SELLER_ID\",
    \"client_id\": \"$CLIENT_ID\",
    \"latitude\": 40.4168,
    \"longitude\": -3.7038,
    \"client_found\": true,
    \"notes\": \"Test\"
  }")

CHECKIN_PAYLOAD=$(cat <<EOF
{\
  "route_id": "${ROUTE_ID}",\
  "seller_id": "${SELLER_ID}",\
  "client_id": "${CLIENT_ID}",\
  "latitude": 40.4168,\
  "longitude": -3.7038,\
  "client_found": true,\
  "notes": "Test"\
}
EOF
)

CHECKIN_RESP=$(curl -s -X POST "$API_URL/visits/checkin/" \
  -F "request_form=$CHECKIN_PAYLOAD" )
VISIT_ID=$(echo "$CHECKIN_RESP" | jq -r '.visit_id' 2>/dev/null)
DISTANCE=$(echo "$CHECKIN_RESP" | jq -r '.distance_meters' 2>/dev/null)
IS_VALID=$(echo "$CHECKIN_RESP" | jq -r '.is_valid' 2>/dev/null)

if [ -z "$VISIT_ID" ] || [ "$VISIT_ID" = "null" ]; then
    echo -e "${RED}❌${NC}"
    echo "$CHECKIN_RESP" | jq .
    exit 1
fi
echo -e "${GREEN}✅${NC}"

echo ""
echo -e "${BLUE}📊 RESULTADOS:${NC}"
echo "  • Distancia: $DISTANCE metros"
echo "  • Válido: $IS_VALID"
echo "  • Visit ID: $VISIT_ID"
echo ""
echo -e "${GREEN}🎉 GPS FUNCIONA CORRECTAMENTE${NC}"
echo ""
echo "PRÓXIMO PASO: Prueba en el móvil"
echo "  1. Abre DevTools en móvil (F12)"
echo "  2. Ve a Check-in"
echo "  3. Haz click en 'Capturar GPS'"
echo "  4. Mira los logs en la consola"
echo ""
