#!/bin/bash
# RF10 - Desativar Produto (Descarte)
# Desativa um produto especificando o motivo
source "$(dirname "$0")/common.sh"

print_header "RF10 - Desativar Produto"

# Login
print_step "Login"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi

SPACE_ID=$(get_space_id "$TOKEN")
echo "   ✓ space_id: $SPACE_ID"

# Garantir que existe um produto
print_step "Buscar ou criar produto"
PRODUCT_ID=$(ensure_product "$TOKEN" "$SPACE_ID")
echo "   ✓ product_id: $PRODUCT_ID"

# Estado antes
print_step "Estado ANTES da desativação"
RESULT_BEFORE=$(do_get "/api/product/$PRODUCT_ID" "$TOKEN")
BODY_BEFORE=$(get_body "$RESULT_BEFORE")
echo "   Nome: $(json_field "$BODY_BEFORE" "name")"
echo "   Status: $(json_field "$BODY_BEFORE" "status")"

echo ""
print_request "PATCH /api/product/$PRODUCT_ID/deactivate"
print_request "Dados: reason=descarte"

RESULT=$(curl -s -w $'\n%{http_code}' -X PATCH "$BASE_URL/api/product/$PRODUCT_ID/deactivate" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"reason": "descarte"}')

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

# Consulta: buscar produto para confirmar desativação
print_step "Consulta: GET /api/product/$PRODUCT_ID (confirma desativação)"
RESULT2=$(do_get "/api/product/$PRODUCT_ID" "$TOKEN")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $(get_http_code "$RESULT2")"
echo "   Nome: $(json_field "$BODY2" "name")"
echo "   Status: $(json_field "$BODY2" "status")"
echo "   Motivo: $(json_field "$BODY2" "status_reason")"
