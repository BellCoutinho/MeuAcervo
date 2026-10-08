#!/bin/bash
# RF03 - Listar Todos os Usuários
# Lista todos os usuários do espaço
source "$(dirname "$0")/common.sh"

print_header "RF03 - Listar Todos os Usuários"

# Login
print_step "Login"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi
echo "   ✓ Token obtido"

echo ""
print_request "GET /api/user/all"

RESULT=$(do_get "/api/user/all" "$TOKEN")
HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

COUNT=$(echo "$BODY" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo ""
echo "   Total de usuários: $COUNT"
