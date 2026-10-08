#!/bin/bash
# RF01 - Alterar Senha
# Usuário logado altera a própria senha
source "$(dirname "$0")/common.sh"

print_header "RF01 - Alterar Senha"

# Login com senha atual (RESET_PASSWORD definido no script 04)
print_step "Login com senha atual ($RESET_PASSWORD)"
TOKEN=$(ensure_login "$RESET_PASSWORD")
if [ $? -ne 0 ]; then
    exit 1
fi
echo "   ✓ Token obtido"

echo ""
print_request "PATCH /api/auth/change-password"
print_request "Dados: current_password=******, new_password=******"

RESULT=$(curl -s -w $'\n%{http_code}' -X PATCH "$BASE_URL/api/auth/change-password" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "current_password": "'"$RESET_PASSWORD"'",
        "new_password": "'"$FINAL_PASSWORD"'"
    }')

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

# Consulta: login com a nova senha
print_step "Consulta: Login com a nova senha $FINAL_PASSWORD (confirma alteração)"
RESULT2=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "'"$DEFAULT_EMAIL"'",
        "password": "'"$FINAL_PASSWORD"'"
    }')

HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"

TOKEN2=$(json_field "$BODY2" "access_token")
if [ -n "$TOKEN2" ]; then
    echo ""
    echo "   ✓ Login com nova senha ($FINAL_PASSWORD) funcionou!"
fi
