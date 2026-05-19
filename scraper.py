import time
import shutil
import os
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

DATA_DIR = Path(__file__).parent / "data"
SCREENSHOTS_DIR = Path(__file__).parent / "debug_screenshots"
STEP = 0


def log(msg):
    print(f"  {msg}")


def screenshot(driver, label):
    global STEP
    STEP += 1
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    path = SCREENSHOTS_DIR / f"step_{STEP:02d}_{label}.png"
    driver.save_screenshot(str(path))


def setup_driver():
    options = Options()
    download_dir = str(DATA_DIR.resolve())
    auto_profile = str(Path(__file__).parent / "chrome_profile")
    options.add_argument(f"--user-data-dir={auto_profile}")
    options.add_argument("--start-maximized")

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    return driver


def run_scraper():
    global STEP
    STEP = 0
    DATA_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 50)
    print("Wingstop Power BI Scraper")
    print("=" * 50)

    driver = setup_driver()

    try:
        # --- Step 1: Go to MyWingstop Reports ---
        print("\n[1] Opening my.wingstop.com/Reports...")
        driver.get("https://my.wingstop.com/Reports")
        time.sleep(8)
        screenshot(driver, "wingstop_reports")
        print(f"  URL: {driver.current_url}")

        # --- Step 2: Handle login if needed ---
        if "login" in driver.current_url.lower() or "microsoftonline" in driver.current_url:
            print("\n[2] Login page detected.")
            screenshot(driver, "login_page")

            # Try picking saved account
            try:
                account = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//*[contains(text(), 'stephen@flwingmen.com')] | "
                        "//*[contains(text(), 'Stephen flwingmen')]"
                    ))
                )
                log("Found saved account. Clicking...")
                account.click()
                time.sleep(8)
                screenshot(driver, "after_account_click")
            except Exception:
                # Try entering email manually
                try:
                    email_field = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
                    )
                    email_field.send_keys("stephen@flwingmen.com")
                    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
                    time.sleep(5)
                    screenshot(driver, "after_email")

                    # Password page
                    try:
                        pass_field = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                        )
                        log("Password page. Please enter your password in the browser.")
                        log("Waiting 30 seconds...")
                        time.sleep(30)
                    except Exception:
                        pass
                except Exception:
                    log("Please log in manually in the browser window.")
                    log("Waiting 30 seconds...")
                    time.sleep(30)

            # Wait for redirect
            time.sleep(5)
            screenshot(driver, "after_login")
            print(f"  URL: {driver.current_url}")

            # If redirected to home, go to Reports
            if "/Reports" not in driver.current_url:
                driver.get("https://my.wingstop.com/Reports")
                time.sleep(8)

        # --- Step 3: Click "Results and Performance" under Smart Kitchen ---
        print("\n[3] Looking for 'Results and Performance'...")
        screenshot(driver, "reports_page")

        # Scroll down to Smart Kitchen section
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        try:
            link = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//*[contains(text(), 'Results and Performance')]"
                ))
            )
            log("Found 'Results and Performance'. Clicking...")
            link.click()
            time.sleep(10)
        except Exception:
            log("Could not find link. Trying alternative...")
            screenshot(driver, "no_results_link")
            # Try all links
            links = driver.find_elements(By.TAG_NAME, "a")
            for l in links:
                if "result" in l.text.lower() or "performance" in l.text.lower():
                    if "smart" not in l.text.lower() or "ops" not in l.text.lower():
                        l.click()
                        time.sleep(10)
                        break

        screenshot(driver, "after_results_click")

        # --- Step 4: Switch to Power BI tab ---
        print("\n[4] Checking for new tab...")
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            log(f"Switched to new tab: {driver.current_url}")
        else:
            log(f"Same tab: {driver.current_url}")

        # Wait for Power BI to load
        log("Waiting for Power BI to load...")
        time.sleep(15)
        screenshot(driver, "powerbi_loaded")

        # --- Step 5: Click "Detailed Metrics (Store Weekly)" ---
        print("\n[5] Navigating to 'Detailed Metrics (Store Weekly)'...")
        try:
            page_link = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//span[contains(text(), 'Detailed Metrics (Store')]"
                ))
            )
            page_link.click()
            time.sleep(10)
            log("Clicked page link.")
            screenshot(driver, "detailed_metrics")
        except Exception:
            log("Could not find sidebar link. Trying alternative selectors...")
            screenshot(driver, "no_sidebar_link")
            try:
                # Try other selectors
                page_link = driver.find_element(By.XPATH,
                    "//*[contains(@title, 'Detailed Metrics (Store')] | "
                    "//*[contains(@aria-label, 'Detailed Metrics')]"
                )
                page_link.click()
                time.sleep(10)
                screenshot(driver, "detailed_metrics_alt")
            except Exception:
                log("Still could not find it. Listing sidebar items...")
                items = driver.find_elements(By.CSS_SELECTOR, "[role='listitem'] span, [role='tab'] span")
                for item in items:
                    log(f"  Sidebar: '{item.text}'")

        # --- Step 6: Export data ---
        print("\n[6] Exporting table data...")
        time.sleep(5)
        existing_files = set(f.name for f in DATA_DIR.glob("*"))

        # Find the table and right-click to export
        table = None
        for selector in [
            "div.tableEx",
            "div[class*='tablixContainer']",
            "div[class*='bodyCells']",
            "div[class*='tableSection']",
        ]:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                table = elements[-1]
                log(f"Found table with: {selector}")
                break

        if not table:
            # Try visual containers
            visuals = driver.find_elements(By.CSS_SELECTOR, "visual-container, .visual-container-component")
            if visuals:
                # Scroll down to find table visual (usually at bottom)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                visuals = driver.find_elements(By.CSS_SELECTOR, "visual-container, .visual-container-component")
                table = visuals[-1] if visuals else None
                log(f"Using last visual container ({len(visuals)} found)")

        if table:
            screenshot(driver, "found_table")

            # Right-click the table
            actions = ActionChains(driver)
            actions.context_click(table).perform()
            time.sleep(3)
            screenshot(driver, "context_menu")

            # Click "Export data"
            try:
                export_opt = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//*[contains(text(), 'Export data')]"
                    ))
                )
                export_opt.click()
                time.sleep(3)
                screenshot(driver, "export_dialog")

                # Click the Export button in the dialog
                try:
                    export_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH,
                            "//button[contains(text(), 'Export')]"
                        ))
                    )
                    export_btn.click()
                    time.sleep(15)
                    screenshot(driver, "after_export")
                    log("Export clicked!")
                except Exception:
                    log("Could not find Export button in dialog.")
                    screenshot(driver, "no_export_button")
            except Exception:
                log("No 'Export data' in context menu.")
                screenshot(driver, "no_export_data_option")

                # Try the toolbar Export button instead
                try:
                    toolbar_export = driver.find_element(By.XPATH,
                        "//button[@aria-label='Export'] | "
                        "//span[text()='Export']/.."
                    )
                    toolbar_export.click()
                    time.sleep(3)
                    screenshot(driver, "toolbar_export_menu")
                except Exception:
                    log("Could not find toolbar Export either.")
                    screenshot(driver, "no_toolbar_export")
        else:
            log("Could not find any table on the page.")
            screenshot(driver, "no_table")
            # Log page source for debugging
            log(f"Page title: {driver.title}")
            log(f"URL: {driver.current_url}")

        # --- Step 7: Check for download ---
        print("\n[7] Checking for downloaded file...")
        time.sleep(5)
        current_files = set(f.name for f in DATA_DIR.glob("*"))
        new_files = current_files - existing_files
        new_files = [f for f in new_files if not f.endswith(".crdownload")]

        if new_files:
            for f in new_files:
                old_path = DATA_DIR / f
                new_name = f"powerbi_detailed_metrics_{timestamp}{old_path.suffix}"
                new_path = DATA_DIR / new_name
                shutil.move(str(old_path), str(new_path))
                print(f"  Downloaded: {new_name}")
        else:
            log("No new files in data folder.")
            # Check default downloads folder
            downloads = Path.home() / "Downloads"
            dl_files = sorted(downloads.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
            recent = [f for f in dl_files[:5] if f.stat().st_mtime > time.time() - 60]
            if recent:
                log(f"Found recent file in Downloads: {recent[0].name}")
                new_name = f"powerbi_detailed_metrics_{timestamp}{recent[0].suffix}"
                shutil.move(str(recent[0]), str(DATA_DIR / new_name))
                print(f"  Moved to data folder: {new_name}")

        screenshot(driver, "final")
        print(f"\n{'=' * 50}")
        print("DONE! Check debug_screenshots/ for step-by-step images.")
        print(f"{'=' * 50}")

    except Exception as e:
        print(f"\nERROR: {e}")
        try:
            screenshot(driver, "fatal_error")
        except Exception:
            pass

    finally:
        driver.quit()


if __name__ == "__main__":
    run_scraper()
