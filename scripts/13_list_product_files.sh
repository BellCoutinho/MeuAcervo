#!/bin/bash
# RF07 - Listar Arquivos do Produto
# Lista todos os arquivos anexados a um produto
source "$(dirname "$0")/common.sh"

print_header "RF07 - Listar Arquivos do Produto"

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

echo ""
print_request "GET /api/file/product/$PRODUCT_ID"

RESULT=$(do_get "/api/file/product/$PRODUCT_ID" "$TOKEN")
HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

COUNT=$(echo "$BODY" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo ""
echo "   Total de arquivos: $COUNT"
