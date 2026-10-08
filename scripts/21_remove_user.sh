#!/bin/bash
# RF03 - Remover Usuário
# Admin remove um usuário do espaço
source "$(dirname "$0")/common.sh"

print_header "RF03 - Remover Usuário"

# Login
print_step "Login"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi

SPACE_ID=$(get_space_id "$TOKEN")
echo "   ✓ space_id: $SPACE_ID"

# Criar usuário temporário para remover
print_step "Convidar e aprovar usuário temporário"
USER_ID=$(create_temp_user "$TOKEN" "$SPACE_ID" "teste.remover@email.com" "Remover")
if [ -z "$USER_ID" ]; then
    print_fail "Não foi possível criar usuário temporário"
    exit 1
fi
echo "   ✓ user_id: $USER_ID (Remover Temp)"

# Estado antes
print_step "Estado ANTES da remoção"
RESULT_BEFORE=$(do_get "/api/user/all" "$TOKEN")
BODY_BEFORE=$(get_body "$RESULT_BEFORE")
COUNT_BEFORE=$(echo "$BODY_BEFORE" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo "   Total de usuários: $COUNT_BEFORE"

echo ""
print_request "DELETE /api/user/$USER_ID"
print_request "Removendo: Remover Temp (user_id: $USER_ID)"

RESULT=$(curl -s -w $'\n%{http_code}' -X DELETE "$BASE_URL/api/user/$USER_ID" \
    -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

# Consulta: listar usuários para confirmar remoção
print_step "Consulta: GET /api/user/all (confirma que Remover Temp foi removido)"
RESULT2=$(do_get "/api/user/all" "$TOKEN")
HTTP_CODE2=$(get_http_code "$RESULT2")
BODY2=$(get_body "$RESULT2")
print_response "HTTP $HTTP_CODE2"
json_pretty "$BODY2"

COUNT_AFTER=$(echo "$BODY2" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo ""
echo "   Usuários antes: $COUNT_BEFORE, depois: $COUNT_AFTER"
