#!/usr/bin/env python3
"""
eCourts Scraper (Python + Selenium)
-----------------------------------
Takes a CNR number, searches on eCourts, and checks if the case is listed today or tomorrow.
Shows results on console and saves them as JSON.
"""

import json
import os
import time
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import argparse

# -------------------- SETTINGS --------------------
BASE_URL = "https://services.ecourts.gov.in/ecourtindia_v6/"
OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# ---------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="eCourts CNR Scraper")
    parser.add_argument("--cnr", type=str, help="CNR number to fetch case details")
    parser.add_argument("--today", action="store_true", help="Filter to only show today's listings")
    return parser.parse_args()

def today_str():
    return datetime.now().strftime("%d-%m-%Y")

def tomorrow_str():
    return (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")

def setup_driver(headless=True):
    """Set up Chrome driver (headless optional)."""
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    return driver

def search_case_by_cnr(cnr):
    """Open eCourts site, prefill CNR, let user solve captcha, then scrape."""
    print("🚀 Opening browser — please complete the CAPTCHA manually.")
    opts = Options()
    opts.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    driver.get(BASE_URL)
    time.sleep(3)

    try:
        # Fill CNR number automatically
        search_box = driver.find_element(By.ID, "cino")
        search_box.clear()
        search_box.send_keys(cnr)
        print("✅ CNR number entered automatically.")
        print("⚠️ Please enter the CAPTCHA manually and click 'Search' on the website.")
        input("👉 When you finish (after results appear), press ENTER here in this terminal to continue... ")
    except Exception as e:
        print("❌ Error entering CNR:", e)
        try:
            driver.quit()
        except:
            pass
        return ""

    # Capture page source
    try:
        page_html = driver.page_source
        print("✅ Captured result page.")
    except Exception as e:
        print("⚠️ Could not capture page source:", e)
        page_html = ""

    try:
        driver.quit()
    except:
        pass

    return page_html

def parse_case_result(html):
    """Extract structured case info from eCourts HTML text."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    result = {}

    # Helper function to safely extract using regex
    def extract(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    # Extract key fields
    result["case_type"] = extract(r"Case Type\s*([A-Z0-9 \-]+)")
    result["filing_number"] = extract(r"Filing Number\s*([0-9/]+)")
    result["filing_date"] = extract(r"Filing Date\s*([0-9\-]+)")
    result["registration_number"] = extract(r"Registration Number\s*([0-9/]+)")
    result["registration_date"] = extract(r"Registration Date[:\s]*([0-9\-]+)")
    result["first_hearing_date"] = extract(r"First Hearing Date\s*([A-Za-z0-9\s\-]+)")
    result["next_hearing_date"] = extract(r"Next Hearing Date\s*([A-Za-z0-9\s\-]+)")
    result["case_stage"] = extract(r"Case Stage\s*([A-Z ]+)")
    result["court_name"] = extract(r"Court Number and Judge\s*([A-Za-z0-9 \-\.]+)")
    result["petitioner"] = extract(r"Petitioner.*?\)\s*([A-Z\s\.\&]+)")
    result["respondent"] = extract(r"Respondent.*?\)\s*([A-Z\s\.\&]+)")

    # Check listing dates (today/tomorrow)
    today = today_str()
    tomorrow = tomorrow_str()
    result["listed_today"] = today in text
    result["listed_tomorrow"] = tomorrow in text

    return result

def save_json(filename, data):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path

def main():
    args = parse_args()

    # Get CNR either from CLI or input
    if args.cnr:
        cnr = args.cnr.strip()
    else:
        cnr = input("Enter CNR number (e.g., MHAU019999992015): ").strip()

    if not cnr:
        print("❌ No CNR entered.")
        return

    print(f"🔍 Searching for CNR: {cnr} ...")
    html = search_case_by_cnr(cnr)

    if not html:
        print("❌ No HTML captured. Exiting.")
        return

    print("📄 Parsing results...")
    result = parse_case_result(html)

    # If --today is set, exit if not listed today
    if args.today and not result["listed_today"]:
        print(f"⚠️ Case {cnr} is not listed today.")
        return

    data = {
        "CNR": cnr,
        "checked_on": datetime.now().isoformat(),
        "results": result
    }

    json_path = save_json(f"result_{cnr}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", data)

    print("\n✅ Done!")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n💾 Results saved to: {json_path}")

if __name__ == "__main__":
    main()
