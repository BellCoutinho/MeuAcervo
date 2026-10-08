#!/bin/bash
# RF07 - Upload de Arquivo (Nota Fiscal)
# Envia um arquivo PDF como nota fiscal do produto
source "$(dirname "$0")/common.sh"

print_header "RF07 - Upload de Nota Fiscal"

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
echo "NF-0012345 - Geladeira Brastemp - R\$ 2500,00" > /tmp/teste_nf.pdf

echo ""
print_request "POST /api/file/upload/$PRODUCT_ID"
print_request "Arquivo: /tmp/teste_nf.pdf"

RESULT=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/file/upload/$PRODUCT_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@/tmp/teste_nf.pdf")

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

FILE_ID=$(json_field "$BODY" "file_id")
echo ""
echo "   file_id: $FILE_ID"

# Consulta: listar arquivos para confirmar upload
print_step "Consulta: GET /api/file/product/$PRODUCT_ID (confirma upload)"
RESULT2=$(do_get "/api/file/product/$PRODUCT_ID" "$TOKEN")
HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"
