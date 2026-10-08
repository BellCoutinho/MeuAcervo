#!/bin/bash
# Configuração compartilhada para todos os scripts de demonstração

export BASE_URL="http://localhost:8000"

# Cores
export GREEN='\033[0;32m'
export CYAN='\033[0;36m'
export YELLOW='\033[1;33m'
export RED='\033[0;31m'
export NC='\033[0m'

# Credenciais
export DEFAULT_EMAIL="joao.silva@email.com"
export REGISTER_PASSWORD="Senha@123"
export RESET_PASSWORD="NovaSenha@456"
export FINAL_PASSWORD="SenhaFinal@789"

# ============================================================
# Funções de output
# ============================================================
print_header() {
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}============================================${NC}"
}

print_step() {
    echo -e "${YELLOW}>> $1${NC}"
}

print_ok() {
    echo -e "${GREEN}   ✓ OK${NC}"
}

print_fail() {
    echo -e "${RED}   ✗ FALHA: $1${NC}"
}

print_request() {
    echo -e "${YELLOW}   [REQUEST] $1${NC}"
}

print_response() {
    echo -e "${GREEN}   [RESPONSE] $1${NC}"
}

# ============================================================
# Funções HTTP
# ============================================================
do_get() {
    local path="$1"
    local token="$2"
    if [ -n "$token" ]; then
        curl -s -w $'\n%{http_code}' -X GET "$BASE_URL$path" \
            -H "Authorization: Bearer $token"
    else
        curl -s -w $'\n%{http_code}' -X GET "$BASE_URL$path"
    fi
}

do_put() {
    local path="$1"
    local data="$2"
    local token="$3"
    if [ -n "$token" ]; then
        curl -s -w $'\n%{http_code}' -X PUT "$BASE_URL$path" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data"
    else
        curl -s -w $'\n%{http_code}' -X PUT "$BASE_URL$path" \
            -H "Content-Type: application/json" \
            -d "$data"
    fi
}

do_patch() {
    local path="$1"
    local data="$2"
    local token="$3"
    if [ -n "$data" ]; then
        if [ -n "$token" ]; then
            curl -s -w $'\n%{http_code}' -X PATCH "$BASE_URL$path" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $token" \
                -d "$data"
        else
            curl -s -w $'\n%{http_code}' -X PATCH "$BASE_URL$path" \
                -H "Content-Type: application/json" \
                -d "$data"
        fi
    else
        if [ -n "$token" ]; then
            curl -s -w $'\n%{http_code}' -X PATCH "$BASE_URL$path" \
                -H "Authorization: Bearer $token"
        else
            curl -s -w $'\n%{http_code}' -X PATCH "$BASE_URL$path"
        fi
    fi
}

do_delete() {
    local path="$1"
    local token="$2"
    if [ -n "$token" ]; then
        curl -s -w $'\n%{http_code}' -X DELETE "$BASE_URL$path" \
            -H "Authorization: Bearer $token"
    else
        curl -s -w $'\n%{http_code}' -X DELETE "$BASE_URL$path"
    fi
}

# ============================================================
# Funções de parse
# ============================================================
get_http_code() {
    echo "$1" | tail -1
}

get_body() {
    echo "$1" | sed '$d'
}

json_pretty() {
    echo "$1" | python3 -m json.tool 2>/dev/null || echo "$1"
}

json_field() {
    echo "$1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('$2',''))" 2>/dev/null || echo ""
}

check_http() {
    local code="$1"
    local expected="$2"
    if [ "$code" = "$expected" ]; then
        print_ok
        return 0
    else
        print_fail "HTTP $code (esperado $expected)"
        return 1
    fi
}

# ============================================================
# Helpers de estado
# ============================================================

# Login e retorna token. Uso: ensure_login [senha]
ensure_login() {
    local password="${1:-$FINAL_PASSWORD}"
    local result
    result=$(curl -s -X POST "$BASE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$DEFAULT_EMAIL\", \"password\": \"$password\"}")
    local token
    token=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
    if [ -z "$token" ]; then
        print_fail "Login falhou"
        return 1
    fi
    echo "$token"
}

# Obtém space_id do usuário logado. Uso: get_space_id <token>
get_space_id() {
    local token="$1"
    local result
    result=$(do_get "/api/space" "$token")
    local body
    body=$(get_body "$result")
    json_field "$body" "space_id"
}

# Busca primeiro produto ou cria um se não existir. Uso: ensure_product <token> <space_id>
ensure_product() {
    local token="$1"
    local space_id="$2"

    # Buscar produto existente
    local result
    result=$(do_get "/api/product/search?space_id=$space_id" "$token")
    local body
    body=$(get_body "$result")
    local product_id
    product_id=$(echo "$body" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if isinstance(data, list) and len(data) > 0:
    print(data[0].get('product_id',''))
else:
    print('')
" 2>/dev/null)

    if [ -n "$product_id" ]; then
        echo "$product_id"
        return 0
    fi

    # Criar produto se não existe
    result=$(curl -s -w $'\n%{http_code}' -X POST "$BASE_URL/api/product" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $token" \
        -d '{
            "space_id": "'"$space_id"'",
            "name": "Geladeira Brastemp",
            "category": "eletrodomestico",
            "brand": "Brastemp",
            "model": "BRM44HK",
            "location": "Cozinha",
            "purchase_value": 2500.00,
            "serial_number": "BRM44HK2024001",
            "warranty_type": "manufacturer",
            "warranty_expiry": "2027-01-15"
        }')
    body=$(get_body "$result")
    product_id=$(json_field "$body" "product_id")
    echo "$product_id"
}

# Convida e aprova um usuário temporário. Retorna user_id.
# Uso: create_temp_user <token> <space_id> <email> <name>
create_temp_user() {
    local token="$1"
    local space_id="$2"
    local email="$3"
    local name="$4"

    local result
    result=$(curl -s -X POST "$BASE_URL/api/user/invite" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $token" \
        -d '{
            "space_id": "'"$space_id"'",
            "first_name": "'"$name"'",
            "last_name": "Temp",
            "email": "'"$email"'",
            "password": "SenhaTemp@123"
        }')
    local user_id
    user_id=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('user_id',''))" 2>/dev/null)

    if [ -n "$user_id" ]; then
        curl -s -X POST "$BASE_URL/api/user/approve/$user_id" \
            -H "Authorization: Bearer $token" > /dev/null
    fi

    echo "$user_id"
}
