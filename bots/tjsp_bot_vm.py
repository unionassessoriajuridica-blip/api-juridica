"""
TJSP Bot para execução em servidor com ambiente gráfico virtual (Xvfb/VNC).
INTEGRADO COM FACILITA ADV.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from config import Config
import os
import re
import time
import logging
import subprocess
import platform
import signal
import atexit
from datetime import datetime
import json
import requests # Biblioteca para enviar dados

logger = logging.getLogger(__name__)

# ==============================================================================
# CONFIGURAÇÕES DE INTEGRAÇÃO COM FACILITA ADV
# ==============================================================================
API_URL = "https://facilita.adv.br/api/robo/atualizar" 
API_TOKEN = "SENHA_DO_SEU_ROBO_123" # Tem que ser IGUAL ao que colocamos no arquivo robo.ts
# ==============================================================================

class TJSPBotVM:
    """
    Bot do TJSP otimizado para rodar em servidor com ambiente gráfico virtual.
    """
    
    def __init__(self):
        self.base_url = Config.TJSP_URL
        self.portal_root = "https://esaj.tjsp.jus.br"
        self.user_data_dir = "/var/www/tjsp_perfil_limpo"
        self.delay = Config.ACTION_DELAY
        self.display_num = ":99"
        self.xvfb_process = None
        self._is_linux = platform.system() == "Linux"
        
        if self._is_linux:
            self._setup_xvfb()
        else:
            logger.warning("Sistema não é Linux. Xvfb não será usado.")
    
    def _setup_xvfb(self):
        """Configura e inicia Xvfb (X Virtual Framebuffer)."""
        if not self._is_linux:
            return
        
        try:
            result = subprocess.run(
                ["pgrep", "-f", f"Xvfb {self.display_num}"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"Xvfb já está rodando no display {self.display_num}")
                os.environ["DISPLAY"] = self.display_num
                return
            
            logger.info(f"Iniciando Xvfb no display {self.display_num}...")
            self.xvfb_process = subprocess.Popen(
                [
                    "Xvfb",
                    self.display_num,
                    "-screen", "0", "1920x1080x24", 
                    "-ac", 
                    "+extension", "RANDR", 
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            os.environ["DISPLAY"] = self.display_num
            time.sleep(2)
            
            if self.xvfb_process.poll() is None:
                logger.info(f"✓ Xvfb iniciado com sucesso no display {self.display_num}")
                atexit.register(self._cleanup_xvfb)
            else:
                raise RuntimeError("Xvfb não conseguiu iniciar")
                
        except Exception as e:
            logger.error(f"Erro ao iniciar Xvfb: {e}")
            pass
    
    def _cleanup_xvfb(self):
        """Finaliza Xvfb."""
        if self.xvfb_process:
            try:
                logger.info("Finalizando Xvfb...")
                self.xvfb_process.terminate()
                self.xvfb_process.wait(timeout=5)
            except Exception:
                pass
            finally:
                self.xvfb_process = None
    
    def _launch_context(self, playwright):
        user_data = "/var/www/API Juridica/perfil_tjsp"
        ext_path = "/var/www/API Juridica/websigner_ext"
        
        launch_options = {
            "headless": False, 
            "channel": "chrome", 
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
            ],
            "ignore_default_args": ["--enable-automation", "--disable-extensions"]
        }
        
        os.environ["DISPLAY"] = ":99"
        return playwright.chromium.launch_persistent_context(
            user_data_dir=user_data,
            **launch_options
        )

    def fetch_esaj_movements(self, process_number: str):
        timeout_padrao = getattr(Config, 'TIMEOUT', 60000)

        try:
            with sync_playwright() as p:
                context = self._launch_context(p)
                page = context.new_page()

                # --- ETAPA 1: LOGIN ---
                logger.info("Acessando página de login...")
                try:
                    page.goto(Config.TJSP_CERT_LOGIN_URL, timeout=timeout_padrao, wait_until="load")
                    time.sleep(3) 

                    if page.locator("#submitCertificado").is_visible(timeout=5000):
                        page.click("#submitCertificado")
                        page.wait_for_url(lambda url: "login" not in url, timeout=15000)
                    elif "login" not in page.url and "esaj.tjsp.jus.br" in page.url:
                        logger.info("Já logado. Prosseguindo.")
                    else:
                        try:
                            page.click("#submitCertificado", timeout=5000)
                        except:
                            pass
                except Exception as e:
                    logger.warning(f"Aviso no login: {e}. Tentando prosseguir.")

                # --- ETAPA 2: CONSULTA ---
                logger.info(f"Consultando processo: {process_number}")
                page.goto("https://esaj.tjsp.jus.br/cpopg/open.do", timeout=timeout_padrao, wait_until="domcontentloaded")
                
                try:
                    radio_selector = "#radioNumeroAntigo"
                    if page.locator(radio_selector).is_visible(timeout=10000):
                        page.locator(radio_selector).click()
                        page.fill("#nuProcessoAntigoFormatado", process_number)
                        page.click("#botaoConsultarProcessos")
                    else:
                        logger.error("Campo de busca não encontrado.")
                        return None
                except Exception as e:
                    logger.error(f"Erro no form de consulta: {e}")
                    return None

                # --- ETAPA 3: RESULTADOS ---
                logger.info("Aguardando resultados...")
                try:
                    page.wait_for_selector("#tabelaTodasMovimentacoes, #tabelaUltimasMovimentacoes, #mensagemRetorno, .alert", timeout=30000)
                    
                    if page.locator("#mensagemRetorno").is_visible():
                        msg = page.locator("#mensagemRetorno").inner_text()
                        if "não encontrado" in msg.lower():
                            logger.info("Processo não encontrado.")
                            return None
                except PlaywrightTimeoutError:
                    logger.error("Timeout esperando resultados.")
                    return None

                movements = self._extract_movements(page)

                page.close()
                context.close()

                if movements:
                    raw_text = ""
                    for m in movements:
                        raw_text += f"{m['date']} - {m['title']}\n{m['description']}\n\n"

                    return {
                        "number": process_number,
                        "status": "Found",
                        "last_movement": movements[0],
                        "movements": movements,
                        "raw_text": raw_text,
                    }
                return None

        except Exception as e:
            logger.error(f"Erro fatal no TJSPBot: {e}")
            return None

    def _extract_movements(self, page):
        movements = []
        try:
            try:
                link_todas = page.locator("#linkMovimentacoes")
                if link_todas.is_visible():
                    link_todas.click()
                    time.sleep(1)
            except:
                pass

            rows = page.locator("tr.containerMovimentacao").all()
            
            # --- IMPRESSÃO NO TERMINAL (RESTAURADA) ---
            print(f"\n{'='*20} EXTRATO DE MOVIMENTAÇÕES ({len(rows)} encontradas) {'='*20}\n")
            
            for i, row in enumerate(rows):
                try:
                    date = row.locator(".dataMovimentacao").inner_text().strip() if row.locator(".dataMovimentacao").count() > 0 else "S/D"
                    
                    desc_el = row.locator(".descricaoMovimentacao")
                    title = ""
                    description = ""
                    
                    if desc_el.count() > 0:
                        full_text = desc_el.inner_text().strip()
                        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                        if lines:
                            title = lines[0]
                            description = "\n".join(lines[1:]) if len(lines) > 1 else ""
                    
                    # PRINT INDIVIDUAL
                    print(f"MOVIMENTAÇÃO #{i+1}")
                    print(f"Data:      {date}")
                    print(f"Título:    {title}")
                    if description:
                        desc_formatada = description.replace('\n', '\n           ')
                        print(f"Descrição: {desc_formatada}")
                    else:
                        print(f"Descrição: [Sem detalhes adicionais]")
                    print("-" * 60)

                    movements.append({
                        "date": date,
                        "title": title,
                        "description": description
                    })
                except:
                    continue
            
            print(f"\n{'='*20} FIM DA EXTRAÇÃO {'='*20}\n")
                    
        except Exception as e:
            logger.error(f"Erro na extração: {e}")

        return movements
    
    def enviar_para_facilita(self, dados):
        """
        Envia os dados coletados para a API do Facilita ADV.
        """
        if not dados:
            return
            
        logger.info("Enviando dados para o Facilita ADV...")
        
        payload = {
            "numero_processo": dados["number"],
            "texto_movimentacoes": dados["raw_text"],
            "token_seguranca": API_TOKEN
        }
        
        try:
            # verify=False para evitar erros de certificado em localhost/dev
            response = requests.post(API_URL, json=payload, verify=False) 
            
            if response.status_code == 200:
                logger.info("✅ SUCESSO! Dados atualizados no site.")
                print(">> Dados enviados com sucesso para o banco de dados.")
            else:
                logger.error(f"❌ Erro ao enviar para API: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Falha de conexão com a API: {e}")

    def __del__(self):
        self._cleanup_xvfb()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Executa o TJSPBotVM para um único processo")
    parser.add_argument("process_number", help="Número do processo (formato 1504040-62.2025.8.26.0393)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    bot = TJSPBotVM()
    
    # 1. PEGAR OS DADOS
    resultado = bot.fetch_esaj_movements(args.process_number)
    
    # 2. SE PEGOU, ENVIAR PRO SITE
    if resultado:
        # Se quiser ver o JSON final também:
        # print(json.dumps(resultado, ensure_ascii=False, indent=2))
        
        bot.enviar_para_facilita(resultado)
    else:
        logger.warning("Não foi possível coletar dados para envio.")