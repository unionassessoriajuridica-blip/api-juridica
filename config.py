import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Facilita ADV Credentials
    FACILITA_URL = "https://facilita-adv-original.ab.rio.br"
    FACILITA_USER = os.getenv("FACILITA_USER")
    FACILITA_PASS = os.getenv("FACILITA_PASS")
    HEADLESS = os.getenv('HEADLESS', 'True') == 'True'
    # TJSP URLs e Credenciais
    TJSP_URL = "https://esaj.tjsp.jus.br/cpopg/open.do"
    # URL de login direto do e-SAJ (fluxo novo especificado)
    TJSP_LOGIN_URL = os.getenv(
        "TJSP_LOGIN_URL",
        "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fesaj%2Fapi%2Fauth%2Fcheck#aba-certificado",
    )
    # URL que abre diretamente a aba de Certificado (com âncora). Use este link quando quiser
    # que a página já carregue na aba de Certificado digital.
    TJSP_CERT_LOGIN_URL = os.getenv(
        "TJSP_CERT_LOGIN_URL",
        "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fesaj%2Fapi%2Fauth%2Fcheck#aba-certificado",
    )
    # Bot Settings
    TIMEOUT = 30000  # 30 seconds
    # Atraso entre ações (segundos) para evitar corrida em páginas lentas
    ACTION_DELAY = float(os.getenv("ACTION_DELAY", "0.6"))
    
