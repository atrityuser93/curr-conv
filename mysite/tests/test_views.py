import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class CurrencyConvertFormTest(LiveServerTestCase):

    def test_form(self):
        # set webdriver for browser
        selenium = webdriver.Chrome()
        # select url
        selenium.get('http://127.0.0.1:8000/')
        # find elements on form to submit
        input_currency = selenium.find_element(by=By.NAME, value='input_currency')
        input_value = selenium.find_element(by=By.NAME, value='input_value')
        output_currency = selenium.find_element(by=By.NAME, value='output_currency')
        submit_button = selenium.find_element(by=By.CSS_SELECTOR, value="button")

        # add input value in forms
        input_currency.send_keys('AUD')
        input_value.send_keys(10)
        output_currency.send_keys('USD')

        # submit form
        submit_button.send_keys(Keys.RETURN)