#!/bin/bash
# RF06 - Cadastrar Produto
# Cadastra um novo produto no espaço
source "$(dirname "$0")/common.sh"

print_header "RF06 - Cadastrar Produto"

# Login e obter space_id
print_step "Login e obter space_id"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi
SPACE_ID=$(get_space_id "$TOKEN")
echo "   ✓ space_id: $SPACE_ID"

echo ""
print_request "POST /api/product"
print_request "Dados: name=Geladeira Brastemp, category=eletrodomestico, brand=Brastemp, model=BRM44HK, purchase_value=2500.00"

RESULT=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/product" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "space_id": "'"$SPACE_ID"'",
        "name": "Geladeira Brastemp",
        "category": "eletrodomestico",
        "brand": "Brastemp",
        "model": "BRM44HK",
        "location": "Cozinha",
        "purchase_value": 2500.00,
        "purchase_date": "2024-01-15",
        "serial_number": "BRM44HK2024001",
        "warranty_type": "manufacturer",
        "warranty_expiry": "2027-01-15"
    }')

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

PRODUCT_ID=$(json_field "$BODY" "product_id")
echo ""
echo "   product_id: $PRODUCT_ID"
echo "   name: $(json_field "$BODY" "name")"
echo "   warranty: $(json_field "$BODY" "warranty_status")"

# Consulta: buscar o produto para confirmar cadastro
print_step "Consulta: GET /api/product/$PRODUCT_ID (confirma que o produto foi cadastrado)"
RESULT2=$(do_get "/api/product/$PRODUCT_ID" "$TOKEN")
HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"
