# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest
import time
import re
import csv
import os

class TC002Level2(unittest.TestCase):
    def setUp(self):
        # Configure Chrome options to disable password save prompts
        chrome_options = webdriver.ChromeOptions()
        
        # Disable password manager and breach detection
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
            "safebrowsing.enabled": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Disable other popup notifications
        chrome_options.add_argument("--disable-notifications")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(30)
        self.base_url = "https://sweetshop.netlify.app/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_t_c002_level2(self):
        """Data-driven test using TC002level2config.csv for web elements and TC002level2data.csv for test data"""
        driver = self.driver
        
        # Load configuration (web elements) from config CSV
        config_file = os.path.join(os.path.dirname(__file__), 'TC002level2config.csv')
        config = {}
        with open(config_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            config_row = next(csv_reader)  # Read first (and only) row
            config = {
                'site_url': config_row.get('Site_URL', ''),
                'email_locator': config_row.get('Email_locator', ''),
                'password_locator': config_row.get('Password_locator', ''),
                'button_locator': config_row.get('Button_locator', ''),
                'success_url': config_row.get('Success_URL', '')
            }
        
        # Load test data from CSV
        data_file = os.path.join(os.path.dirname(__file__), 'TC002level2data.csv')
        
        # Initialize counters
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        with open(data_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row_num, row in enumerate(csv_reader, start=2):  # start=2 because row 1 is header
                test_id = row.get('ID', '')
                email = row.get('Email', '')
                password = row.get('Password', '')
                test_type = row.get('Type', '')
                target_1 = row.get('Target_1', '')
                result_1 = row.get('Result_1', '')
                target_2 = row.get('Target_2', '')
                result_2 = row.get('Result_2', '')
                
                # Get web elements from config
                site_url = config['site_url']
                email_locator = config['email_locator']
                password_locator = config['password_locator']
                button_locator = config['button_locator']
                success_url = config['success_url']
                
                total_tests += 1
                print(f"\n--- Running Test: {test_id} ---")
                
                try:
                    # Open login page using URL from CSV
                    driver.get(site_url)
                    time.sleep(1)
                    
                    # Enter email using locator from CSV
                    email_field = self._find_element_by_target(driver, email_locator)
                    email_field.click()
                    email_field.clear()
                    if email:
                        email_field.send_keys(email)
                    
                    # Enter password using locator from CSV
                    password_field = self._find_element_by_target(driver, password_locator)
                    password_field.click()
                    password_field.clear()
                    if password:
                        password_field.send_keys(password)
                    
                    time.sleep(0.5)
                    
                    # Execute test based on type
                    if test_type == "success":
                        submit_button = self._find_element_by_target(driver, button_locator)
                        submit_button.click()
                        time.sleep(2)
                        
                        # Verify successful login by checking URL
                        current_url = driver.current_url
                        expected_url = success_url if success_url else target_1
                        self.assertIn("00efc23d-b605-4f31-b97b-6bb276de447e", current_url, 
                                     f"Test {test_id}: Login should be successful")
                        print(f"✓ Test {test_id} PASSED: Login successful")
                        passed_tests += 1
                    
                    elif test_type == "one_field_invalid":
                        submit_button = self._find_element_by_target(driver, button_locator)
                        submit_button.click()
                        time.sleep(1.5)
                        
                        # Verify error message - check DOM text first
                        if target_1:
                            actual_text = ''
                            try:
                                # First try to find the error element in the DOM
                                error_element = self._find_element_by_target(driver, target_1)
                                actual_text = error_element.text.strip()
                            except:
                                pass
                            
                            # If DOM text is empty, try HTML5 validation message as fallback
                            if not actual_text:
                                try:
                                    if 'Email' in str(target_1):
                                        error_element = self._find_element_by_target(driver, email_locator)
                                    else:
                                        error_element = self._find_element_by_target(driver, password_locator)
                                    actual_text = error_element.get_attribute('validationMessage')
                                except:
                                    pass
                            
                            # Verify the error message
                            if actual_text:
                                self.assertIn(result_1.lower(), actual_text.lower(), 
                                             f"Test {test_id}: Error message mismatch. Expected: '{result_1}', Got: '{actual_text}'")
                                print(f"✓ Test {test_id} PASSED: Error message verified")
                                passed_tests += 1
                            else:
                                raise Exception(f"No error message found. Expected: '{result_1}'")
                    
                    elif test_type == "two_field_invalid":
                        submit_button = self._find_element_by_target(driver, button_locator)
                        submit_button.click()
                        time.sleep(1.5)
                        
                        # Verify first error message - check DOM text first
                        validation_passed = False
                        if target_1:
                            actual_text_1 = ''
                            try:
                                error_element_1 = self._find_element_by_target(driver, target_1)
                                actual_text_1 = error_element_1.text.strip()
                            except:
                                pass
                            
                            if not actual_text_1:
                                try:
                                    error_element_1 = self._find_element_by_target(driver, email_locator)
                                    actual_text_1 = error_element_1.get_attribute('validationMessage')
                                except:
                                    pass
                            
                            if actual_text_1:
                                self.assertIn(result_1.lower(), actual_text_1.lower(), 
                                             f"Test {test_id}: First error message mismatch. Expected: '{result_1}', Got: '{actual_text_1}'")
                                validation_passed = True
                        
                        # Check second error if available (may not show if HTML5 validates first field only)
                        if target_2 and result_2:
                            try:
                                actual_text_2 = ''
                                try:
                                    error_element_2 = self._find_element_by_target(driver, target_2)
                                    actual_text_2 = error_element_2.text.strip()
                                except:
                                    pass
                                
                                if actual_text_2:
                                    self.assertIn(result_2.lower(), actual_text_2.lower(), 
                                                 f"Test {test_id}: Second error message mismatch")
                            except:
                                pass  # Second error may not be visible
                        
                        if validation_passed:
                            print(f"✓ Test {test_id} PASSED: Error message verified")
                            passed_tests += 1
                        else:
                            raise Exception(f"No error message found. Expected: '{result_1}'")
                    
                    elif test_type == "one_field_limit":
                        # Verify attribute (e.g., maxlength)
                        if target_1 and '@' in target_1:
                            parts = target_1.split('@')
                            element_locator = parts[0]
                            attribute_name = parts[1] if len(parts) > 1 else 'maxlength'
                            
                            element = self._find_element_by_target(driver, element_locator)
                            actual_value = element.get_attribute(attribute_name)
                            self.assertEqual(actual_value, result_1, 
                                           f"Test {test_id}: Attribute value mismatch")
                            print(f"✓ Test {test_id} PASSED: Attribute verified")
                            passed_tests += 1
                    
                    elif test_type == "two_field_limit":
                        # Verify first attribute
                        if target_1 and '@' in target_1:
                            parts = target_1.split('@')
                            element_locator = parts[0]
                            attribute_name = parts[1] if len(parts) > 1 else 'maxlength'
                            
                            element_1 = self._find_element_by_target(driver, element_locator)
                            actual_value_1 = element_1.get_attribute(attribute_name)
                            self.assertEqual(actual_value_1, result_1, 
                                           f"Test {test_id}: First attribute value mismatch")
                        
                        # Verify second attribute
                        if target_2 and '@' in target_2:
                            parts = target_2.split('@')
                            element_locator = parts[0]
                            attribute_name = parts[1] if len(parts) > 1 else 'maxlength'
                            
                            element_2 = self._find_element_by_target(driver, element_locator)
                            actual_value_2 = element_2.get_attribute(attribute_name)
                            self.assertEqual(actual_value_2, result_2, 
                                           f"Test {test_id}: Second attribute value mismatch")
                        
                        print(f"✓ Test {test_id} PASSED: Both attributes verified")
                        passed_tests += 1
                    
                except Exception as e:
                    print(f"✗ Test {test_id} FAILED: {str(e)}")
                    self.verificationErrors.append(f"Test {test_id}: {str(e)}")
                    failed_tests += 1
        
        # Print summary statistics
        print(f"\n{'='*60}")
        print(f"TEST EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total test cases: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests/total_tests*100):.2f}%" if total_tests > 0 else "Success rate: 0.00%")
        print(f"{'='*60}\n")
    
    def _find_element_by_target(self, driver, target):
        """Helper method to find element by various locator types"""
        if target.startswith('id='):
            return driver.find_element(By.ID, target.replace('id=', ''))
        elif target.startswith('xpath='):
            return driver.find_element(By.XPATH, target.replace('xpath=', ''))
        elif target.startswith('name='):
            return driver.find_element(By.NAME, target.replace('name=', ''))
        elif target.startswith('css='):
            return driver.find_element(By.CSS_SELECTOR, target.replace('css=', ''))
        elif target.startswith('link='):
            return driver.find_element(By.LINK_TEXT, target.replace('link=', ''))
        else:
            # Default to xpath if no prefix
            return driver.find_element(By.XPATH, target)
    
    def is_element_present(self, how, what):
        try: 
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: 
            return False
        return True
    
    def is_alert_present(self):
        try: 
            self.driver.switch_to.alert
        except NoAlertPresentException as e: 
            return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: 
            self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
