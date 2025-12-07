import csv
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "checkout_data.csv"
SAUCE_BASE_URL = "https://www.saucedemo.com/"
GECKODRIVER_PATH = PROJECT_ROOT / "geckodriver.exe"


def create_driver() -> webdriver.Firefox:
    """Create and return a Firefox WebDriver instance."""
    opts = Options()
    opts.add_argument("--start-maximized")

    service = Service(GeckoDriverManager().install())
    # service = Service(str(GECKODRIVER_PATH))
    driver = webdriver.Firefox(service=service, options=opts)
    driver.implicitly_wait(5)
    return driver


def login(driver, username: str = "standard_user", password: str = "secret_sauce") -> None:
    driver.get(SAUCE_BASE_URL)
    driver.find_element(By.ID, "user-name").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()


def go_to_checkout_step_one(driver) -> None:
    """Mimic the flow to reach checkout step one page."""
    driver.get(SAUCE_BASE_URL + "inventory.html")
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    driver.find_element(By.ID, "checkout").click()


def run_checkout_test(row: dict) -> None:
    test_id = row["test_id"]
    first_name = row["first_name"]
    last_name = row["last_name"]
    postal_code = row["postal_code"]
    expected_type = row["expected_type"]
    expected_value = row["expected_value"]

    driver = create_driver()
    try:
        login(driver)
        go_to_checkout_step_one(driver)

        first_name_input = driver.find_element(By.ID, "first-name")
        last_name_input = driver.find_element(By.ID, "last-name")
        postal_code_input = driver.find_element(By.ID, "postal-code")

        first_name_input.clear()
        last_name_input.clear()
        postal_code_input.clear()

        if first_name:
            first_name_input.send_keys(first_name)
        if last_name:
            last_name_input.send_keys(last_name)
        if postal_code:
            postal_code_input.send_keys(postal_code)

        driver.find_element(By.ID, "continue").click()
        time.sleep(1)

        if expected_type == "error":
            error_elem = driver.find_element(
                By.XPATH,
                "//div[@id='checkout_info_container']/div/form/div/div[4]/h3",
            )
            actual = error_elem.text.strip()
        elif expected_type == "title":
            title_elem = driver.find_element(
                By.CSS_SELECTOR,
                "div#header_container div.header_secondary_container span.title",
            )
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

    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            run_checkout_test(row)
            time.sleep(0.5) 


if __name__ == "__main__":
    main()


