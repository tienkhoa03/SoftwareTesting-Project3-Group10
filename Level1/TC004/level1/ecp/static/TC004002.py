# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class TC004002(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path=r'')
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_t_c004002(self):
        driver = self.driver
        driver.get(self.base_url + "chrome://newtab/")
        driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/account")
        driver.find_element_by_xpath("//div[@id='widget-navbar-217834']/ul/li[6]/ul/li[6]/a/div/span").click()
        driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/logout")
        driver.find_element_by_link_text("Continue").click()
        driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=common/home")
        driver.find_element_by_link_text("Login").click()
        driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")
        driver.find_element_by_id("input-email").click()
        driver.find_element_by_id("input-email").clear()
        driver.find_element_by_id("input-email").send_keys("alextisgona@gmail.com")
        driver.find_element_by_id("input-password").click()
        driver.find_element_by_id("input-password").clear()
        driver.find_element_by_id("input-password").send_keys("@@@123abc")
        driver.find_element_by_xpath("//input[@value='Login']").click()
        driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/account")
        driver.find_element_by_xpath("//div[@id='widget-navbar-217834']/ul/li[6]/a/div/span").click()
    
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
