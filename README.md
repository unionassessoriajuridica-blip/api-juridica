# Robô de Automação Jurídica - e-SAJ para Facilita ADV

Automação que busca movimentações de processos no e-SAJ do TJSP e atualiza no sistema Facilita ADV.

## Requisitos

- **Python 3.8+**
- **Ubuntu Server** (recomendado) ou Linux com Xvfb
- **Certificado Digital A1** instalado no sistema
- **Plugin WebSigner** instalado no Chrome/Chromium

## Instalação no Servidor Ubuntu

### ⚡ Instalação Automatizada (Recomendada)

```bash
# Execute o script de instalação
bash install.sh

# Edite o arquivo .env com suas credenciais
nano .env

# Teste a instalação
bash test_install.sh
```

O script instala tudo automaticamente. Veja `INSTALACAO.md` para detalhes.

### 📋 Instalação Manual

Se preferir instalar manualmente:

```bash
# Atualiza pacotes
sudo apt-get update

# Instala Xvfb (ambiente gráfico virtual)
sudo apt-get install -y xvfb

# Instala dependências do Playwright
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
    libasound2
```

### 2. Instalar Chrome/Chromium

```bash
# Opção 1: Chromium (mais leve)
sudo apt-get install -y chromium-browser

# Opção 2: Google Chrome (recomendado para WebSigner)
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

### 3. Instalar Plugin WebSigner

1. Baixe o plugin WebSigner do site oficial do TJSP
2. Instale no Chrome/Chromium do servidor
3. Configure conforme instruções do plugin

### 4. Configurar Certificado A1

**Opção A: Importar certificado .pfx/.p12 no navegador**

```bash
# Via linha de comando (exemplo)
certutil -d sql:$HOME/.pki/nssdb -A -t "P,," -n "Seu Certificado" -i /caminho/para/certificado.pfx
```

**Opção B: Instalar certificado no sistema e usar via plugin**

Siga as instruções do WebSigner para detectar certificados instalados no sistema.

### 5. Instalar Dependências Python

```bash
# Clone ou copie o projeto para o servidor
cd /caminho/do/projeto

# Instala dependências Python
pip3 install -r requirements.txt

# Instala navegadores do Playwright
python3 -m playwright install chromium
python3 -m playwright install-deps chromium
```

### 6. Configurar Variáveis de Ambiente

Crie arquivo `.env` na raiz do projeto:

```env
# Facilita ADV
FACILITA_USER=seu_usuario
FACILITA_PASS=sua_senha

# TJSP (URLs padrão, normalmente não precisa alterar)
TJSP_MODE=real
HEADLESS=False
ACTION_DELAY=0.6
```

## Uso

### Executar Manualmente

```bash
python3 main.py
```

### Executar como Serviço (systemd)

1. Crie arquivo `/etc/systemd/system/tjsp-bot.service`:

```ini
[Unit]
Description=TJSP Bot - Automação Jurídica
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/do/projeto
Environment="DISPLAY=:99"
ExecStart=/usr/bin/python3 /caminho/do/projeto/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. Habilite e inicie o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tjsp-bot
sudo systemctl start tjsp-bot
sudo systemctl status tjsp-bot
```

### Agendar Execução (Cron)

```bash
# Edita crontab
crontab -e

# Executa a cada hora, por exemplo
0 * * * * cd /caminho/do/projeto && /usr/bin/python3 main.py >> /var/log/tjsp-bot.log 2>&1
```

## Estrutura do Projeto

```
.
├── main.py                 # Script principal
├── config.py               # Configurações
├── requirements.txt        # Dependências Python
├── bots/
│   ├── tjsp_bot_vm.py     # Bot do e-SAJ (usa Xvfb)
│   └── facilita_bot.py    # Bot do Facilita ADV
└── docker/                 # Arquivos Docker (opcional)
    ├── Dockerfile
    ├── docker-compose.yml
    └── entrypoint.sh
```

## Como Funciona

1. **Xvfb** cria um ambiente gráfico virtual (display :99)
2. **Chrome/Chromium** roda no ambiente virtual (headless=False)
3. **WebSigner** detecta certificado e faz login automaticamente
4. **Playwright** controla navegador e extrai dados
5. **Facilita Bot** atualiza informações no sistema destino

## Troubleshooting

### Xvfb não inicia

```bash
# Verifica se está instalado
which Xvfb

# Verifica se porta está em uso
lsof -i :99

# Mata processo existente se necessário
pkill Xvfb
```

### Certificado não detectado

- Verifique se certificado está instalado/importado corretamente
- Teste manualmente no Chrome do servidor
- Verifique se plugin WebSigner está instalado e funcionando

### Erro de navegação

- Verifique conectividade de rede
- Verifique logs: `tail -f /var/log/tjsp-bot.log`
- Teste manualmente: `DISPLAY=:99 google-chrome --no-sandbox`

### Performance

- Xvfb consome recursos (normal)
- Considere aumentar RAM/CPU do servidor
- Configure agendamento apropriado (não rodar muito frequente)

## Logs

Os logs são exibidos no console. Para produção, redirecione para arquivo:

```bash
python3 main.py >> /var/log/tjsp-bot.log 2>&1
```

## Notas Importantes

⚠️ **Este bot requer:**
- Certificado A1 válido e instalado
- Plugin WebSigner funcionando
- Ambiente gráfico virtual (Xvfb)
- Não funciona em modo headless puro

⚠️ **Sessão pode expirar:**
- O e-SAJ pode exigir reautenticação periódica
- Configure monitoramento e alertas
- Considere renovação manual quando necessário

## Suporte

Para problemas específicos, verifique:
1. Logs da aplicação
2. Logs do sistema (`journalctl -u tjsp-bot`)
3. Status do Xvfb (`ps aux | grep Xvfb`)
4. Testes manuais no navegador
