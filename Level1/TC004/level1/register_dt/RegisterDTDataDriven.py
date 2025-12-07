# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import csv
import unittest
import time
from pathlib import Path

CHROMEDRIVER_PATH = Path(__file__).resolve().parent.parent.parent / "common" / "chromedriver.exe"

class RegisterDTDataDriven(unittest.TestCase):
    def setUp(self):
        service = Service(executable_path=str(CHROMEDRIVER_PATH))
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(30)
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_register_d_t_data_driven(self):
        data_file = Path(__file__).resolve().parent / "data" / "REGISTER_DT.csv"
        rows = self._load_rows(data_file)
        for row in rows:
            with self.subTest(tc_id=row.get("tc_id")):
                self._run_register_flow(row)
                self.driver.delete_all_cookies()
                self.driver.get("about:blank")
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True

    def _load_rows(self, csv_path):
        with open(csv_path, newline='', encoding='utf-8') as fh:
            return list(csv.DictReader(fh))

    def _run_register_flow(self, row):
        driver = self.driver
        driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/register")

        driver.find_element(By.ID, "input-firstname").clear()
        driver.find_element(By.ID, "input-firstname").send_keys(row.get("firstname", ""))

        driver.find_element(By.ID, "input-lastname").clear()
        driver.find_element(By.ID, "input-lastname").send_keys(row.get("lastname", ""))

        email_input = driver.find_element(By.ID, "input-email")
        # allow server-side validation by bypassing HTML5 email blocker
        driver.execute_script("arguments[0].setAttribute('type','text');", email_input)
        email_input.clear()
        email_input.send_keys(row.get("email", ""))

        driver.find_element(By.ID, "input-telephone").clear()
        driver.find_element(By.ID, "input-telephone").send_keys(row.get("telephone", ""))

        driver.find_element(By.ID, "input-password").clear()
        driver.find_element(By.ID, "input-password").send_keys(row.get("password", ""))

        driver.find_element(By.ID, "input-confirm").clear()
        driver.find_element(By.ID, "input-confirm").send_keys(row.get("confirm", ""))

        agree_val = (row.get("agree", "").strip().lower() == "yes")
        agree_checkbox = driver.find_element(By.ID, "input-agree")
        if agree_checkbox.is_selected() != agree_val:
            label = driver.find_element(By.CSS_SELECTOR, 'label[for="input-agree"]')
            driver.execute_script("arguments[0].scrollIntoView(true);", label)
            driver.execute_script("arguments[0].click();", label)

        driver.find_element(By.CSS_SELECTOR, "input[type=\"submit\"][value=\"Continue\"]").click()
        time.sleep(2)

        expect_type = row.get("expect_type", "").strip().lower()
        expect_text = row.get("expect_text", "")

        if expect_type == "alert":
            self.assertTrue(self.is_element_present(By.CSS_SELECTOR, ".alert-danger"))
            if expect_text:
                self.assertEqual(expect_text, driver.find_element(By.CSS_SELECTOR, ".alert-danger").text)
        elif expect_type == "field_error":
            self.assertTrue(self.is_element_present(By.CSS_SELECTOR, ".text-danger"))
        elif expect_type == "success":
            self.assertTrue(self.is_element_present(By.CSS_SELECTOR, "#content h1"))
            if expect_text:
                self.assertEqual(expect_text, driver.find_element(By.CSS_SELECTOR, "#content h1").text)
            driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/logout")
        else:
            self.fail(f"Unknown expect_type: {expect_type}")
    
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
    unittest.main(verbosity=2)
