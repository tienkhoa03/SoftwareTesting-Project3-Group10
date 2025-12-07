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
from selenium.webdriver.support.ui import Select
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
        
        for idx, test_data in enumerate(self.test_data):
            print(f"\n{'='*60}")
            print(f"Running {test_data['test_case_id']}")
            print(f"{'='*60}")
            
            try:
                # Navigate only for first test
                if idx == 0:
                    # Navigate and add to cart
                    driver.get(self.config['product_url'])
                    time.sleep(2)
                    
                    self.get_element('add_to_cart').click()
                    time.sleep(2)
                    
                    driver.get(self.config['cart_url'])
                    time.sleep(2)
                    
                    # Expand estimate section
                    self.get_element('estimate_link').click()
                    time.sleep(1)
                else:
                    time.sleep(1)
                
                # Fill shipping form
                if test_data['country']:
                    Select(self.get_element('country')).select_by_visible_text(test_data['country'])
                    time.sleep(1)
                
                if test_data['region']:
                    Select(self.get_element('region')).select_by_visible_text(test_data['region'])
                    time.sleep(1)
                
                self.get_element('postcode').clear()
                if test_data['postcode']:
                    self.get_element('postcode').send_keys(test_data['postcode'])
                
                # Get quotes
                self.get_element('get_quotes').click()
                time.sleep(2)
                
                # Verify result
                try:
                    if test_data['expected_type'] == "shipping_rate":
                        driver.find_element(By.XPATH, f"//label[contains(text(),'{test_data['expected_result']}')]")
                        print(f"[PASS]")
                        self.results.append({'test_case': test_data['test_case_id'], 'passed': True})
                    else:
                        error = driver.find_element(By.CSS_SELECTOR, ".alert.alert-danger").text
                        if test_data['expected_result'] in error:
                            print(f"[PASS]")
                            self.results.append({'test_case': test_data['test_case_id'], 'passed': True})
                        else:
                            print(f"[FAIL]")
                            self.results.append({'test_case': test_data['test_case_id'], 'passed': False})
                except:
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
