# Level 2 data-driven register (Decision Table) using locators CSV
import csv
import time
from pathlib import Path
from typing import Dict, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FILE = PROJECT_ROOT / "data" / "REGISTER_DT.csv"
LOCATOR_FILE = PROJECT_ROOT / "locators.csv"
CHROMEDRIVER_PATH = Path(r"f:\HK251\Testing\btl3\Duy\common\chromedriver.exe")


def load_locators() -> Dict[str, Tuple[str, str]]:
    locs: Dict[str, Tuple[str, str]] = {}
    with LOCATOR_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            locs[row["name"]] = (row["type"], row["value"])
    return locs


def create_driver() -> webdriver.Chrome:
    driver = webdriver.Chrome(executable_path=str(CHROMEDRIVER_PATH))
    driver.implicitly_wait(15)
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
    firstname = row.get("firstname", "")
    lastname = row.get("lastname", "")
    email = row.get("email", "")
    telephone = row.get("telephone", "")
    password = row.get("password", "")
    confirm = row.get("confirm", "")
    agree = (row.get("agree", "").strip().lower() == "yes")
    expect_type = (row.get("expect_type") or "").strip().lower()
    expect_text = row.get("expect_text", "")

    driver = create_driver()
    try:
        driver.get(find(driver, locs, "register_url"))

        find(driver, locs, "firstname_input").clear()
        find(driver, locs, "firstname_input").send_keys(firstname)

        find(driver, locs, "lastname_input").clear()
        find(driver, locs, "lastname_input").send_keys(lastname)

        email_input = find(driver, locs, "email_input")
        driver.execute_script("arguments[0].setAttribute('type','text');", email_input)
        email_input.clear()
        email_input.send_keys(email)

        find(driver, locs, "telephone_input").clear()
        find(driver, locs, "telephone_input").send_keys(telephone)

        find(driver, locs, "password_input").clear()
        find(driver, locs, "password_input").send_keys(password)

        find(driver, locs, "confirm_input").clear()
        find(driver, locs, "confirm_input").send_keys(confirm)

        agree_checkbox = find(driver, locs, "agree_checkbox")
        if agree_checkbox.is_selected() != agree:
            label = find(driver, locs, "agree_label")
            driver.execute_script("arguments[0].scrollIntoView(true);", label)
            driver.execute_script("arguments[0].click();", label)

        find(driver, locs, "submit_button").click()
        time.sleep(2)

        if expect_type == "alert":
            self_assert(True, is_present(driver, locs, "alert_danger"), test_id, "alert missing")
            if expect_text:
                actual = find(driver, locs, "alert_danger").text
                self_assert(expect_text, actual, test_id, "alert text")
        elif expect_type == "field_error":
            self_assert(True, is_present(driver, locs, "field_error"), test_id, "field error")
        elif expect_type == "success":
            self_assert(True, is_present(driver, locs, "success_heading"), test_id, "success heading")
            if expect_text:
                actual = find(driver, locs, "success_heading").text
                self_assert(expect_text, actual, test_id, "success text")
            driver.get(find(driver, locs, "logout_url"))
        else:
            self_assert(True, False, test_id, f"Unknown expect_type: {expect_type}")

        print(f"[{test_id}] PASS")
    except AssertionError as ae:
        print(f"[{test_id}] FAIL - {ae}")
    except Exception as exc:
        print(f"[{test_id}] ERROR - {exc}")
    finally:
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


def is_present(driver: webdriver.Chrome, locs: Dict[str, Tuple[str, str]], name: str) -> bool:
    try:
        find(driver, locs, name)
        return True
    except NoSuchElementException:
        return False


def self_assert(expected, actual, test_id, msg):
    if expected != actual:
        raise AssertionError(f"{msg}: expected='{expected}' actual='{actual}'")


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
