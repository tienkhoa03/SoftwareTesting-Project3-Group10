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
DATA_FILE = PROJECT_ROOT / "data" / "cart_data.csv"
LOCATOR_FILE = PROJECT_ROOT / "data" / "locators.csv"
GECKODRIVER_PATH = PROJECT_ROOT / "geckodriver.exe"


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
    if loc_type == "url":
        return value  # Return URL string
    raise ValueError(f"Unsupported locator type: {loc_type}")


def login(driver: webdriver.Firefox, locators: Dict[str, Tuple[str, str]]) -> None:
    login_url = locators["login_url"][1]
    driver.get(login_url)
    find(driver, locators, "username_input").send_keys("standard_user")
    find(driver, locators, "password_input").send_keys("secret_sauce")
    find(driver, locators, "login_button").click()


def add_item_to_cart(driver: webdriver.Firefox, locators: Dict[str, Tuple[str, str]], item_name: str) -> None:
    """Add an item to cart by item name using locators."""
    item_map = {
        "backpack": "add_backpack_button",
        "bike-light": "add_bike_light_button",
        "bolt-t-shirt": "add_bolt_t_shirt_button",
        "fleece-jacket": "add_fleece_jacket_button",
        "onesie": "add_onesie_button",
        "red-t-shirt": "add_red_t_shirt_button",
    }
    if item_name in item_map:
        find(driver, locators, item_map[item_name]).click()


def remove_item_from_cart(driver: webdriver.Firefox, locators: Dict[str, Tuple[str, str]], item_name: str) -> None:
    """Remove an item from cart by item name using locators."""
    item_map = {
        "backpack": "remove_backpack_button",
        "bike-light": "remove_bike_light_button",
        "bolt-t-shirt": "remove_bolt_t_shirt_button",
        "fleece-jacket": "remove_fleece_jacket_button",
        "onesie": "remove_onesie_button",
        "red-t-shirt": "remove_red_t_shirt_button",
    }
    if item_name in item_map:
        find(driver, locators, item_map[item_name]).click()


def get_cart_badge_count(driver: webdriver.Firefox, locators: Dict[str, Tuple[str, str]]) -> str:
    """Get the cart badge count. Returns empty string if badge doesn't exist."""
    try:
        badge = find(driver, locators, "cart_badge")
        return badge.text.strip()
    except Exception:
        return ""


def run_cart_test(row: dict, locators: Dict[str, Tuple[str, str]]) -> None:
    test_id = row["test_id"]
    action = row["action"]
    items_to_add = row["items_to_add"].strip() if row["items_to_add"] else ""
    items_to_remove = row["items_to_remove"].strip() if row["items_to_remove"] else ""
    initial_cart_count = row["initial_cart_count"].strip() if row["initial_cart_count"] else "0"
    verify_type = row["verify_type"]
    verify_value = row["verify_value"]
    expected_result = row["expected_result"]

    driver = create_driver()
    try:
        # Handle login requirement
        if action != "add_without_login":
            login(driver, locators)
            time.sleep(1)

        # Navigate to inventory page
        if action != "navigate_cart" and action != "add_without_login":
            inventory_url = locators["inventory_url"][1]
            driver.get(inventory_url)
            time.sleep(1)

        # Handle initial cart count setup (for TC-008-006)
        if initial_cart_count and initial_cart_count != "0":
            # Add items to reach initial count
            if initial_cart_count == "2":
                add_item_to_cart(driver, locators, "backpack")
                add_item_to_cart(driver, locators, "bike-light")
                time.sleep(0.5)

        # Perform actions
        if action == "navigate_cart":
            # TC-008-001: Navigate to cart and verify title
            inventory_url = locators["inventory_url"][1]
            driver.get(inventory_url)
            time.sleep(1)
            cart_url = locators["cart_url"][1]
            driver.get(cart_url)
            time.sleep(1)
            find(driver, locators, "cart_link").click()
            time.sleep(1)
        elif action == "add_all_items":
            inventory_url = locators["inventory_url"][1]
            driver.get(inventory_url)
            time.sleep(1)
            for item in items_to_add.split():
                add_item_to_cart(driver, locators, item)
                time.sleep(0.3)
        elif action == "add_and_continue_shopping":
            add_item_to_cart(driver, locators, items_to_add.split()[0])
            time.sleep(0.5)
            find(driver, locators, "cart_link").click()
            time.sleep(1)
            # Verify item in cart
            item_name_elem = find(driver, locators, "item_name_in_cart")
            if item_name_elem.text.strip() == "Sauce Labs Backpack":
                find(driver, locators, "continue_shopping_button").click()
                time.sleep(1)
        elif action == "add_without_login":
            # TC-008-004: Login, navigate to inventory, delete cookie before adding item
            login(driver, locators)
            time.sleep(1)
            inventory_url = locators["inventory_url"][1]
            driver.get(inventory_url)
            time.sleep(1)
            # Delete cookie right before adding item to simulate expired session
            driver.delete_cookie("session-username")
            add_item_to_cart(driver, locators, items_to_add.split()[0])
            time.sleep(0.5)
            find(driver, locators, "cart_link").click()
            time.sleep(1)
        elif action == "add_one_item":
            add_item_to_cart(driver, locators, items_to_add.split()[0])
            time.sleep(0.5)
        elif action == "verify_and_remove":
            # Cart should already have items (from initial_cart_count)
            remove_item_from_cart(driver, locators, items_to_remove.split()[0])
            time.sleep(0.5)
        elif action == "complex_flow":
            # TC-008-007: Add items, verify remove buttons, go to cart, remove items, verify badge, continue shopping, verify add buttons
            # Add items one by one
            for item in items_to_add.split():
                add_item_to_cart(driver, locators, item)
                time.sleep(0.3)
            # Go to cart
            find(driver, locators, "cart_link").click()
            time.sleep(1)
            # Remove items from cart
            for item in items_to_remove.split():
                remove_item_from_cart(driver, locators, item)
                time.sleep(0.3)
            # Continue shopping
            find(driver, locators, "continue_shopping_button").click()
            time.sleep(1)

        # Verify results
        actual = ""
        if verify_type == "title":
            title_elem = find(driver, locators, "title_span")
            actual = title_elem.text.strip()
        elif verify_type == "cart_badge":
            actual = get_cart_badge_count(driver, locators)
        elif verify_type == "remove_button":
            # After continuing shopping, verify remove button appears on inventory page
            remove_map = {
                "backpack": "remove_backpack_button",
                "bike-light": "remove_bike_light_button",
                "bolt-t-shirt": "remove_bolt_t_shirt_button",
            }
            item_key = items_to_add.split()[0]
            if item_key in remove_map:
                remove_button = find(driver, locators, remove_map[item_key])
                actual = remove_button.text.strip()
        elif verify_type == "error":
            if action == "add_without_login":
                error_elem = find(driver, locators, "login_error_h3")
            else:
                error_elem = find(driver, locators, "error_h3")
            actual = error_elem.text.strip()
        elif verify_type == "item_in_cart":
            item_name_elem = find(driver, locators, "item_name_in_cart")
            actual = item_name_elem.text.strip()
        elif verify_type == "add_button":
            # Verify add button text after removing items and continuing shopping
            add_map = {
                "backpack": "add_backpack_button",
                "bike-light": "add_bike_light_button",
                "bolt-t-shirt": "add_bolt_t_shirt_button",
            }
            # Check first item's add button
            first_item = items_to_add.split()[0] if items_to_add else ""
            if first_item in add_map:
                add_button = find(driver, locators, add_map[first_item])
                actual = add_button.text.strip()

        result = "PASS" if actual == expected_result else "FAIL"
        print(f"[{test_id}] {result} - expected='{expected_result}' actual='{actual}'")
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
            run_cart_test(row, locators)
            time.sleep(0.5)


if __name__ == "__main__":
    main()

