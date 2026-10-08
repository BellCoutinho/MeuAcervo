#!/bin/bash
# RF03 - Aprovar Usuário
# Admin aprova um usuário pendente
source "$(dirname "$0")/common.sh"

print_header "RF03 - Aprovar Usuário"

# Login
print_step "Login"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi

SPACE_ID=$(get_space_id "$TOKEN")
echo "   ✓ space_id: $SPACE_ID"

# Criar usuário temporário para aprovar
print_step "Convidar usuário temporário para teste"
USER_ID=$(create_temp_user "$TOKEN" "$SPACE_ID" "teste.aprovar@email.com" "Aprovar")
if [ -z "$USER_ID" ]; then
    print_fail "Não foi possível criar usuário temporário"
    exit 1
fi
echo "   ✓ user_id: $USER_ID"

echo ""
print_request "POST /api/user/approve/$USER_ID"

RESULT=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/user/approve/$USER_ID" \
    -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

# Consulta: listar usuários para confirmar aprovação
print_step "Consulta: GET /api/user/all (confirma aprovação de Aprovar Temp)"
RESULT2=$(do_get "/api/user/all" "$TOKEN")
HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"
