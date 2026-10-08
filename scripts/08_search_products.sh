#!/bin/bash
# RF09 - Buscar Produtos
# Lista todos os produtos do espaço
source "$(dirname "$0")/common.sh"

print_header "RF09 - Buscar Produtos"

# Login e obter space_id
print_step "Login e obter space_id"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi
SPACE_ID=$(get_space_id "$TOKEN")
echo "   ✓ space_id: $SPACE_ID"

echo ""
print_request "GET /api/product/search?space_id=$SPACE_ID"

RESULT=$(do_get "/api/product/search?space_id=$SPACE_ID" "$TOKEN")
HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

COUNT=$(echo "$BODY" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo ""
echo "   Total de produtos encontrados: $COUNT"
