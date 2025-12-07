import csv
import time
from pathlib import Path
from typing import Dict, Tuple

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "checkout_data.csv"
LOCATOR_FILE = PROJECT_ROOT / "data" / "locators.csv"
GECKODRIVER_PATH = PROJECT_ROOT.parent / "geckodriver.exe"


def load_locators() -> Dict[str, Tuple[str, str]]:
    """Load locators/url definitions from CSV into a dictionary."""
    locators: Dict[str, Tuple[str, str]] = {}
    with LOCATOR_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            loc_type = row["type"]
            value = row["value"]
            locators[name] = (loc_type, value)
    return locators


def create_driver() -> webdriver.Firefox:
    opts = Options()
    opts.add_argument("--start-maximized")

    service = Service(GeckoDriverManager().install())
    # service = Service(str(GECKODRIVER_PATH))
    driver = webdriver.Firefox(service=service, options=opts)
    driver.implicitly_wait(5)
    return driver


def find(driver: webdriver.Firefox, locators: Dict[str, Tuple[str, str]], name: str):
    """Find a single element by locator name defined in CSV."""
    loc_type, value = locators[name]
    if loc_type == "id":
        return driver.find_element(By.ID, value)
    if loc_type == "css":
        return driver.find_element(By.CSS_SELECTOR, value)
    if loc_type == "xpath":
        return driver.find_element(By.XPATH, value)
    raise ValueError(f"Unsupported locator type: {loc_type}")


def login(driver: webdriver.Firefox, locators: Dict[str, Tuple[str, str]]) -> None:
    login_url = locators["login_url"][1]
    driver.get(login_url)
    find(driver, locators, "username_input").send_keys("standard_user")
    find(driver, locators, "password_input").send_keys("secret_sauce")
    find(driver, locators, "login_button").click()


def go_to_checkout_step_one(driver: webdriver.Firefox, locators: Dict[str, Tuple[str, str]]) -> None:
    inventory_url = locators["inventory_url"][1]
    driver.get(inventory_url)
    find(driver, locators, "add_backpack_button").click()
    find(driver, locators, "cart_link").click()
    find(driver, locators, "checkout_button").click()


def run_checkout_test(row: dict, locators: Dict[str, Tuple[str, str]]) -> None:
    test_id = row["test_id"]
    first_name = row["first_name"]
    last_name = row["last_name"]
    postal_code = row["postal_code"]
    expected_type = row["expected_type"]
    expected_value = row["expected_value"]

    driver = create_driver()
    try:
        login(driver, locators)
        go_to_checkout_step_one(driver, locators)

        first_name_input = find(driver, locators, "first_name_input")
        last_name_input = find(driver, locators, "last_name_input")
        postal_code_input = find(driver, locators, "postal_code_input")

        first_name_input.clear()
        last_name_input.clear()
        postal_code_input.clear()

        if first_name:
            first_name_input.send_keys(first_name)
        if last_name:
            last_name_input.send_keys(last_name)
        if postal_code:
            postal_code_input.send_keys(postal_code)

        find(driver, locators, "continue_button").click()
        time.sleep(1)

        if expected_type == "error":
            error_elem = find(driver, locators, "error_h3")
            actual = error_elem.text.strip()
        elif expected_type == "title":
            title_elem = find(driver, locators, "title_span")
            actual = title_elem.text.strip()
        else:
            actual = ""

        result = "PASS" if actual == expected_value else "FAIL"
        print(f"[{test_id}] {result} - expected='{expected_value}' actual='{actual}'")
    except Exception as exc:  # noqa: BLE001
        print(f"[{test_id}] ERROR: {exc}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except Exception:
            pass  


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Test data file not found: {DATA_FILE}")
    if not LOCATOR_FILE.exists():
        raise FileNotFoundError(f"Locator file not found: {LOCATOR_FILE}")

    locators = load_locators()

    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            run_checkout_test(row, locators)
            time.sleep(0.5) 


if __name__ == "__main__":
    main()


