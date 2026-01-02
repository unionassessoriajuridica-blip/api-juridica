from playwright.sync_api import sync_playwright
import os, time, json

EXT_PATH = os.path.abspath("/var/www/API Juridica/websigner_ext")
USER_DIR = os.path.abspath("/var/www/API Juridica/.tjsp_session_vm")

os.environ.setdefault('DISPLAY', ':99')

with sync_playwright() as p:
    try:
        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            f"--disable-extensions-except={EXT_PATH}",
            f"--load-extension={EXT_PATH}",
        ]
        context = p.chromium.launch_persistent_context(user_data_dir=USER_DIR, headless=False, args=launch_args, env=os.environ.copy())
        page = context.new_page()
        page.goto('chrome://extensions/', timeout=20000)
        time.sleep(2)
        # Try to access shadow DOM to read extension items
        res = page.evaluate("""
            (() => {
                try {
                    const manager = document.querySelector('extensions-manager');
                    if (!manager) return {error: 'no manager'};
                    const mgr = manager.shadowRoot;
                    const items = mgr.querySelectorAll('extensions-item');
                    const out = [];
                    items.forEach(it => {
                        try {
                            const s = it.shadowRoot;
                            const idEl = s.querySelector('#extension-id');
                            const nameEl = s.querySelector('#name');
                            out.push({id: idEl? idEl.innerText.trim(): null, name: nameEl? nameEl.innerText.trim(): null});
                        } catch(e) {}
                    });
                    return {items: out};
                } catch (e) {
                    return {error: e.toString()};
                }
            })()
        """)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        context.close()
    except Exception as e:
        print({"error": str(e)})

