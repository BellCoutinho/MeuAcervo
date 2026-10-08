#!/bin/bash
# RF04 - Informação de Armazenamento
# Admin consulta o consumo de armazenamento do espaço
source "$(dirname "$0")/common.sh"

print_header "RF04 - Informação de Armazenamento"

# Login
print_step "Login"
TOKEN=$(ensure_login)
if [ $? -ne 0 ]; then exit 1; fi
echo "   ✓ Token obtido"

echo ""
print_request "GET /api/space/storage-info"

RESULT=$(do_get "/api/space/storage-info" "$TOKEN")
HTTP_CODE=$(get_http_code "$RESULT")
BODY=$(get_body "$RESULT")

print_response "HTTP $HTTP_CODE"
json_pretty "$BODY"

echo ""
echo "   Espaço total: $(json_field "$BODY" "storage_quota") bytes"
echo "   Espaço usado: $(json_field "$BODY" "total_used") bytes"
