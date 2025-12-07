# -*- coding: utf-8 -*-
"""
Level 1 - Data-driven Automation Testing for Estimate Shipping & Taxes
Project #3: Software Testing 2025S1

Test cases: TC-010 series (Estimate shipping & tax validation)
Website: https://ecommerce-playground.lambdatest.io/
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import csv
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


class Level1EstimateTaxTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup once for all tests"""
        cls.test_data = read_test_data_csv('estimate_tax_test_data.csv')
        cls.results = []
    
    def setUp(self):
        """Setup before each test"""
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.verificationErrors = []
    
    def test_estimate_tax_all_cases(self):
        """Run all estimate tax test cases from CSV"""
        driver = self.driver
        wait = WebDriverWait(driver, 20)
        
        for idx, test_data in enumerate(self.test_data):
            print(f"\n{'='*60}")
            print(f"Running {test_data['test_case_id']}")
            print(f"{'='*60}")
            
            try:
                # Navigate to website only for first test
                if idx == 0:
                    # Navigate to product page directly
                    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=product/product&product_id=56")
                    
                    # Wait for page to load completely
                    time.sleep(3)
                    
                    # Wait for and click Add to Cart button - using the visible button in product details
                    try:
                        # Primary locator - button with both btn-cart and button-cart classes (not in mobile-only section)
                        add_to_cart_btn = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button-cart.btn-cart"))
                        )
                        # Scroll to button to ensure it's in view
                        driver.execute_script("arguments[0].scrollIntoView(true);", add_to_cart_btn)
                        time.sleep(1)
                        add_to_cart_btn.click()
                        time.sleep(3)
                    except (TimeoutException, Exception) as e:
                        print(f"⚠ Primary locator failed: {e}, trying alternative...")
                        try:
                            # Try by title attribute as fallback
                            add_to_cart_btn = driver.find_element(By.XPATH, "//button[@title='Add to Cart' and contains(@class, 'button-cart')]")
                            driver.execute_script("arguments[0].scrollIntoView(true);", add_to_cart_btn)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", add_to_cart_btn)
                            time.sleep(3)
                        except Exception as e2:
                            print(f"⚠ All locators failed: {e2}")
                            raise
                    
                    # Navigate to cart page
                    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=checkout/cart")
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
                    # For subsequent tests, just wait
                    time.sleep(1)                # Fill shipping form
                # Wait for form to be ready
                wait.until(EC.presence_of_element_located((By.ID, "input-country")))
                
                if test_data['country']:
                    driver.find_element(By.ID, "input-country").click()
                    Select(driver.find_element(By.ID, "input-country")).select_by_visible_text(test_data['country'])
                    time.sleep(1)
                
                if test_data['region']:
                    driver.find_element(By.ID, "input-zone").click()
                    Select(driver.find_element(By.ID, "input-zone")).select_by_visible_text(test_data['region'])
                    time.sleep(1)
                
                driver.find_element(By.ID, "input-postcode").click()
                driver.find_element(By.ID, "input-postcode").clear()
                if test_data['postcode']:
                    driver.find_element(By.ID, "input-postcode").send_keys(test_data['postcode'])
                
                # Get quotes
                driver.find_element(By.ID, "button-quote").click()
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
                        
                        # Close the modal by clicking the close button
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
                except AssertionError as e:
                    self.verificationErrors.append(str(e))
                    print(f"[FAIL] Assertion: {str(e)}")
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
            print("TEST SUMMARY - LEVEL 1 ESTIMATE TAX")
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
