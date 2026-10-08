#!/bin/bash
# RF01 - Cadastro de Usuário
# Cadastra um novo usuário (admin) com espaço próprio
source "$(dirname "$0")/common.sh"

print_header "RF01 - Cadastro de Usuário"

EMAIL="joao.silva@email.com"
PASSWORD="Senha@123"

print_request "POST /api/auth/register"
print_request "Dados: first_name=Joao, last_name=Silva, email=$EMAIL, space_name=Minha Casa"

RESULT=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "first_name": "Joao",
        "last_name": "Silva",
        "email": "'"$EMAIL"'",
        "password": "'"$PASSWORD"'",
        "space_name": "Minha Casa",
        "space_address": "Rua A, 123 - Sao Paulo",
        "utility_unit_number": "UT-001"
    }')

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

USER_ID=$(json_field "$BODY" "user_id")
SPACE_ID=$(json_field "$BODY" "space_id")

echo ""
echo "   user_id:  $USER_ID"
echo "   space_id: $SPACE_ID"

# Consulta: buscar espaço para confirmar cadastro
print_step "Consulta: GET /api/space (confirma que o usuário e espaço foram criados)"
TOKEN=$(do_login "$EMAIL" "$PASSWORD")
RESULT2=$(do_get "/api/space" "$TOKEN")
HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"
