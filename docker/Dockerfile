# Dockerfile para rodar TJSP Bot com Xvfb
# 
# Este container fornece um ambiente gráfico virtual usando Xvfb,
# permitindo que o WebSigner funcione mesmo sem monitor físico.

FROM ubuntu:22.04

# Evita prompts interativos durante instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependências básicas
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    gnupg \
    ca-certificates \
    xvfb \
    x11vnc \
    fluxbox \
    && rm -rf /var/lib/apt/lists/*

# Instala Google Chrome (necessário para WebSigner)
# NOTA: WebSigner pode requerer Chrome instalado, mas Chromium do Playwright também pode funcionar
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Instala navegadores do Playwright
RUN python3 -m playwright install chromium
RUN python3 -m playwright install-deps chromium

# Copia código da aplicação
COPY . .

# Define variáveis de ambiente
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Script de inicialização
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expõe porta VNC (opcional, para debug)
EXPOSE 5900

# Ponto de entrada
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "main.py"]

