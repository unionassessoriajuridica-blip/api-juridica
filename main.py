import sys
import argparse
import logging
from bots.tjsp_bot_vm import TJSPBotVM
from config import Config

# Configuração de Log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    print("=== Início da Automação Jurídica ===")

    # Configura argumentos para permitir execução via terminal:
    # Ex: python3 main.py "1513733-70.2025.8.26.0393"
    parser = argparse.ArgumentParser(description="Automação TJSP")
    parser.add_argument("process_number", nargs="?", help="Número do processo")
    args = parser.parse_args()

    # Se passou argumento, usa ele. Se não, usa a lista padrão.
    if args.process_number:
        processes_to_check = [args.process_number]
    else:
        processes_to_check = [
            "1513733-70.2025.8.26.0393"
        ]

    # Inicializa bot
    try:
        tjsp_bot = TJSPBotVM()  # Usa Xvfb para ambiente gráfico virtual
    except Exception as e:
        logger.error(f"Erro ao inicializar o bot: {e}")
        return

    for process_number in processes_to_check:
        print(f"\n--- Processando: {process_number} ---")

        # 1. Obter dados do TJSP
        logger.info(f"Buscando processo {process_number} no e-SAJ...")
        process_data = tjsp_bot.fetch_esaj_movements(process_number)

        if process_data:
            logger.info(f"Dados extraídos com sucesso. Última mov: {process_data.get('last_movement', {}).get('title', 'N/A')}")
            
            # 2. ENVIAR PARA O SITE (A parte nova)
            logger.info("Enviando dados para o Facilita ADV...")
            tjsp_bot.enviar_para_facilita(process_data)
            
        else:
            logger.warning(f"Não foi possível obter dados do processo {process_number}")

    print("\n=== Fim da Execução ===")

if __name__ == "__main__":
    main()
