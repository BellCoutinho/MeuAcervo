#!/bin/bash
# Executa todos os scripts de demonstração em ordem
# Uso: ./scripts/run_all.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================"
echo "  ProductControl API - Demonstração Completa"
echo "============================================"
echo ""
echo "Pré-requisitos:"
echo "  - App rodando em http://localhost:8000"
echo "  - Execute: podman-compose up --build -d"
echo ""

for script in "$SCRIPT_DIR"/[0-9]*.sh; do
    if [ -f "$script" ]; then
        bash "$script"
        echo ""
    fi
done

echo "============================================"
echo "  Demonstração concluída!"
echo "============================================"
