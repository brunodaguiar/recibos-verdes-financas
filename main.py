from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from finances_selenium import FinancesSelenium

# create an object of FinancesSelenium class
finances_selenium = FinancesSelenium()

finances_selenium.start()