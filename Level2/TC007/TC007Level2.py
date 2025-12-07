# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, csv, os

class TC007Level2(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_t_c007_level2(self):
        driver = self.driver
        
        # Load configuration from config file (web elements and locators)
        config_file = os.path.join(os.path.dirname(__file__), 'TC007level2config.csv')
        with open(config_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            config = next(csv_reader)  # Read only the first row for configuration
        
        # Parse configuration values
        url_home = config['URL_home']
        btn_customer_login = config['Btn_customer_login'].replace('xpath=', '')
        select_user_id = config['Select_user_id'].replace('id=', '')
        btn_login = config['Btn_login'].replace('xpath=', '')
        btn_transaction_tab = config['Btn_transaction_tab'].replace('xpath=', '')
        btn_deposit_tab = config['Btn_deposit_tab'].replace('xpath=', '')
        btn_withdraw_tab = config['Btn_withdraw_tab'].replace('xpath=', '')
        btn_reset = config['Btn_reset'].replace('xpath=', '')
        btn_back = config['Btn_back'].replace('xpath=', '')
        input_amount = config['Input_amount'].replace('xpath=', '')
        btn_submit = config['Btn_submit'].replace('xpath=', '')
        select_account_id = config['Select_account_id'].replace('id=', '')
        label_balance = config['Label_balance'].replace('xpath=', '')
        user_name = config['User_name'].replace('label=', '')
        account_main = config['Account_main'].replace('label=', '')
        account_temp = config['Account_temp'].replace('label=', '')
        
        print(f"\n{'='*60}")
        print(f"Configuration loaded from TC007level2config.csv")
        print(f"URL: {url_home}")
        print(f"User: {user_name}")
        print(f"{'='*60}\n")
        
        # Load test data from data file
        data_file = os.path.join(os.path.dirname(__file__), 'TC007level2data.csv')
        with open(data_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            test_data = list(csv_reader)
        
        # Initialize counters for test cases
        total_test_cases = len(test_data)
        passed_test_cases = 0
        failed_test_cases = 0
        
        print(f"Total test cases imported from TC007level2data.csv: {total_test_cases}")
        print(f"{'='*60}\n")
        
        # Execute test for each row in CSV
        for row in test_data:
            test_id = row['ID']
            deposit = row['Deposit']
            withdraw = row['Withdraw']
            test_type = row['Type']
            script_target = row['Script_target']
            balance_result = row['Balance_result']
            verified_target = row['Verified_target'].replace('xpath=', '') if row['Verified_target'] else ''
            expected_result = row['Expected_result']
            
            # Track if current test case passes
            test_case_passed = True
            
            print(f"\n=== Running test case: {test_id} ===")
            
            # Step 1: Navigate to URL_home
            driver.get(url_home)
            time.sleep(1)
            
            # Step 2: Click Customer Login button
            customer_login = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_customer_login)))
            customer_login.click()
            
            # Step 3: Click user select dropdown
            user_select = self.wait.until(EC.element_to_be_clickable((By.ID, select_user_id)))
            user_select.click()
            
            # Step 4: Select user
            Select(user_select).select_by_visible_text(user_name)
            
            # Step 5: Click Login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_login)))
            login_button.click()
            time.sleep(1)
            
            # Step 6: Click Transaction tab button
            transaction_tab_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_transaction_tab)))
            transaction_tab_btn.click()
            time.sleep(0.5)
            
            # Step 7: Click Reset button
            reset_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_reset)))
            reset_button.click()
            time.sleep(1)
            print(f"✓ Transactions reset - Balance set to 0")
            
            # Step 8: Click Back button
            back_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_back)))
            back_button.click()
            time.sleep(1)
            
            # Step 9: Click Deposit tab button
            deposit_tab_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_deposit_tab)))
            deposit_tab_btn.click()
            time.sleep(0.5)
            
            # Step 10: Click deposit input field
            deposit_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, input_amount)))
            deposit_input.click()
            
            # Step 11: Type deposit amount
            deposit_input.clear()
            deposit_input.send_keys(deposit)
            time.sleep(0.5)
            
            # Step 12: Click Deposit submit button
            deposit_submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_submit)))
            deposit_submit.click()
            time.sleep(1)
            
            # Step 13: Click Withdraw tab button
            withdraw_tab_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_withdraw_tab)))
            withdraw_tab_btn.click()
            time.sleep(0.5)
            
            # Step 14: Click withdraw input field
            withdraw_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, input_amount)))
            withdraw_input.click()
            time.sleep(0.3)
            
            # Step 15-17: Handle different test types for withdraw
            if test_type == "no_transaction":
                # Execute script to set negative value
                if script_target:
                    driver.execute_script(script_target)
                    time.sleep(0.5)
            elif test_type == "input_invalid":
                # Try to enter invalid input (letters)
                try:
                    withdraw_input.clear()
                    withdraw_input.send_keys(withdraw)
                    time.sleep(0.5)
                    # Verify input field value
                    actual_value = withdraw_input.get_attribute("value")
                    if verified_target:
                        target_element = driver.find_element(By.XPATH, verified_target)
                        self.assertEqual(expected_result, actual_value)
                except Exception as e:
                    test_case_passed = False
                    print(f"Input validation test: {str(e)}")
            else:
                # Normal withdraw input (type)
                withdraw_input.clear()
                withdraw_input.send_keys(withdraw)
                time.sleep(0.5)
            
            # Step 21: Click Withdraw submit button
            withdraw_submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_submit)))
            withdraw_submit.click()
            time.sleep(1)
            
            # Step 22-26: Verify results based on test type
            if test_type == "success":
                if verified_target and expected_result:
                    try:
                        result_element = self.wait.until(EC.presence_of_element_located((By.XPATH, verified_target)))
                        actual_text = result_element.text
                        self.assertEqual(expected_result, actual_text)
                        print(f"✓ Verification passed: {expected_result}")
                    except AssertionError as e:
                        test_case_passed = False
                        self.verificationErrors.append(f"{test_id}: Expected '{expected_result}', got '{actual_text}'")
                        print(f"✗ Verification failed: Expected '{expected_result}', got '{actual_text}'")
                    except Exception as e:
                        test_case_passed = False
                        self.verificationErrors.append(f"{test_id}: {str(e)}")
                        print(f"✗ Verification error: {str(e)}")
            elif test_type == "no_transaction":
                if verified_target and expected_result:
                    try:
                        time.sleep(1)  # Wait a bit to ensure no message appears
                        result_element = self.wait.until(EC.presence_of_element_located((By.XPATH, verified_target)))
                        actual_text = result_element.text
                        # For no_transaction, we expect the message to NOT be the expected success message
                        self.assertNotEqual(expected_result, actual_text)
                        print(f"✓ Verification passed: Text is not '{expected_result}'")
                    except AssertionError as e:
                        test_case_passed = False
                        self.verificationErrors.append(f"{test_id}: Text should not be '{expected_result}'")
                        print(f"✗ Verification failed: Text should not be '{expected_result}'")
                    except Exception as e:
                        # If element not found, that's actually okay for no_transaction case
                        print(f"✓ Verification passed: No transaction message displayed")
            elif test_type == "balance_insufficient":
                if verified_target and expected_result:
                    try:
                        result_element = self.wait.until(EC.presence_of_element_located((By.XPATH, verified_target)))
                        actual_text = result_element.text
                        self.assertEqual(expected_result, actual_text)
                        print(f"✓ Verification passed: {expected_result}")
                    except AssertionError as e:
                        test_case_passed = False
                        self.verificationErrors.append(f"{test_id}: Expected '{expected_result}', got '{actual_text}'")
                        print(f"✗ Verification failed: Expected '{expected_result}', got '{actual_text}'")
                    except Exception as e:
                        test_case_passed = False
                        self.verificationErrors.append(f"{test_id}: {str(e)}")
                        print(f"✗ Verification error: {str(e)}")
            
            # Step 27: Click account select dropdown
            account_select = self.wait.until(EC.element_to_be_clickable((By.ID, select_account_id)))
            account_select.click()
            
            # Step 28: Select temporary account
            Select(account_select).select_by_visible_text(account_temp)
            time.sleep(0.5)
            
            # Step 29: Click account select dropdown again
            account_select = self.wait.until(EC.element_to_be_clickable((By.ID, select_account_id)))
            account_select.click()
            
            # Step 30: Select main account
            Select(account_select).select_by_visible_text(account_main)
            time.sleep(1)
            
            # Step 31: Verify final balance
            try:
                balance_element = self.wait.until(EC.presence_of_element_located((By.XPATH, label_balance)))
                actual_balance = balance_element.text
                self.assertEqual(balance_result, actual_balance)
                print(f"✓ Balance verification passed: {balance_result}")
            except AssertionError as e:
                test_case_passed = False
                self.verificationErrors.append(f"{test_id} - Balance: {str(e)}")
                print(f"✗ Balance verification failed: Expected {balance_result}, got {balance_element.text if 'balance_element' in locals() else 'N/A'}")
            except Exception as e:
                test_case_passed = False
                self.verificationErrors.append(f"{test_id} - Balance error: {str(e)}")
                print(f"✗ Balance verification error: {str(e)}")
            
            # Update counters based on test result
            if test_case_passed:
                passed_test_cases += 1
                print(f"✓ Test case {test_id} PASSED")
            else:
                failed_test_cases += 1
                print(f"✗ Test case {test_id} FAILED")
            
            print(f"=== Test case {test_id} completed ===\n")
        
        # Print final summary
        print(f"\n{'='*60}")
        print(f"TEST EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total test cases:  {total_test_cases}")
        print(f"Passed:            {passed_test_cases} ({passed_test_cases/total_test_cases*100:.1f}%)")
        print(f"Failed:            {failed_test_cases} ({failed_test_cases/total_test_cases*100:.1f}%)")
        print(f"{'='*60}\n")
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
