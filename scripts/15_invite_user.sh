#!/bin/bash
# RF03 - Convidar Novo Usuário
# Admin convida um novo membro para o espaço
source "$(dirname "$0")/common.sh"

print_header "RF03 - Convidar Novo Usuário"

# Login e obter space_id
print_step "Login e obter space_id"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi
SPACE_ID=$(get_space_id "$TOKEN")
echo "   ✓ space_id: $SPACE_ID"

echo ""
print_request "POST /api/user/invite"
print_request "Dados: first_name=Maria, last_name=Santos, email=maria.santos@email.com"

RESULT=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/user/invite" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "space_id": "'"$SPACE_ID"'",
        "first_name": "Maria",
        "last_name": "Santos",
        "email": "maria.santos@email.com",
        "password": "SenhaMaria@123"
    }')

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

INVITED_USER_ID=$(json_field "$BODY" "user_id")
echo ""
echo "   user_id: $INVITED_USER_ID"
echo "   name: Maria Santos"
echo "   email: maria.santos@email.com"
echo "   status: $(json_field "$BODY" "status")"

# Consulta: listar usuários para confirmar convite
print_step "Consulta: GET /api/user/all (confirma que Maria Santos foi convidada)"
RESULT2=$(do_get "/api/user/all" "$TOKEN")
HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"
