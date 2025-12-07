# -*- coding: utf-8 -*-
"""
Level 2 - Advanced Data-driven Automation Testing for Checkout
Project #3: Software Testing 2025S1

Features:
- Dynamic element locators from JSON config
- Configurable URLs and timeouts
- Flexible test data structure
- Enhanced error handling
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import csv
import json
import time
import unittest


def read_test_data_csv(filename):
    """Read test data from CSV file"""
    test_data = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            test_data.append(row)
    return test_data


def load_config(config_file, test_key):
    """Load configuration from JSON file"""
    with open(config_file, 'r', encoding='utf-8') as file:
        config_data = json.load(file)
    return config_data[test_key]


class Level2CheckoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup once for all tests"""
        cls.config = load_config('level2_config.json', 'checkout_test')
        cls.test_data = read_test_data_csv('checkout_test_data.csv')
        cls.results = []
    
    def setUp(self):
        """Setup before each test"""
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(30)
        self.wait = WebDriverWait(self.driver, 15)
        self.verificationErrors = []
    
    def get_element(self, locator_key, wait_for_clickable=False, wait_for_visible=False):
        """Get element using locator from config"""
        locator = self.config['locators'][locator_key]
        by_type = self._get_by_type(locator['type'])
        
        if wait_for_clickable:
            return self.wait.until(EC.element_to_be_clickable((by_type, locator['value'])))
        elif wait_for_visible:
            return self.wait.until(EC.visibility_of_element_located((by_type, locator['value'])))
        else:
            return self.driver.find_element(by_type, locator['value'])
    
    def _get_by_type(self, by_string):
        """Convert string to By type"""
        by_mapping = {
            'id': By.ID,
            'name': By.NAME,
            'xpath': By.XPATH,
            'css': By.CSS_SELECTOR,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT
        }
        return by_mapping.get(by_string, By.XPATH)
    
    def test_checkout_all_cases(self):
        """Run all checkout test cases from CSV"""
        driver = self.driver
        wait = self.wait
        
        for idx, test_data in enumerate(self.test_data):
            print(f"\n{'='*60}")
            print(f"Running {test_data['test_case_id']}")
            print(f"{'='*60}")
            
            try:
                # Navigate only for first test
                if idx == 0:
                    driver.get(self.config['base_url'])
                    time.sleep(2)
                    
                    # Wait for and click Add to Basket
                    add_to_basket = self.get_element('add_to_basket', wait_for_clickable=True)
                    add_to_basket.click()
                    time.sleep(2)
                    
                    # Try to find the basket link - it might be visible without toggling navbar
                    try:
                        # First try direct basket link (might be visible on larger screens)
                        locator = self.config['locators']['basket_link']
                        by_type = self._get_by_type(locator['type'])
                        basket_link = driver.find_element(by_type, locator['value'])
                        if basket_link.is_displayed():
                            basket_link.click()
                        else:
                            raise NoSuchElementException("Basket link not visible")
                    except (NoSuchElementException, Exception):
                        # If basket link not visible, toggle navbar first
                        navbar_toggler = self.get_element('navbar_toggle', wait_for_clickable=True)
                        navbar_toggler.click()
                        time.sleep(1)
                        
                        basket_link = self.get_element('basket_link', wait_for_clickable=True)
                        basket_link.click()
                    
                    # Wait for checkout form to load
                    self.get_element('first_name', wait_for_visible=True)
                    time.sleep(2)  # Buffer for form to fully render
                else:
                    # For subsequent tests, scroll to top and wait for form to be ready
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                    self.get_element('first_name', wait_for_clickable=True)
                
                # Fill checkout form
                self.get_element('first_name').clear()
                self.get_element('first_name').send_keys(test_data['first_name'])
                
                self.get_element('last_name').clear()
                self.get_element('last_name').send_keys(test_data['last_name'])
                
                self.get_element('email').clear()
                self.get_element('email').send_keys(test_data['email'])
                
                Select(self.get_element('country')).select_by_visible_text(test_data['country'])
                time.sleep(1)
                
                Select(self.get_element('city')).select_by_visible_text(test_data['city'])
                
                self.get_element('address').clear()
                self.get_element('address').send_keys(test_data['address'])
                
                self.get_element('zip').clear()
                self.get_element('zip').send_keys(test_data['zip'])
                
                self.get_element('card_name').clear()
                self.get_element('card_name').send_keys(test_data['card_name'])
                
                self.get_element('card_number').clear()
                self.get_element('card_number').send_keys(test_data['card_number'])
                
                self.get_element('card_expiration').clear()
                self.get_element('card_expiration').send_keys(test_data['card_expiration'])
                
                self.get_element('cvv').clear()
                self.get_element('cvv').send_keys(test_data['cvv'])
                
                # Submit form
                submit_button = self.get_element('submit_button', wait_for_clickable=True)
                submit_button.click()
                
                # Wait for result/validation message to appear
                time.sleep(2)
                
                # Verify result
                try:
                    # Wait for the validation message element to be present
                    result_element = self.get_element('verify_text', wait_for_visible=True)
                    actual_text = result_element.text
                    print(f"Expected: '{test_data['expected_result']}'")
                    print(f"Actual: '{actual_text}'")
                    self.assertEqual(test_data['expected_result'], actual_text)
                    print(f"[PASS]")
                    self.results.append({'test_case': test_data['test_case_id'], 'passed': True})
                except AssertionError as e:
                    self.verificationErrors.append(str(e))
                    print(f"[FAIL] - Assertion failed")
                    self.results.append({'test_case': test_data['test_case_id'], 'passed': False})
                except Exception as e:
                    print(f"[FAIL] - Could not find result element: {str(e)}")
                    self.results.append({'test_case': test_data['test_case_id'], 'passed': False})
                
            except Exception as e:
                import traceback
                print(f"[ERROR]: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                traceback.print_exc()
                self.results.append({'test_case': test_data['test_case_id'], 'passed': False})
    
    def is_element_present(self, how, what):
        """Check if element is present"""
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True
    
    def tearDown(self):
        """Cleanup after test"""
        self.driver.quit()
        
        # Print summary if results exist
        if self.results:
            print(f"\n{'='*60}")
            print("TEST SUMMARY - LEVEL 2 CHECKOUT")
            print(f"{'='*60}")
            total = len(self.results)
            passed = sum(1 for r in self.results if r['passed'])
            failed = total - passed
            
            print(f"Total tests: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {failed}")
            print(f"Success rate: {(passed/total)*100:.2f}%")
            
            print("\nDetailed results:")
            for result in self.results:
                status = "[PASS]" if result['passed'] else "[FAIL]"
                print(f"  {result['test_case']}: {status}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
