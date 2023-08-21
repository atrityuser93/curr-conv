import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import logging

# logging.basicConfig(filename='test.log', level=logging.INFO)
logger = logging.getLogger()
logger.level = logging.INFO


class CurrencyConvertFormTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        # create/open new Chrome session w/ webdriver
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(30)
        cls.driver.maximize_window()
        cls.driver.get('http://127.0.0.1:8000/converter')

    def test_form(self):
        # set webdriver for browser
        # selenium = webdriver.Chrome()
        # select url
        # selenium.get('http://127.0.0.1:8000/')
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)
        # find elements on form to submit
        input_currency = self.driver.find_element(by=By.NAME, value='input_currency')
        input_value = self.driver.find_element(by=By.NAME, value='input_value')
        output_currency = self.driver.find_element(by=By.NAME, value='output_currency')
        submit_button = self.driver.find_element(by=By.CSS_SELECTOR, value="button")

        # add input value in forms
        input_currency.send_keys('Australian Dollar')
        input_value.send_keys(10)
        output_currency.send_keys('United States Dollar')

        # submit form
        submit_button.send_keys(Keys.RETURN)

        # check output value
        output_value = self.driver.find_element(by=By.NAME, value='output_value')
        value = output_value.get_attribute(name='value')
        # logging.getLogger().info(r'%s{attr}')
        logging.getLogger().info('BBB')
        # logging.getLogger().info('{}'.format(attr))
        # logging.getLogger().info('Attribute type: {}'.format(type(value)))
        logging.getLogger().info('Attribute type: {}'.format(type(float(value))))
        self.assertAlmostEqual(float(value), 6.469818557291871)

        logger.removeHandler(stream_handler)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()

