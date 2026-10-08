#!/bin/bash
# RF01 - Esqueci Minha Senha
# Solicita um token de redefinição de senha
source "$(dirname "$0")/common.sh"

print_header "RF01 - Esqueci Minha Senha"

print_request "POST /api/auth/forgot-password"
print_request "Dados: email=$DEFAULT_EMAIL"

RESULT=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/auth/forgot-password" \
    -H "Content-Type: application/json" \
    -d '{"email": "'"$DEFAULT_EMAIL"'"}')

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

RESET_TOKEN=$(json_field "$BODY" "reset_token")
echo ""
echo "   reset_token: $RESET_TOKEN"
