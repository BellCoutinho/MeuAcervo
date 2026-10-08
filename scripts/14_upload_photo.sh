#!/bin/bash
# RF07 - Upload de Foto
# Envia uma foto do produto
source "$(dirname "$0")/common.sh"

print_header "RF07 - Upload de Foto"

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

# Criar arquivo temporário
echo "fake-photo-content" > /tmp/teste_foto.jpg

echo ""
print_request "POST /api/file/upload/$PRODUCT_ID"
print_request "Arquivo: /tmp/teste_foto.jpg"

RESULT=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/file/upload/$PRODUCT_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@/tmp/teste_foto.jpg")

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

# Consulta: listar arquivos para confirmar
print_step "Consulta: GET /api/file/product/$PRODUCT_ID (confirma upload da foto)"
RESULT2=$(do_get "/api/file/product/$PRODUCT_ID" "$TOKEN")
HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"
