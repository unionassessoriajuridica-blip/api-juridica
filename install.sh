#!/bin/bash
# Script de Instalação Automatizada - TJSP Bot
# Execute com: bash install.sh

set -e  # Para se algum comando falhar

echo "=========================================="
echo "Instalação Automatizada - TJSP Bot"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para print colorido
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Verifica se está rodando como root quando necessário
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_warning "Alguns comandos precisam de sudo. Você pode precisar inserir sua senha."
    fi
}

# 1. Atualizar sistema
echo "[1/8] Atualizando sistema..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq
print_success "Sistema atualizado"

# 2. Instalar Xvfb
echo ""
echo "[2/8] Instalando Xvfb..."
if command -v Xvfb &> /dev/null; then
    print_success "Xvfb já está instalado"
else
    sudo apt-get install -y xvfb -qq
    print_success "Xvfb instalado"
fi

# 3. Instalar dependências do Playwright
echo ""
echo "[3/8] Instalando dependências do Playwright..."
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2t64 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    -qq
print_success "Dependências do Playwright instaladas"

# 4. Instalar Google Chrome
echo ""
echo "[4/8] Instalando Google Chrome..."
if command -v google-chrome &> /dev/null; then
    print_success "Google Chrome já está instalado"
else
    if [ ! -f /usr/share/keyrings/googlechrome-linux-keyring.gpg ]; then
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list > /dev/null
        sudo apt-get update -qq
    fi
    sudo apt-get install -y google-chrome-stable -qq
    print_success "Google Chrome instalado"
fi

# 5. Instalar Python e pip
echo ""
echo "[5/8] Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python encontrado: $PYTHON_VERSION"
else
    sudo apt-get install -y python3 python3-pip -qq
    print_success "Python instalado"
fi

if command -v pip3 &> /dev/null; then
    print_success "pip3 encontrado"
else
    sudo apt-get install -y python3-pip -qq
    print_success "pip3 instalado"
fi

# 6. Instalar dependências Python
echo ""
echo "[6/8] Instalando dependências Python..."
PROJECT_DIR=$(pwd)
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip3 install --user -r "$PROJECT_DIR/requirements.txt"
    print_success "Dependências Python instaladas"
else
    print_error "Arquivo requirements.txt não encontrado!"
    exit 1
fi

# 7. Instalar navegadores Playwright
echo ""
echo "[7/8] Instalando navegadores Playwright..."
python3 -m playwright install chromium
python3 -m playwright install-deps chromium
print_success "Navegadores Playwright instalados"

# 8. Criar arquivo .env se não existir
echo ""
echo "[8/8] Verificando configuração..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    print_warning "Arquivo .env não encontrado. Criando template..."
    cat > "$PROJECT_DIR/.env" << EOF
# Credenciais Facilita ADV
FACILITA_USER=seu_usuario_aqui
FACILITA_PASS=sua_senha_aqui

# Configurações do Bot
ACTION_DELAY=0.6
EOF
    print_warning "Arquivo .env criado. EDITE com suas credenciais!"
else
    print_success "Arquivo .env encontrado"
fi

# Resumo
echo ""
echo "=========================================="
echo "Instalação Concluída!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo .env com suas credenciais:"
echo "   nano .env"
echo ""
echo "2. Configure o certificado A1 no navegador"
echo "3. Instale o plugin WebSigner no Chrome"
echo "4. Teste a instalação:"
echo "   python3 main.py"
echo ""
echo "Para mais informações, consulte README.md"
echo ""

