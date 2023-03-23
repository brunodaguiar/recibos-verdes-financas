from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.firefox import GeckoDriverManager
from extension_methods import IReadOnlyIWebElementCollectionExtension

class FinancesLoginSelenium:
    user = ""
    password = ""

    def __init__(self, driver: webdriver, vat, password):
        self._driver = driver
        self._txt_user = None
        self._txt_password = None
        self._btn_login = None

        self.user = vat
        self.password = password

    def login(self):
        self._driver.find_elements(By.CLASS_NAME, "tab-label")[1].click()
        self._get_credential_form_elements()

        if not self._has_all_login_elements():
            raise Exception("Login form is missing fields")

        self._txt_user.send_keys(self.user)
        self._txt_password.send_keys(self.password)

        self._btn_login.click()

    def _get_credential_form_elements(self):
        self._txt_user = self._driver.find_element(By.ID, "username")
        self._txt_password = self._driver.find_element(By.ID, "password-nif")
        self._btn_login = self._driver.find_element(By.ID, "sbmtLogin")

    def is_login_available(self):
        self._get_credential_form_elements()
        return self._has_all_login_elements()

    def _has_all_login_elements(self):
        return self._txt_user is not None and \
               self._txt_password is not None and \
               self._btn_login is not None

