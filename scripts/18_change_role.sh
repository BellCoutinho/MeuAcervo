#!/bin/bash
# RF03 - Alterar Perfil de Usuário
# Admin altera o perfil de um usuário (user ↔ admin)
source "$(dirname "$0")/common.sh"

print_header "RF03 - Alterar Perfil de Usuário"

# Login
print_step "Login"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi

SPACE_ID=$(get_space_id "$TOKEN")
echo "   ✓ space_id: $SPACE_ID"

# Criar usuário temporário
print_step "Convidar e aprovar usuário temporário"
USER_ID=$(create_temp_user "$TOKEN" "$SPACE_ID" "teste.role@email.com" "Role")
if [ -z "$USER_ID" ]; then
    print_fail "Não foi possível criar usuário temporário"
    exit 1
fi
echo "   ✓ user_id: $USER_ID"

echo ""
print_request "PATCH /api/user/$USER_ID/role"
print_request "Dados: new_role=admin"

RESULT=$(curl -s -w $'\n%{http_code}' -X PATCH "$BASE_URL/api/user/$USER_ID/role" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"new_role": "admin"}')

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

# Consulta: listar usuários para confirmar mudança de perfil
print_step "Consulta: GET /api/user/all (confirma que Role Temp agora é admin)"
RESULT2=$(do_get "/api/user/all" "$TOKEN")
HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"
