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

class TC007(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_t_c007(self):
        driver = self.driver
        
        # Load test data from CSV file
        csv_file = os.path.join(os.path.dirname(__file__), 'TC007data.csv')
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            test_data = list(csv_reader)
        
        # Initialize counters for test cases
        total_test_cases = len(test_data)
        passed_test_cases = 0
        failed_test_cases = 0
        
        print(f"\n{'='*60}")
        print(f"Total test cases imported from CSV: {total_test_cases}")
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
            
            # Step 2: Navigate to banking project
            driver.get("https://www.globalsqa.com/angularJs-protractor/BankingProject")
            
            # Step 3: Click Customer Login button (xpath following Logout)
            customer_login = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Logout'])[1]/following::button[1]")))
            customer_login.click()
            
            # Step 4: Click userSelect dropdown
            user_select = self.wait.until(EC.element_to_be_clickable((By.ID, "userSelect")))
            user_select.click()
            
            # Step 5: Select Hermoine Granger
            Select(user_select).select_by_visible_text("Hermoine Granger")
            
            # Step 6: Click Login button (submit button)
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            login_button.click()
            time.sleep(1)
            
            # Step 7: Click button following "Dollar" (Withdrawl button to navigate to transactions)
            dollar_following_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Dollar'])[1]/following::button[1]")))
            dollar_following_btn.click()
            time.sleep(0.5)
            
            # Step 8: Click button following "Back" (Reset button)
            back_following_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Back'])[1]/following::button[1]")))
            back_following_btn.click()
            time.sleep(1)
            
            # Step 9: Click button following "Logout" (Home button)
            logout_following_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Logout'])[1]/following::button[1]")))
            logout_following_btn.click()
            time.sleep(1)
            
            # Step 10: Click button following "Transactions" (Deposit button)
            transactions_following_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Transactions'])[1]/following::button[1]")))
            transactions_following_btn.click()
            time.sleep(0.5)
            
            # Step 11: Click deposit input field
            deposit_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='number']")))
            deposit_input.click()
            
            # Step 12: Type deposit amount
            deposit_input.clear()
            deposit_input.send_keys(deposit)
            time.sleep(0.5)
            
            # Step 13: Click Deposit submit button (button with empty value)
            deposit_submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@value='']")))
            deposit_submit.click()
            time.sleep(1)
            
            # Step 14: Click button following "Deposit" (Withdrawl button)
            deposit_following_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Deposit'])[1]/following::button[1]")))
            deposit_following_btn.click()
            time.sleep(0.5)
            
            # Step 15: Click withdraw input field
            withdraw_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='number']")))
            withdraw_input.click()
            time.sleep(0.3)
            
            # Step 16-18: Handle different test types for withdraw
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
            
            # Step 22: Click Withdraw submit button (button with empty value)
            withdraw_submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@value='']")))
            withdraw_submit.click()
            time.sleep(1)
            
            # Verify results based on test type
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
            
            # Step 27: Click accountSelect dropdown
            account_select = self.wait.until(EC.element_to_be_clickable((By.ID, "accountSelect")))
            account_select.click()
            
            # Step 28: Select account 1002
            Select(account_select).select_by_visible_text("1002")
            time.sleep(0.5)
            
            # Step 29: Click accountSelect dropdown again
            account_select = self.wait.until(EC.element_to_be_clickable((By.ID, "accountSelect")))
            account_select.click()
            
            # Step 30: Select account 1001
            Select(account_select).select_by_visible_text("1001")
            time.sleep(1)
            
            # Step 31: Verify final balance
            try:
                balance_element = self.wait.until(EC.presence_of_element_located((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Please open an account with us.'])[1]/following::strong[2]")))
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
