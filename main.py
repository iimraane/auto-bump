# -*- coding: utf-8 -*-
"""
Made witch <3 by El Titano 

Dépendance : selenium>=4.20.0
Lancement : python discord_bump_bot.py
"""

import json, os, sys, time, pickle, traceback
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException, JavascriptException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CONFIG_PATH = "config.json"
COOKIES_PATH = "cookies.pkl"
CHROME_PROFILE_DIR = os.path.abspath("chrome_profile")  # 👈 session persistante

BANNER = r"""
=========================================================
🥳  DISCORD BUMP BOT — By El Titano
=========================================================
"""

MENU = """
🎛️  MENU PRINCIPAL
1) ⚙️  Configurer
2) 🚀  Lancer 
3) 📖  Explications / Aide
4) ❌  Quitter
"""

EXPLICATION = """
📖  COMMENT ÇA MARCHE (résumé)

1) ⚙️ Configurer
   • Colle l’URL du salon/fil (doit contenir "discord.com/channels/").
   • (Optionnel) Login : on ouvre discord.com/login, tu te connectes ➜ on détecte ton panneau utilisateur,
     on lit ton pseudo et on enregistre ta session (profil Chrome dédié + cookies en secours).

2) 🚀 Lancer
   • Donne une heure de départ (ex: 21:30 ou 'now' / 'maintenant').
   • À l’heure : /bump (Entrée x2) + "Bot made with <3 by El Titano".
   • Pause 2h01 puis on recommence 🔁 (laisse Chrome ouvert).

3) 🆘 Si souci
   • Je t’explique le pourquoi et comment corriger 🙂
   • Support : discord **@el_titano**
"""

# ---------- UTILITAIRES CONSOLE ----------
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def header():
    clear(); print(BANNER.strip())

def soft_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\n🛑 Opération annulée."); sys.exit(0)

def live_countdown(seconds: int, prefix="⏳ Attente"):
    try:
        while seconds > 0:
            mins, secs = divmod(seconds, 60); hrs, mins = divmod(mins, 60)
            print(f"\r{prefix} : {hrs:02d}:{mins:02d}:{secs:02d} (Ctrl+C pour arrêter) ", end="", flush=True)
            time.sleep(1); seconds -= 1
        print("\r" + " " * 80 + "\r", end="")
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé. À bientôt !"); sys.exit(0)

# ---------- CONFIG ----------
def load_config():
    if not os.path.exists(CONFIG_PATH): return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return {}

def save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def validate_discord_url(u: str) -> bool:
    return u.startswith("http") and ("discord.com/channels/" in u)

# ---------- SELENIUM / CHROME ----------
def ensure_profile_dir():
    os.makedirs(CHROME_PROFILE_DIR, exist_ok=True)

def chrome_options_headed() -> Options:
    ensure_profile_dir()
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-infobars")
    # ✅ Profil persistant → conserve la session comme un navigateur normal
    opts.add_argument(f"--user-data-dir={CHROME_PROFILE_DIR}")
    # adoucit les warnings
    opts.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    return opts

def make_service_silent() -> Service:
    try:
        return Service(log_output=os.devnull)  # Selenium >= 4.7
    except TypeError:
        return Service()

def make_driver() -> webdriver.Chrome:
    try:
        service = make_service_silent()
        driver = webdriver.Chrome(service=service, options=chrome_options_headed())
        driver.set_page_load_timeout(60)
        return driver
    except WebDriverException as e:
        print("❌ ChromeDriver n’a pas pu démarrer.")
        print("Vérifie Google Chrome + selenium>=4.20.")
        print("Détails :", e); print("Support : discord @el_titano"); sys.exit(1)

# ---------- COOKIES (FALLBACK, si le profil échoue) ----------
def save_cookies(driver: webdriver.Chrome):
    try:
        cookies = driver.get_cookies()
        with open(COOKIES_PATH, "wb") as f: pickle.dump(cookies, f)
        print("🍪 Cookies enregistrés (secours).")
    except Exception as e:
        print("⚠️ Sauvegarde cookies échouée :", e)

def load_cookies(driver: webdriver.Chrome, base_url: str = "https://discord.com"):
    if not os.path.exists(COOKIES_PATH):
        print("ℹ️ Pas de cookies de secours (profil Chrome devrait suffire)."); return
    try:
        driver.get(base_url)
        with open(COOKIES_PATH, "rb") as f: cookies = pickle.load(f)
        for c in cookies:
            if "sameSite" in c and c["sameSite"] is None: c["sameSite"] = "Lax"
            try: driver.add_cookie(c)
            except Exception: pass
        driver.get(base_url)
        print("✅ Cookies (secours) rechargés.")
    except Exception as e:
        print("⚠️ Chargement cookies (secours) impossible :", e)

# ---------- INTERSTITIEL "APPLICATION DÉTECTÉE" ----------
def click_continue_in_browser_if_needed(driver, timeout=10):
    """
    Clique "Continuer dans le navigateur" / "Continue in browser" si l’interstitiel s’affiche.
    On essaie plusieurs méthodes (texte FR/EN, classes, JS click).
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            # 1) XPath par texte (FR + EN)
            btns = driver.find_elements(
                By.XPATH,
                "//button[.//div[contains(., 'Continuer dans le navigateur')] or .//*[contains(., 'Continue in browser')]]"
            )
            if not btns:
                # 2) CSS par classes connues + innerText
                btns = driver.find_elements(By.CSS_SELECTOR, "button.linkButton__921c5, button.lookLink__201d5")
                btns = [b for b in btns if "navigateur" in (b.text or "").lower() or "browser" in (b.text or "").lower()]
            if btns:
                try:
                    btns[0].click()
                except Exception:
                    # 3) Dernier recours : click JS
                    driver.execute_script("arguments[0].click();", btns[0])
                print("🧭 Interstitiel détecté → 'Continuer dans le navigateur' cliqué.")
                time.sleep(1)
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

# ---------- LOGIN & USERNAME ----------
def wait_for_login_panel_and_get_username(driver: webdriver.Chrome, timeout=300) -> str:
    print("🔐 Connecte-toi… je guette le panneau utilisateur.")
    start = time.time(); username = None
    while time.time() - start < timeout:
        try:
            # Parfois Discord te redirige vers l’interstitiel
            click_continue_in_browser_if_needed(driver, timeout=2)

            panels = driver.find_elements(By.CSS_SELECTOR, 'section[aria-label="Zone utilisateur"]')
            if panels:
                try:
                    username = driver.execute_script("""
                        const sec = document.querySelector('section[aria-label="Zone utilisateur"]');
                        if (!sec) return null;
                        const text = (sec.textContent || "").trim();
                        const lines = text.split('\\n').map(s => s.trim()).filter(Boolean);
                        for (const L of lines) { if (L.length > 0 && L.length <= 30) return L; }
                        return lines.length ? lines[0] : null;
                    """)
                except JavascriptException:
                    username = None
                return (username or "Utilisateur").strip()
        except Exception:
            pass
        time.sleep(1.0)
    raise TimeoutException("Login non détecté (panneau utilisateur introuvable).")

def do_login_flow_and_save(driver: webdriver.Chrome) -> str:
    driver.get("https://discord.com/login")
    click_continue_in_browser_if_needed(driver, timeout=5)
    username = wait_for_login_panel_and_get_username(driver)
    print(f"✅ Bien connecté(e) en tant que {username}")
    # se placer sur l’app avant de snapshot cookies (au cas où)
    driver.get("https://discord.com/channels/@me")
    time.sleep(1.0)
    save_cookies(driver)  # secours ; la session principale vit dans chrome_profile
    return username

# ---------- TIMING ----------
def parse_time(hhmm: str):
    hhmm = hhmm.strip()
    if hhmm.lower() in ("now", "maintenant"): return datetime.now()
    if ":" not in hhmm: raise ValueError("Format d’heure invalide (ex: 21:30).")
    hh, mm = hhmm.split(":")[:2]; hh, mm = int(hh), int(mm)
    now = datetime.now()
    target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if target <= now: target += timedelta(days=1)
    return target

def wait_until(hhmm: str):
    try:
        target = parse_time(hhmm)
    except Exception as e:
        print(f"⚠️ {e}\nSupport : discord @el_titano"); return False
    print(f"⏰ Départ programmé : {target.strftime('%Y-%m-%d %H:%M')}")
    seconds = int((target - datetime.now()).total_seconds())
    if seconds > 0: live_countdown(seconds, prefix="⏳ Attente jusqu’à l’heure de départ")
    return True

# ---------- ACTIONS DISCORD ----------
def open_target_and_focus_box(driver: webdriver.Chrome, url: str):
    print(f"🌐 Ouverture : {url}")
    driver.get(url)
    click_continue_in_browser_if_needed(driver, timeout=6)
    print("🖱️ Je cherche la zone de message…")
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            boxes = driver.find_elements(By.CSS_SELECTOR, 'div[role="textbox"][data-slate-editor="true"]')
            box = next((b for b in boxes if b.is_displayed()), None)
            if box:
                box.click(); time.sleep(0.2); return box
        except Exception:
            pass
        time.sleep(0.5)
    raise NoSuchElementException("Impossible de trouver le champ message (textbox).")

def send_bump_and_signature(driver: webdriver.Chrome):
    boxes = driver.find_elements(By.CSS_SELECTOR, 'div[role="textbox"][data-slate-editor="true"]')
    box = next((b for b in boxes if b.is_displayed()), None)
    if not box: raise NoSuchElementException("Textbox introuvable au moment d’envoyer.")
    print("⌨️ Envoi de /bump …")
    box.send_keys("/bump"); time.sleep(0.25); box.send_keys(Keys.ENTER); time.sleep(0.2); box.send_keys(Keys.ENTER)
    time.sleep(0.5)
    try: box.click()
    except Exception: pass
    signature = "Bot made with <3 by El Titano"
    print(f"💬 Envoi signature : {signature}")
    box.send_keys(signature); time.sleep(0.25); box.send_keys(Keys.ENTER)

def sleep_2h01():
    seconds = 2*60*60 + 60
    live_countdown(seconds, prefix="😴 Pause (2h01)")

# ---------- FLOWS ----------
def configure():
    cfg = load_config()
    print("⚙️ CONFIGURATION")
    print("\n👉 Colle l’URL du salon/fil Discord (https://discord.com/channels/…)")
    print("   (Entrée = garder la valeur actuelle)")
    current = cfg.get("url", "")
    if current: print(f"   URL actuelle : {current}")
    url = soft_input("> URL : ").strip() or current
    if not validate_discord_url(url):
        print("❌ URL invalide (il faut 'discord.com/channels/' dedans).")
        print("Support : discord @el_titano"); return

    driver = make_driver()
    # le profil persistant suffit souvent ; on tente néanmoins de recharger cookies de secours
    load_cookies(driver)
    driver.get("https://discord.com/channels/@me"); time.sleep(1.0)
    click_continue_in_browser_if_needed(driver, timeout=4)

    print("\n🔑 Veux-tu te (re)connecter maintenant ? (o/N)")
    do_login = soft_input("> ").strip().lower() == "o"

    username = cfg.get("username")
    if do_login or not username:
        try:
            username = do_login_flow_and_save(driver)
        except Exception as e:
            print("❌ Échec du login :", e); print("Support : discord @el_titano")
        finally:
            try: driver.quit()
            except Exception: pass
    else:
        try:
            username = username or "Utilisateur"
            driver.get("https://discord.com/channels/@me"); time.sleep(1.0)
            click_continue_in_browser_if_needed(driver, timeout=3)
        except Exception: pass
        finally:
            try: driver.quit()
            except Exception: pass

    cfg["url"] = url
    if username:
        cfg["username"] = username
        print(f"✅ Bien connecté(e) en tant que {username}")
    save_config(cfg); print("💾 Configuration sauvegardée !")

def lancer():
    cfg = load_config()
    if not cfg.get("url"):
        print("⚠️ Aucune URL configurée. Va d’abord dans '1) Configurer'."); return

    url = cfg["url"]; username = cfg.get("username", "Utilisateur")
    print(f"👤 Utilisateur prévu : {username}")
    print(f"🔗 URL cible       : {url}")
    print("\n⏰ Donne l’heure de départ (24h, ex: 21:30). Tu peux aussi taper 'now' / 'maintenant'.")
    start_at = soft_input("> Heure de début : ").strip()
    if not wait_until(start_at): return

    driver = make_driver()
    try:
        load_cookies(driver)  # secours ; principal = profil persistant
        open_target_and_focus_box(driver, url)
        cycle = 1
        while True:
            print(f"\n🔁 Cycle #{cycle}")
            try:
                send_bump_and_signature(driver)
            except Exception as e:
                print("❌ Erreur pendant l’envoi :", e)
                print("Causes fréquentes : textbox non focus, latence réseau, mise à jour Discord.")
                print("Astuce : clique une fois dans la zone de texte, puis laisse le script continuer.")
                print("Support : discord @el_titano")
            sleep_2h01()
            try:
                open_target_and_focus_box(driver, url)
            except Exception as e:
                print("⚠️ Zone de texte non retrouvée :", e, "\nJe réessaierai au prochain cycle.")
            cycle += 1

    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l’utilisateur. Bonne journée !")
    except Exception as e:
        print("💥 Erreur inattendue :", e); traceback.print_exc(); print("Support : discord @el_titano")
    finally:
        try: driver.quit()
        except Exception: pass

def explications():
    print(EXPLICATION)

def main():
    header()
    while True:
        print(MENU)
        choice = soft_input("> Choix (1/2/3/4) : ").strip(); header()
        if choice == "1": configure()
        elif choice == "2": lancer()
        elif choice == "3": explications()
        elif choice == "4": print("👋 Bye !"); break
        else: print("🤔 Option inconnue. Essaye 1, 2, 3 ou 4.")
        soft_input("\n(Entrée pour revenir au menu)"); header()

if __name__ == "__main__":
    main()
