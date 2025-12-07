import csv
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "cart_data.csv"
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
    time.sleep(0.5)  # Wait for page to load
    driver.find_element(By.ID, "user-name").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()
    time.sleep(0.5)  # Wait for login to complete


def clear_cart(driver) -> None:
    """Clear all items from cart if any exist."""
    try:
        login(driver)
        time.sleep(0.5)
        
        driver.get(SAUCE_BASE_URL + "cart.html")
        time.sleep(0.5)
        # Remove all items from cart
        while True:
            try:
                remove_btn = driver.find_element(By.CSS_SELECTOR, "button.btn.btn_secondary.btn_small.cart_button")
                remove_btn.click()
                time.sleep(0.3)
            except:
                break
    except:
        pass


def add_item_to_cart(driver, item_name: str) -> None:
    """Add an item to cart by item name."""
    item_map = {
        "backpack": "add-to-cart-sauce-labs-backpack",
        "bike-light": "add-to-cart-sauce-labs-bike-light",
        "bolt-t-shirt": "add-to-cart-sauce-labs-bolt-t-shirt",
        "fleece-jacket": "add-to-cart-sauce-labs-fleece-jacket",
        "onesie": "add-to-cart-sauce-labs-onesie",
        "red-t-shirt": "add-to-cart-test.allthethings()-t-shirt-(red)",
    }
    if item_name in item_map:
        driver.find_element(By.ID, item_map[item_name]).click()


def remove_item_from_cart(driver, item_name: str) -> None:
    """Remove an item from cart by item name."""
    item_map = {
        "backpack": "remove-sauce-labs-backpack",
        "bike-light": "remove-sauce-labs-bike-light",
        "bolt-t-shirt": "remove-sauce-labs-bolt-t-shirt",
        "fleece-jacket": "remove-sauce-labs-fleece-jacket",
        "onesie": "remove-sauce-labs-onesie",
        "red-t-shirt": "remove-test.allthethings()-t-shirt-(red)",
    }
    if item_name in item_map:
        driver.find_element(By.ID, item_map[item_name]).click()


def get_cart_badge_count(driver) -> str:
    """Get the cart badge count. Returns empty string if badge doesn't exist."""
    try:
        badge = driver.find_element(By.CSS_SELECTOR, "span.shopping_cart_badge")
        return badge.text.strip()
    except Exception:
        return ""


def run_cart_test(row: dict, driver: webdriver.Firefox) -> str:
    """Run a single cart test case. Returns 'PASS' or 'FAIL'."""
    test_id = row["test_id"]
    action = row["action"]
    items_to_add = row["items_to_add"].strip() if row["items_to_add"] else ""
    items_to_remove = row["items_to_remove"].strip() if row["items_to_remove"] else ""
    initial_cart_count = row["initial_cart_count"].strip() if row["initial_cart_count"] else "0"
    verify_type = row["verify_type"]
    verify_value = row["verify_value"]
    expected_result = row["expected_result"]

    try:
        # Clear cart before each test to ensure clean state
        if action != "add_without_login":
            clear_cart(driver)

        if action != "add_without_login":
            login(driver)
            time.sleep(0.5)

        if action != "navigate_cart" and action != "add_without_login":
            driver.get(SAUCE_BASE_URL + "inventory.html")
            time.sleep(1)

        # Handle initial cart count setup (for TC-008-006)
        if initial_cart_count and initial_cart_count != "0":
            # Add items to reach initial count
            if initial_cart_count == "2":
                add_item_to_cart(driver, "backpack")
                add_item_to_cart(driver, "bike-light")
                time.sleep(0.5)

        # Perform actions
        if action == "navigate_cart":
            # TC-008-001: Navigate to cart and verify title
            driver.get(SAUCE_BASE_URL + "inventory.html")
            time.sleep(1)
            driver.get(SAUCE_BASE_URL + "cart.html")
            time.sleep(1)
            driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
            time.sleep(1)
        elif action == "add_all_items":
            driver.get(SAUCE_BASE_URL + "inventory.html")
            time.sleep(1)
            for item in items_to_add.split():
                add_item_to_cart(driver, item)
                time.sleep(0.3)
        elif action == "add_and_continue_shopping":
            add_item_to_cart(driver, items_to_add.split()[0])
            time.sleep(0.5)
            driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
            time.sleep(1)
            # Verify item in cart
            item_name_elem = driver.find_element(By.XPATH, "//a[@id='item_4_title_link']/div")
            if item_name_elem.text.strip() == "Sauce Labs Backpack":
                driver.find_element(By.ID, "continue-shopping").click()
                time.sleep(1)
        elif action == "add_without_login":
            # TC-008-004: Login, navigate to inventory, delete cookie before adding item
            login(driver)
            time.sleep(1)
            driver.get(SAUCE_BASE_URL + "inventory.html")
            time.sleep(1)
            # Delete cookie right before adding item to simulate expired session
            driver.delete_cookie("session-username")
            time.sleep(0.5)
            try:
                add_item_to_cart(driver, items_to_add.split()[0])
                time.sleep(0.5)
            except Exception:
                pass
            try:
                driver.get(SAUCE_BASE_URL + "cart.html")
                time.sleep(1)
            except Exception:
                pass
        elif action == "add_one_item":
            add_item_to_cart(driver, items_to_add.split()[0])
            time.sleep(0.5)
        elif action == "verify_and_remove":
            # Cart should already have items (from initial_cart_count)
            remove_item_from_cart(driver, items_to_remove.split()[0])
            time.sleep(0.5)
        elif action == "complex_flow":
            # TC-008-007: Add items, verify remove buttons, go to cart, remove items, verify badge, continue shopping, verify add buttons
            # Add items one by one and verify remove buttons appear
            for item in items_to_add.split():
                add_item_to_cart(driver, item)
                time.sleep(0.3)
                # Verify remove button appears
                remove_id_map = {
                    "backpack": "remove-sauce-labs-backpack",
                    "bike-light": "remove-sauce-labs-bike-light",
                    "bolt-t-shirt": "remove-sauce-labs-bolt-t-shirt",
                }
                if item in remove_id_map:
                    badge_count = get_cart_badge_count(driver)
                    # Verify badge updates
            # Go to cart
            driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
            time.sleep(1)
            # Remove items from cart
            for item in items_to_remove.split():
                remove_item_from_cart(driver, item)
                time.sleep(0.3)
            # Continue shopping
            driver.find_element(By.ID, "continue-shopping").click()
            time.sleep(1)

        # Verify results
        actual = ""
        if verify_type == "title":
            title_elem = driver.find_element(
                By.CSS_SELECTOR,
                "div#header_container div.header_secondary_container span.title",
            )
            actual = title_elem.text.strip()
        elif verify_type == "cart_badge":
            actual = get_cart_badge_count(driver)
        elif verify_type == "remove_button":
            # After continuing shopping, verify remove button appears on inventory page
            remove_id_map = {
                "backpack": "remove-sauce-labs-backpack",
                "bike-light": "remove-sauce-labs-bike-light",
                "bolt-t-shirt": "remove-sauce-labs-bolt-t-shirt",
            }
            item_key = items_to_add.split()[0]
            if item_key in remove_id_map:
                remove_button = driver.find_element(By.ID, remove_id_map[item_key])
                actual = remove_button.text.strip()
        elif verify_type == "error":
            if action == "add_without_login":
                error_elem = driver.find_element(
                    By.XPATH,
                    "//div[@id='login_button_container']/div/form/div[3]/h3",
                )
            else:
                error_elem = driver.find_element(
                    By.XPATH,
                    "//div[@id='checkout_info_container']/div/form/div/div[4]/h3",
                )
            actual = error_elem.text.strip()
        elif verify_type == "item_in_cart":
            item_name_elem = driver.find_element(By.XPATH, "//a[@id='item_4_title_link']/div")
            actual = item_name_elem.text.strip()
        elif verify_type == "add_button":
            # Verify add button text after removing items and continuing shopping
            add_id_map = {
                "backpack": "add-to-cart-sauce-labs-backpack",
                "bike-light": "add-to-cart-sauce-labs-bike-light",
                "bolt-t-shirt": "add-to-cart-sauce-labs-bolt-t-shirt",
            }
            # Check first item's add button
            first_item = items_to_add.split()[0] if items_to_add else ""
            if first_item in add_id_map:
                add_button = driver.find_element(By.ID, add_id_map[first_item])
                actual = add_button.text.strip()

        result = "PASS" if actual == expected_result else "FAIL"
        print(f"[{test_id}] {result} - expected='{expected_result}' actual='{actual}'")
        return result
    except Exception as exc:  # noqa: BLE001
        print(f"[{test_id}] ERROR: {exc}")
        import traceback
        traceback.print_exc()
        return "FAIL" 


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Test data file not found: {DATA_FILE}")

    driver = create_driver()
    try:
        with DATA_FILE.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                run_cart_test(row, driver)
                time.sleep(0.5)
    finally:
        try:
            driver.quit()
        except Exception:
            pass 


if __name__ == "__main__":
    main()

