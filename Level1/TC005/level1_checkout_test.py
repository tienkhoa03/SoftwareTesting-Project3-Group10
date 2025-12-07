# -*- coding: utf-8 -*-
"""
Level 1 - Data-driven Automation Testing for Checkout
Project #3: Software Testing 2025S1

Test cases: TC-005 series (Checkout validation)
Website: https://sweetshop.netlify.app/
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
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


class Level1CheckoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup once for all tests"""
        cls.test_data = read_test_data_csv('checkout_test_data.csv')
        cls.results = []
    
    def setUp(self):
        """Setup before each test"""
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.wait = WebDriverWait(self.driver, 15)
        self.verificationErrors = []
    
    def test_checkout_all_cases(self):
        """Run all checkout test cases from CSV"""
        driver = self.driver
        wait = self.wait
        
        for idx, test_data in enumerate(self.test_data):
            print(f"\n{'='*60}")
            print(f"Running {test_data['test_case_id']}")
            print(f"{'='*60}")
            
            try:
                # Navigate to website only for first test or after previous test
                if idx == 0:
                    driver.get("https://sweetshop.netlify.app/")
                    
                    # Wait for and click Add to Basket
                    add_to_basket = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add to Basket")))
                    add_to_basket.click()
                    
                    # Wait for and click navbar toggler
                    navbar_toggler = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.navbar-toggler")))
                    navbar_toggler.click()
                    
                    # Wait for and click Basket link
                    basket_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "1 Basket")))
                    basket_link.click()
                    
                    # Wait for checkout form to load
                    wait.until(EC.presence_of_element_located((By.ID, "name")))
                    time.sleep(1)  # Small buffer for form to fully render
                else:
                    # For subsequent tests, just wait for form to be ready
                    wait.until(EC.element_to_be_clickable((By.ID, "name")))
                
                # Fill checkout form
                name_field = driver.find_element(By.ID, "name")
                name_field.clear()
                name_field.send_keys(test_data['first_name'])
                
                driver.find_element(By.XPATH, "//form/div/div[2]/input").clear()
                driver.find_element(By.XPATH, "//form/div/div[2]/input").send_keys(test_data['last_name'])
                
                driver.find_element(By.ID, "email").clear()
                driver.find_element(By.ID, "email").send_keys(test_data['email'])
                
                Select(driver.find_element(By.ID, "country")).select_by_visible_text(test_data['country'])
                time.sleep(1)
                
                Select(driver.find_element(By.ID, "city")).select_by_visible_text(test_data['city'])
                
                driver.find_element(By.ID, "address").clear()
                driver.find_element(By.ID, "address").send_keys(test_data['address'])
                
                driver.find_element(By.ID, "zip").clear()
                driver.find_element(By.ID, "zip").send_keys(test_data['zip'])
                
                driver.find_element(By.ID, "cc-name").clear()
                driver.find_element(By.ID, "cc-name").send_keys(test_data['card_name'])
                
                driver.find_element(By.ID, "cc-number").clear()
                driver.find_element(By.ID, "cc-number").send_keys(test_data['card_number'])
                
                driver.find_element(By.ID, "cc-expiration").clear()
                driver.find_element(By.ID, "cc-expiration").send_keys(test_data['card_expiration'])
                
                driver.find_element(By.ID, "cc-cvv").clear()
                driver.find_element(By.ID, "cc-cvv").send_keys(test_data['cvv'])
                
                # Submit form
                driver.find_element(By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Security code required'])[1]/following::button[1]").click()
                time.sleep(2)
                
                # Verify result
                try:
                    actual_text = driver.find_element(By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Name on card'])[1]/following::small[1]").text
                    self.assertEqual(test_data['expected_result'], actual_text)
                    print(f"[PASS]")
                    self.results.append({'test_case': test_data['test_case_id'], 'passed': True})
                except AssertionError as e:
                    self.verificationErrors.append(str(e))
                    print(f"[FAIL]")
                    self.results.append({'test_case': test_data['test_case_id'], 'passed': False})
                
            except Exception as e:
                print(f"[ERROR]: {e}")
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
            print("TEST SUMMARY - LEVEL 1 CHECKOUT")
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
