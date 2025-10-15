#!/usr/bin/env python3
"""
fetch_test.py
Fetch the eCourts homepage using requests; if content looks JS-dependent, try Selenium.
Saves HTML files to results/.
"""

import os
import time
from pathlib import Path

OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)

TARGET = "https://services.ecourts.gov.in/ecourtindia_v6/"

HEADERS = {
    "User-Agent": "ecourts-scraper-test/1.0 (+https://example.com)"
}

def fetch_with_requests(url, timeout=15):
    import requests
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.text

def fetch_with_selenium(url, wait_seconds=3):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    try:
        driver.get(url)
        # wait for JS to render a bit
        time.sleep(wait_seconds)
        return driver.page_source
    finally:
        driver.quit()

def save_file(path, text):
    with open(path, "w", encoding="utf8") as f:
        f.write(text)
    print(f"Saved: {path}")

def has_cnr_like_text(html_text):
    t = html_text.lower()
    # crude checks: look for "cnr", "case no", "case no.", "search by cnr"
    checks = ["cnr", "case no", "case number", "search by cnr", "search by cnr number"]
    return any(ch in t for ch in checks)

def looks_js_blocked(html_text):
    # If page is tiny or contains common JS placeholders, assume JS needed
    if len(html_text) < 3000:
        return True
    lower = html_text.lower()
    if "javascript" in lower and ("enable javascript" in lower or "please enable" in lower):
        return True
    # otherwise assume OK
    return False

def main():
    print("1) Trying requests...")
    try:
        html = fetch_with_requests(TARGET)
        save_file(OUTPUT_DIR / "homepage_requests.html", html)
        print("requests fetch OK — length:", len(html))
        if has_cnr_like_text(html):
            print(">>> The requests-fetched HTML already contains 'cnr' or case-number text. Likely we can scrap with requests + BeautifulSoup.")
        else:
            print(">>> Did NOT find obvious 'cnr' text in the requests HTML.")
        if looks_js_blocked(html):
            print(">>> The page looks small or suggests JS required. We will try Selenium next.")
        else:
            print(">>> Page looks like a full HTML page. Try inspecting results/homepage_requests.html in your browser.")
    except Exception as e:
        print("requests failed:", repr(e))
        html = None

    if html is None or looks_js_blocked(html) or not has_cnr_like_text(html):
        print("\n2) Falling back to Selenium to render the page (this will open headless Chrome)...")
        try:
            html2 = fetch_with_selenium(TARGET, wait_seconds=4)
            save_file(OUTPUT_DIR / "homepage_selenium.html", html2)
            print("Selenium fetch OK — length:", len(html2))
            if has_cnr_like_text(html2):
                print(">>> Selenium-rendered HTML contains 'cnr' or case-number text. Use Selenium or inspect the network calls to find a JSON endpoint.")
            else:
                print(">>> Even after rendering, no obvious 'cnr' text found. You should inspect the page manually with developer tools.")
        except Exception as e:
            print("Selenium fetch failed:", repr(e))
            print("If Selenium fails, ensure Chrome is installed and webdriver-manager can download the driver. You can also run the script with a display (no --headless) for debugging.")

if __name__ == "__main__":
    main()
