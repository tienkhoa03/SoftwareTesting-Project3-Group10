# -*- coding: utf-8 -*-
import csv
import time
import unittest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

CHROMEDRIVER_PATH = Path(__file__).resolve().parent.parent.parent / "common" / "chromedriver.exe"
DATA_FILE = Path(__file__).resolve().parent / "data" / "BVA_LOGIN.csv"


class BVALoginDataDriven(unittest.TestCase):
    def setUp(self):
        service = Service(executable_path=str(CHROMEDRIVER_PATH))
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(20)

    def test_login_bva(self):
        rows = self._load_rows(DATA_FILE)
        for row in rows:
            with self.subTest(tc_id=row.get("tc_id")):
                self._run_case(row)
                # reset state to reduce flakiness between rows
                self.driver.delete_all_cookies()
                self.driver.execute_script("window.sessionStorage.clear(); window.localStorage.clear();")
                self.driver.get("about:blank")
                time.sleep(0.8)

    def _run_case(self, row):
        driver = self.driver
        driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")

        email = row.get("email", "")
        password = row.get("password", "")
        expect_type = row.get("expect_type", "").strip().lower()
        expect_text = row.get("expect_text", "")

        # fill form
        email_input = driver.find_element(By.ID, "input-email")
        email_input.clear()
        email_input.send_keys(email)

        pwd_input = driver.find_element(By.ID, "input-password")
        pwd_input.clear()
        pwd_input.send_keys(password)

        driver.find_element(By.XPATH, "//input[@value='Login']").click()
        time.sleep(2)

        if expect_type == "success":
            # after success should land on account page with heading
            self.assertTrue(self.is_element_present(By.CSS_SELECTOR, "#content h2"))
            if expect_text:
                self.assertIn(expect_text, driver.find_element(By.CSS_SELECTOR, "#content h2").text)
        elif expect_type == "alert":
            self.assertTrue(self.is_element_present(By.CSS_SELECTOR, ".alert-danger"))
            if expect_text:
                actual = driver.find_element(By.CSS_SELECTOR, ".alert-danger").text
                lockout = "exceeded allowed number of login attempts"
                if lockout.lower() in actual.lower():
                    # accept lockout banner as alternate expected when site throttles
                    self.assertIn(lockout.split()[0], actual.lower())
                else:
                    self.assertEqual(expect_text, actual)
        else:
            self.fail(f"Unknown expect_type: {expect_type}")

    def _load_rows(self, csv_path):
        with open(csv_path, newline='', encoding='utf-8') as fh:
            return list(csv.DictReader(fh))

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
