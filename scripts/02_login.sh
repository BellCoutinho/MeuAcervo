#!/bin/bash
# RF01 - Login
# Autentica o usuário e retorna token JWT
source "$(dirname "$0")/common.sh"

print_header "RF01 - Login"

print_request "POST /api/auth/login"
print_request "Dados: email=$DEFAULT_EMAIL, password=******"

RESULT=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "'"$DEFAULT_EMAIL"'",
        "password": "'"$REGISTER_PASSWORD"'"
    }')

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

TOKEN=$(json_field "$BODY" "access_token")
ROLE=$(json_field "$BODY" "role")
USER_UID=$(json_field "$BODY" "uid")

echo ""
echo "   access_token: ${TOKEN:0:50}..."
echo "   uid: $USER_UID"
echo "   role: $ROLE"

# Consulta: usar token para buscar espaço (confirma que o token é válido)
print_step "Consulta: GET /api/space (confirma que o token é válido)"
RESULT2=$(do_get "/api/space" "$TOKEN")
HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"
