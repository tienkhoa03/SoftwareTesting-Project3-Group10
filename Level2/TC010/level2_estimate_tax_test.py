# -*- coding: utf-8 -*-
"""
Level 2 - Advanced Data-driven Automation Testing for Estimate Tax
Project #3: Software Testing 2025S1

Features:
- Dynamic element locators from JSON config
- Configurable URLs and timeouts
- Flexible test data structure
- Enhanced error handling
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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


class Level2EstimateTaxTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup once for all tests"""
        cls.config = load_config('level2_config.json', 'estimate_tax_test')
        cls.test_data = read_test_data_csv('estimate_tax_test_data.csv')
        cls.results = []
    
    def setUp(self):
        """Setup before each test"""
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.verificationErrors = []
    
    def get_element(self, locator_key):
        """Get element using locator from config"""
        locator = self.config['locators'][locator_key]
        by_type = self._get_by_type(locator['type'])
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
    
    def test_estimate_tax_all_cases(self):
        """Run all estimate tax test cases from CSV"""
        driver = self.driver
        wait = WebDriverWait(driver, 20)
        
        for idx, test_data in enumerate(self.test_data):
            print(f"\n{'='*60}")
            print(f"Running {test_data['test_case_id']}")
            print(f"{'='*60}")
            
            try:
                # Navigate only for first test
                if idx == 0:
                    # Navigate and add to cart
                    driver.get(self.config['product_url'])
                    time.sleep(3)
                    
                    # Try multiple strategies to click Add to Cart
                    try:
                        # Use CSS selector for the visible button
                        add_to_cart_btn = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button-cart.btn-cart"))
                        )
                        # Scroll to button
                        driver.execute_script("arguments[0].scrollIntoView(true);", add_to_cart_btn)
                        time.sleep(1)
                        add_to_cart_btn.click()
                        time.sleep(3)
                    except (TimeoutException, Exception) as e:
                        print(f"⚠ Primary locator failed: {e}, trying alternative...")
                        try:
                            btn = driver.find_element(By.XPATH, "//button[@title='Add to Cart' and contains(@class, 'button-cart')]")
                            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(3)
                        except Exception as e2:
                            print(f"⚠ All locators failed: {e2}")
                            raise
                    
                    driver.get(self.config['cart_url'])
                    time.sleep(3)
                    
                    # Wait for and expand estimate section using the accordion header
                    try:
                        # Try to find the collapsed accordion header
                        estimate_header = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "h5[data-target='#collapse-shipping']"))
                        )
                        
                        # Scroll the element into view
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", estimate_header)
                        time.sleep(1)
                        
                        # Check if it's already expanded
                        collapse_div = driver.find_element(By.ID, "collapse-shipping")
                        if "show" not in collapse_div.get_attribute("class"):
                            # Click to expand
                            estimate_header.click()
                            time.sleep(2)
                        else:
                            print("Estimate section already expanded")
                            time.sleep(1)
                    except Exception as e:
                        print(f"Error expanding estimate section: {str(e)}")
                        print(f"Current URL: {driver.current_url}")
                        raise
                else:
                    time.sleep(1)
                
                # Fill shipping form
                wait.until(EC.presence_of_element_located((By.ID, "input-country")))
                
                if test_data['country']:
                    country_elem = self.get_element('country')
                    country_elem.click()
                    Select(country_elem).select_by_visible_text(test_data['country'])
                    time.sleep(1)
                
                if test_data['region']:
                    region_elem = self.get_element('region')
                    region_elem.click()
                    Select(region_elem).select_by_visible_text(test_data['region'])
                    time.sleep(1)
                
                postcode_elem = self.get_element('postcode')
                postcode_elem.click()
                postcode_elem.clear()
                if test_data['postcode']:
                    postcode_elem.send_keys(test_data['postcode'])
                
                # Get quotes
                self.get_element('get_quotes').click()
                time.sleep(2)
                
                # Verify result
                try:
                    if test_data['expected_type'] == "shipping_rate":
                        # Wait for modal to appear
                        wait.until(EC.presence_of_element_located((By.ID, "modal-shipping")))
                        time.sleep(1)
                        
                        # Verify shipping rate text
                        actual_text = wait.until(
                            EC.presence_of_element_located((By.XPATH, "//div[@id='modal-shipping']//label"))
                        ).text
                        
                        if test_data['expected_result'] in actual_text:
                            print(f"[PASS]")
                            self.results.append({'test_case': test_data['test_case_id'], 'passed': True})
                        else:
                            print(f"[FAIL] Expected: {test_data['expected_result']}, Got: {actual_text}")
                            self.results.append({'test_case': test_data['test_case_id'], 'passed': False})
                        
                        # Close the modal
                        try:
                            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#modal-shipping .close")))
                            close_btn.click()
                            time.sleep(1)
                        except:
                            # Alternative: Use JavaScript to close modal
                            driver.execute_script("arguments[0].style.display='none';", 
                                                driver.find_element(By.ID, "modal-shipping"))
                            time.sleep(1)
                        
                        # Remove modal backdrop and clean up modal state
                        driver.execute_script("""
                            var modal = document.getElementById('modal-shipping');
                            if (modal) modal.remove();
                            var backdrops = document.querySelectorAll('.modal-backdrop');
                            backdrops.forEach(function(backdrop) { backdrop.remove(); });
                            document.body.classList.remove('modal-open');
                            document.body.style.overflow = '';
                            document.body.style.paddingRight = '';
                        """)
                        time.sleep(1)
                    else:
                        error = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.alert-danger"))
                        ).text
                        if test_data['expected_result'] in error:
                            print(f"[PASS]")
                            self.results.append({'test_case': test_data['test_case_id'], 'passed': True})
                        else:
                            print(f"[FAIL] Expected: {test_data['expected_result']}, Got: {error}")
                            self.results.append({'test_case': test_data['test_case_id'], 'passed': False})
                except Exception as e:
                    print(f"[FAIL] Exception: {str(e)}")
                    self.results.append({'test_case': test_data['test_case_id'], 'passed': False})
                    
            except Exception as e:
                print(f"[ERROR]: {e}")
                self.results.append({'test_case': test_data['test_case_id'], 'passed': False})
            
            # Clean up any remaining modals and backdrops between tests
            try:
                driver.execute_script("""
                    var modals = document.querySelectorAll('.modal');
                    modals.forEach(function(modal) { modal.remove(); });
                    var backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(function(backdrop) { backdrop.remove(); });
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                """)
            except:
                pass
    
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
            print("TEST SUMMARY - LEVEL 2 ESTIMATE TAX")
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
