#!/bin/bash
# Script de Teste - Verifica se tudo está instalado corretamente

echo "=========================================="
echo "Teste de Instalação - TJSP Bot"
echo "=========================================="
echo ""

ERRORS=0

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 está instalado"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NÃO está instalado"
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 existe"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NÃO existe"
        return 1
    fi
}

# Testa comandos essenciais
echo "Verificando comandos instalados..."
check_command python3 || ((ERRORS++))
check_command pip3 || ((ERRORS++))
check_command Xvfb || ((ERRORS++))
check_command google-chrome || check_command chromium-browser || ((ERRORS++))

echo ""
echo "Verificando arquivos do projeto..."
check_file main.py || ((ERRORS++))
check_file config.py || ((ERRORS++))
check_file requirements.txt || ((ERRORS++))
check_file bots/tjsp_bot_vm.py || ((ERRORS++))

echo ""
echo "Testando Xvfb..."
export DISPLAY=:99
if Xvfb :99 -screen 0 1920x1080x24 -ac &
then
    XVFB_PID=$!
    sleep 2
    if kill -0 $XVFB_PID 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Xvfb funciona corretamente"
        kill $XVFB_PID 2>/dev/null
    else
        echo -e "${RED}✗${NC} Xvfb não iniciou corretamente"
        ((ERRORS++))
    fi
else
    echo -e "${RED}✗${NC} Erro ao iniciar Xvfb"
    ((ERRORS++))
fi

echo ""
echo "Testando Python e dependências..."
if python3 -c "import playwright" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Playwright está instalado"
else
    echo -e "${RED}✗${NC} Playwright NÃO está instalado (execute: pip3 install playwright)"
    ((ERRORS++))
fi

if python3 -c "import dotenv" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} python-dotenv está instalado"
else
    echo -e "${RED}✗${NC} python-dotenv NÃO está instalado"
    ((ERRORS++))
fi

echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}Todos os testes passaram!${NC}"
    echo ""
    echo "Próximo passo: Configure o arquivo .env e teste com:"
    echo "  python3 main.py"
    exit 0
else
    echo -e "${RED}Encontrados $ERRORS erro(s)${NC}"
    echo ""
    echo "Execute o script de instalação:"
    echo "  bash install.sh"
    exit 1
fi

