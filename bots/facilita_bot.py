from playwright.sync_api import sync_playwright
from config import Config
import time

class FacilitaBot:
    def __init__(self):
        self.url = Config.FACILITA_URL
        self.user = Config.FACILITA_USER
        self.password = Config.FACILITA_PASS
        self.headless = Config.HEADLESS

    def login(self, page):
        print(f"[Facilita Bot] Navigating to {self.url}...")
        page.goto(self.url)
        
        # Wait for load
        page.wait_for_load_state("networkidle")
        
        # Check if we need to click a "Login" button first
        if page.locator("input[type='email']").count() == 0:
            print("[Facilita Bot] Login fields not found. Looking for 'Login' button...")
            login_btn = page.locator("text=Login").first
            if login_btn.count() > 0:
                print("[Facilita Bot] Clicking 'Login' button...")
                login_btn.click()
                page.wait_for_load_state("networkidle")
            else:
                print("[Facilita Bot] Warning: Could not find 'Login' button or inputs.")

        print("[Facilita Bot] Attempting login...")
        
        # Fill credentials
        # Selectors based on common practices, might need adjustment if IDs are dynamic
        try:
            page.fill("input[type='email']", self.user)
            page.fill("input[type='password']", self.password)
            
            # Click login button
            # Try multiple selectors for the button
            if page.locator("button[type='submit']").count() > 0:
                page.click("button[type='submit']")
            elif page.locator("text=Entrar").count() > 0:
                page.click("text=Entrar")
            elif page.locator("text=Login").count() > 0:
                page.click("text=Login")
            else:
                print("[Facilita Bot] Error: Login button not found.")
                return False
                
            page.wait_for_load_state("networkidle")
            
            # Check if login was successful
            # We assume success if we are redirected or see a dashboard element
            time.sleep(3) # Give some time for SPA transition
            print(f"[Facilita Bot] Page title after login: {page.title()}")
            
            if "login" not in page.url.lower():
                print("[Facilita Bot] Login successful!")
                return True
            else:
                print("[Facilita Bot] Login failed (still on login URL).")
                return False
                
        except Exception as e:
            print(f"[Facilita Bot] Login Error: {e}")
            return False

    def update_process(self, process_data):
        """
        Updates the process in Facilita ADV with the data fetched from TJSP.
        """
        if not process_data:
            print("[Facilita Bot] No data to update.")
            return

        with sync_playwright() as p:
            # Sempre rodar COM navegador visível para poder acompanhar
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            
            if self.login(page):
                print(f"[Facilita Bot] Searching for process {process_data['number']}...")
                
                print("[Facilita Bot] Waiting 5 seconds for dashboard to render...")
                time.sleep(5)

                print("[Facilita Bot] Looking for search input with data-testid='input-search-processos'...")
                
                search_input = None
                try:
                    search_input = page.wait_for_selector("[data-testid='input-search-processos']", timeout=10000)
                except:
                    print("[Facilita Bot] data-testid not found within timeout.")

                if not search_input:
                    print("[Facilita Bot] Trying placeholder...")
                    try:
                        search_input = page.wait_for_selector("input[placeholder='Buscar processos ativos...']", timeout=5000)
                    except:
                        pass

                if search_input:
                    print("[Facilita Bot] Search bar found. Typing process number...")
                    search_input.fill(process_data['number'])
                    search_input.press("Enter")
                    page.wait_for_load_state("networkidle")

                    # Aguarda 10 segundos para visualização do usuário na tela de resultados
                    print("[Facilita Bot] Pausando 10 segundos para visualização dos resultados.")
                    time.sleep(10)
                    
                    print("[Facilita Bot] Clicking on the first result...")
                    time.sleep(3)
                    edit_btn = page.locator("button[data-testid^='button-edit-']").first
                    if edit_btn.count() > 0:
                        print("[Facilita Bot] Edit button found directly in list. Clicking...")
                        edit_btn.click()
                    else:
                        print("[Facilita Bot] Edit button not found in list. Clicking on process number text...")
                        page.locator(f"text={process_data['number']}").first.click()
                        
                    page.wait_for_load_state("networkidle")
                    time.sleep(2)
                    print("[Facilita Bot] Looking for 'Info. Processo' tab with data-testid='tab-info-processo'...")
                    info_btn = None
                    try:
                        info_btn = page.wait_for_selector("[data-testid='tab-info-processo']", timeout=5000)
                    except:
                        print("[Facilita Bot] Tab not found by testid. Trying text...")
                        try:
                            info_btn = page.wait_for_selector("text=Info. Processo", timeout=3000)
                        except:
                            pass
                    if info_btn:
                        print("[Facilita Bot] Clicking 'Info. Processo'...")
                        info_btn.click()
                        time.sleep(2)
                        print("[Facilita Bot] SUCCESS! Navigated to Info. Processo tab.")
                    else:
                        print("[Facilita Bot] 'Info. Processo' button not found.")
                else:
                    print("[Facilita Bot] Search bar not found. Trying direct URL navigation (if pattern known)...")
            
            # Remover fechamento automático do browser
            print("[Facilita Bot] Automação finalizada. Navegador permanecerá aberto para inspeção manual.")
            print("[Facilita Bot] Feche o navegador manualmente quando desejar.")
            # NÃO chamar browser.close()
