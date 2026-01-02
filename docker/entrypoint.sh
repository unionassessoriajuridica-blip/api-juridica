#!/bin/bash
# Script de inicialização do container

set -e

echo "=== Iniciando TJSP Bot Container ==="

# Inicia Xvfb em background
echo "Iniciando Xvfb no display :99..."
Xvfb :99 -screen 0 1920x1080x24 -ac +extension RANDR &
XVFB_PID=$!

# Aguarda Xvfb inicializar
sleep 2

# Verifica se Xvfb está rodando
if ! kill -0 $XVFB_PID 2>/dev/null; then
    echo "ERRO: Xvfb não conseguiu iniciar!"
    exit 1
fi

echo "✓ Xvfb iniciado (PID: $XVFB_PID)"

# Opcional: Inicia VNC server para debug remoto
# Descomente as linhas abaixo se quiser acessar via VNC
# echo "Iniciando VNC server na porta 5900..."
# x11vnc -display :99 -forever -shared -rfbport 5900 -bg -o /var/log/x11vnc.log
# echo "✓ VNC server iniciado (senha: vnc)"

# Limpa processo ao sair
trap "kill $XVFB_PID 2>/dev/null" EXIT

# Executa comando passado
echo "Executando: $@"
exec "$@"

