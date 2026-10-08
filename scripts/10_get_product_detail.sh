#!/bin/bash
# RF08 - Detalhes do Produto (com Garantia)
# Busca detalhes completos de um produto
source "$(dirname "$0")/common.sh"

print_header "RF08 - Detalhes do Produto"

# Login
print_step "Login"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi

# Obter space_id
SPACE_ID=$(get_space_id "$TOKEN")
echo "   ✓ space_id: $SPACE_ID"

# Garantir que existe um produto
print_step "Buscar ou criar produto"
PRODUCT_ID=$(ensure_product "$TOKEN" "$SPACE_ID")
echo "   ✓ product_id: $PRODUCT_ID"

echo ""
print_request "GET /api/product/$PRODUCT_ID"

RESULT=$(do_get "/api/product/$PRODUCT_ID" "$TOKEN")
HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

echo ""
echo "   Nome: $(json_field "$BODY" "name")"
echo "   Marca: $(json_field "$BODY" "brand")"
echo "   Modelo: $(json_field "$BODY" "model")"
echo "   Valor: R\$ $(json_field "$BODY" "purchase_value")"
echo "   Garantia: $(json_field "$BODY" "warranty_status")"
echo "   Status: $(json_field "$BODY" "status")"
