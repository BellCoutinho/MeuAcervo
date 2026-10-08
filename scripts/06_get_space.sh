#!/bin/bash
# RF02 - Verificar Perfil Admin
# Busca informações do espaço (requer autenticação)
source "$(dirname "$0")/common.sh"

print_header "RF02 - Verificar Perfil Admin"

# Login
print_step "Login"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi
echo "   ✓ Token obtido"

echo ""
print_request "GET /api/space"
print_request "Headers: Authorization: Bearer <token>"

RESULT=$(do_get "/api/space" "$TOKEN")
HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

SPACE_ID=$(json_field "$BODY" "space_id")
echo ""
echo "   space_id: $SPACE_ID"
echo "   name: $(json_field "$BODY" "name")"
echo "   address: $(json_field "$BODY" "address")"
echo "   utility_unit_number: $(json_field "$BODY" "utility_unit_number")"
echo "   storage_quota: $(json_field "$BODY" "storage_quota") bytes"
