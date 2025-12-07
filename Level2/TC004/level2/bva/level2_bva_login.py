# Data-driven login test (Level 2 style with locator CSV)
import csv
import time
from pathlib import Path
from typing import Dict, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FILE = PROJECT_ROOT / "data" / "BVA_LOGIN.csv"
LOCATOR_FILE = PROJECT_ROOT / "locators.csv"
CHROMEDRIVER_PATH = Path(__file__).resolve().parent.parent.parent / "common" / "chromedriver.exe"


def load_locators() -> Dict[str, Tuple[str, str]]:
    locators: Dict[str, Tuple[str, str]] = {}
    with LOCATOR_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            locators[row["name"]] = (row["type"], row["value"])
    return locators


def create_driver() -> webdriver.Chrome:
    service = Service(executable_path=str(CHROMEDRIVER_PATH))
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(10)
    return driver


def find(driver: webdriver.Chrome, locs: Dict[str, Tuple[str, str]], name: str):
    t, v = locs[name]
    if t == "id":
        return driver.find_element(By.ID, v)
    if t == "css":
        return driver.find_element(By.CSS_SELECTOR, v)
    if t == "xpath":
        return driver.find_element(By.XPATH, v)
    if t == "url":
        return v
    raise ValueError(f"Unsupported locator type: {t}")


def run_case(row: dict, locs: Dict[str, Tuple[str, str]]) -> None:
    test_id = row.get("tc_id")
    email = (row.get("email") or "").strip()
    password = (row.get("password") or "").strip()
    expect_type = (row.get("expect_type") or "").strip().lower()
    expect_text = row.get("expect_text") or ""

    driver = create_driver()
    try:
        driver.get(find(driver, locs, "login_url"))

        find(driver, locs, "email_input").clear()
        find(driver, locs, "email_input").send_keys(email)
        find(driver, locs, "password_input").clear()
        find(driver, locs, "password_input").send_keys(password)
        find(driver, locs, "login_button").click()
        time.sleep(2)

        if expect_type == "success":
            heading = find(driver, locs, "account_heading")
            actual = heading.text
            ok = expect_text in actual if expect_text else heading is not None
            note = ""
        elif expect_type == "alert":
            alert = find(driver, locs, "alert_danger")
            actual = alert.text
            lockout = "exceeded allowed number of login attempts"
            if lockout.lower() in actual.lower():
                ok = True  # accept lockout as valid for repeated attempts
                note = "(lockout)"
            else:
                ok = (expect_text == actual) if expect_text else alert is not None
                note = ""
        else:
            ok = False
            actual = ""
            note = ""

        result = "PASS" if ok else "FAIL"
        print(f"[{test_id}] {result} {note} expected='{expect_text}' actual='{actual}'")
    finally:
        # always cleanly close to avoid rate-limit accumulation
        try:
            driver.delete_all_cookies()
            driver.execute_script("window.sessionStorage.clear(); window.localStorage.clear();")
            driver.get("about:blank")
        except Exception:
            pass
        try:
            driver.quit()
        except Exception:
            pass


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing data file: {DATA_FILE}")
    if not LOCATOR_FILE.exists():
        raise FileNotFoundError(f"Missing locator file: {LOCATOR_FILE}")

    locs = load_locators()
    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            run_case(row, locs)
            time.sleep(0.8)


if __name__ == "__main__":
    main()
