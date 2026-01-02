import sys
import argparse
import logging
import time
import requests
import hashlib
from bots.tjsp_bot_vm import TJSPBotVM
from config import Config

# Configuração de Log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Configurações da API
API_BASE = "https://facilita.adv.br/api/robo" # Ajuste se for localhost no teste
API_TOKEN = "SENHA_DO_SEU_ROBO_123"

def calcular_hash(texto):
    """Gera um hash MD5 para comparação rápida de conteúdo."""
    if not texto:
        return ""
    return hashlib.md5(texto.encode('utf-8')).hexdigest()

def obter_processos_do_banco():
    """Busca a lista de processos cadastrados no sistema."""
    url = f"{API_BASE}/listar?token_seguranca={API_TOKEN}"
    try:
        resp = requests.get(url, verify=False, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error(f"Erro ao obter processos: {resp.status_code} - {resp.text}")
            return []
    except Exception as e:
        logger.error(f"Falha de conexão ao listar processos: {e}")
        return []

def main():
    print("=== 🤖 Início da Automação (Modo Inteligente) ===")

    # Verifica se passou um processo específico via argumento (para testes manuais)
    parser = argparse.ArgumentParser()
    parser.add_argument("process_number", nargs="?", help="Processo específico")
    args = parser.parse_args()

    lista_processos = []

    if args.process_number:
        # Modo Teste: Apenas o processo informado
        logger.info(f"Modo Manual: Verificando apenas {args.process_number}")
        lista_processos = [{"numero_processo": args.process_number, "movimentacoes": ""}]
    else:
        # Modo Automático: Busca todos do banco
        logger.info("Modo Automático: Buscando lista de processos no banco...")
        lista_processos = obter_processos_do_banco()

    if not lista_processos:
        logger.warning("Nenhum processo encontrado para verificar.")
        return

    logger.info(f"Total de processos na fila: {len(lista_processos)}")

    # Inicializa o navegador (abre apenas uma vez para economizar memória)
    try:
        tjsp_bot = TJSPBotVM()
    except Exception as e:
        logger.error(f"Erro fatal ao iniciar navegador: {e}")
        return

    # Loop de Processamento
    for item in lista_processos:
        num_proc = item.get("numero_processo")
        texto_antigo = item.get("movimentacoes") or ""
        
        # Limpeza do número (remove pontuação para log/comparação se necessário)
        # Mas mantemos o formato original para a busca no site se for o padrão do TJ
        
        print(f"\n>>> Processando: {num_proc}")

        try:
            # 1. Busca dados novos no Site
            dados_novos = tjsp_bot.fetch_esaj_movements(num_proc)

            if dados_novos:
                texto_novo = dados_novos["raw_text"]

                # 2. COMPARAÇÃO INTELIGENTE (Deduplicação)
                # Comparamos os Hashes ou o texto cru. Se for igual, ignoramos.
                hash_antigo = calcular_hash(texto_antigo.strip())
                hash_novo = calcular_hash(texto_novo.strip())

                if hash_antigo == hash_novo:
                    logger.info(f"⏭️  Sem alterações. Dados já estão atualizados. Pulando envio.")
                else:
                    logger.info(f"✨ Novas movimentações detectadas! Enviando atualização...")
                    tjsp_bot.enviar_para_facilita(dados_novos)
            else:
                logger.warning(f"Não foi possível ler dados do processo {num_proc}")

        except Exception as e:
            logger.error(f"Erro ao processar {num_proc}: {e}")
            # Continua para o próximo processo mesmo com erro
            continue
        
        # Pausa para não bloquear o IP do tribunal (importante!)
        time.sleep(5) 

    print("\n=== Fim do Ciclo de Execução ===")

if __name__ == "__main__":
    main()