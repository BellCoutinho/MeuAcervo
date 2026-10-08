#!/bin/bash
# RF10 - Atualizar Produto
# Atualiza informações de um produto
source "$(dirname "$0")/common.sh"

print_header "RF10 - Atualizar Produto"

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
print_step "Estado ANTES da atualização"
RESULT_BEFORE=$(do_get "/api/product/$PRODUCT_ID" "$TOKEN")
BODY_BEFORE=$(get_body "$RESULT_BEFORE")
echo "   Nome: $(json_field "$BODY_BEFORE" "name")"
echo "   Valor: R\$ $(json_field "$BODY_BEFORE" "purchase_value")"
echo "   Serial: $(json_field "$BODY_BEFORE" "serial_number")"

echo ""
print_request "PUT /api/product/$PRODUCT_ID"
print_request "Dados: name=Geladeira Brastemp Inverter, purchase_value=3200.00, serial_number=BRM44HK2024001-REV1"

RESULT=$(curl -s -w $'\n%{http_code}' -X PUT "$BASE_URL/api/product/$PRODUCT_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "name": "Geladeira Brastemp Inverter",
        "purchase_value": 3200.00,
        "serial_number": "BRM44HK2024001-REV1"
    }')

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

# Consulta: buscar produto para confirmar atualização
print_step "Consulta: GET /api/product/$PRODUCT_ID (confirma atualização)"
RESULT2=$(do_get "/api/product/$PRODUCT_ID" "$TOKEN")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $(get_http_code "$RESULT2")"
echo "   Nome: $(json_field "$BODY2" "name")"
echo "   Valor: R\$ $(json_field "$BODY2" "purchase_value")"
echo "   Serial: $(json_field "$BODY2" "serial_number")"
