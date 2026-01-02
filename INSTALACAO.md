# Guia de Instalação - Servidor Ubuntu

## ⚡ Instalação Rápida (Recomendada)

Se você quer instalar tudo automaticamente:

```bash
# 1. Copie o projeto para o servidor
# 2. Entre no diretório do projeto
cd /caminho/do/projeto

# 3. Execute o script de instalação
bash install.sh

# 4. Edite o arquivo .env com suas credenciais
nano .env

# 5. Teste a instalação
bash test_install.sh
```

O script `install.sh` instala automaticamente:
- Xvfb
- Dependências do sistema
- Google Chrome
- Python e pip
- Dependências Python
- Navegadores Playwright

---

## 📋 Instalação Manual (Passo a Passo)

Se preferir instalar manualmente ou se o script falhar:

```bash
# Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Instalar Dependências do Sistema

```bash
# Xvfb (ambiente gráfico virtual)
sudo apt-get install -y xvfb

# Dependências do Playwright
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
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils
```

### 3. Instalar Chrome/Chromium

**Opção A: Google Chrome (Recomendado)**

```bash
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

**Opção B: Chromium**

```bash
sudo apt-get install -y chromium-browser
```

### 4. Instalar Python e pip

```bash
sudo apt-get install -y python3 python3-pip
```

### 5. Copiar Projeto para Servidor

```bash
# Via git, scp, ou copiar arquivos manualmente
# Exemplo:
scp -r projeto/ usuario@servidor:/home/usuario/tjsp-bot/
```

### 6. Instalar Dependências Python

```bash
cd /caminho/do/projeto
pip3 install -r requirements.txt
python3 -m playwright install chromium
python3 -m playwright install-deps chromium
```

### 7. Instalar Plugin WebSigner

1. Baixe o plugin do site oficial do TJSP
2. Instale no Chrome do servidor (pode precisar de acesso gráfico temporário ou usar VNC)
3. Verifique se plugin está ativo

### 8. Configurar Certificado A1

**Opção A: Importar no navegador (recomendado)**

```bash
# Via linha de comando (exemplo - ajuste conforme necessário)
certutil -d sql:$HOME/.pki/nssdb -A -t "P,," -n "Certificado A1" -i /caminho/certificado.pfx
```

**Opção B: Instalar no sistema**

Siga instruções do WebSigner para detectar certificados do sistema.

### 9. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
cd /caminho/do/projeto
nano .env
```

Conteúdo do `.env`:

```env
FACILITA_USER=seu_usuario
FACILITA_PASS=sua_senha
ACTION_DELAY=0.6
```

### 10. Testar Instalação

```bash
# Testa se Xvfb funciona
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
# Deve iniciar sem erros

# Testa se Chrome funciona
DISPLAY=:99 google-chrome --no-sandbox --version

# Testa o bot
cd /caminho/do/projeto
python3 main.py
```

### 11. Configurar como Serviço (Opcional)

Crie `/etc/systemd/system/tjsp-bot.service`:

```ini
[Unit]
Description=TJSP Bot - Automação Jurídica
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/do/projeto
Environment="DISPLAY=:99"
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /caminho/do/projeto/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Ativar serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tjsp-bot
sudo systemctl start tjsp-bot
sudo systemctl status tjsp-bot
```

### 12. Verificar Logs

```bash
# Se usando systemd
sudo journalctl -u tjsp-bot -f

# Se executando manualmente
tail -f /var/log/tjsp-bot.log
```

## Checklist Final

- [ ] Xvfb instalado e funcionando
- [ ] Chrome/Chromium instalado
- [ ] Plugin WebSigner instalado e ativo
- [ ] Certificado A1 configurado
- [ ] Dependências Python instaladas
- [ ] Navegadores Playwright instalados
- [ ] Arquivo .env configurado
- [ ] Teste manual funcionou
- [ ] Serviço configurado (opcional)

## Troubleshooting

Ver seção Troubleshooting no `README.md`.

