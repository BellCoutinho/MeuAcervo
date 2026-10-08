#!/bin/bash
# RF01 - Redefinir Senha
# Usa o token de reset para definir nova senha
source "$(dirname "$0")/common.sh"

print_header "RF01 - Redefinir Senha"

# Passo 1: obter token de reset
print_step "Passo 1: Solicitar token de reset"
RESULT=$(curl -s -X POST "$BASE_URL/api/auth/forgot-password" \
    -H "Content-Type: application/json" \
    -d '{"email": "'"$DEFAULT_EMAIL"'"}')
RESET_TOKEN=$(json_field "$RESULT" "reset_token")
echo "   reset_token: $RESET_TOKEN"

# Passo 2: redefinir senha
echo ""
print_step "Passo 2: Redefinir senha com o token"

print_request "POST /api/auth/reset-password"
print_request "Dados: token=$RESET_TOKEN, new_password=******"

RESULT=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/auth/reset-password" \
    -H "Content-Type: application/json" \
    -d '{
        "token": "'"$RESET_TOKEN"'",
        "new_password": "'"$RESET_PASSWORD"'"
    }')

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

# Consulta: login com a nova senha
print_step "Consulta: Login com a nova senha $RESET_PASSWORD (confirma redefinição)"
RESULT2=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "'"$DEFAULT_EMAIL"'",
        "password": "'"$RESET_PASSWORD"'"
    }')

HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"

TOKEN=$(json_field "$BODY2" "access_token")
if [ -n "$TOKEN" ]; then
    echo ""
    echo "   ✓ Login com nova senha ($RESET_PASSWORD) funcionou!"
fi
