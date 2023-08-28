import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from django.test import LiveServerTestCase, TransactionTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging

from convert.models import CountryCodes, ExchangeRates, CurrencyConvert

# logging.basicConfig(filename='test.log', level=logging.INFO)
logger = logging.getLogger()
logger.level = logging.INFO


class CurrencyConvertFormTest(LiveServerTestCase):
    fixtures = ['mod.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create/open new Chrome session w/ webdriver
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(35)
        cls.driver.maximize_window()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def test_convert_form(self):
        # use to access Django test session URL (for a closed session and independent session)
        self.driver.get(f"{self.live_server_url}/convert")
        # self.driver.get("http://localhost:8081/converter/")
        # stream_handler = logging.StreamHandler(sys.stdout)
        # logger.addHandler(stream_handler)
        # find elements on form to submit
        input_currency = self.driver.find_element(by=By.NAME, value='input_currency')
        input_value = self.driver.find_element(by=By.NAME, value='input_value')
        output_currency = self.driver.find_element(by=By.NAME, value='output_currency')
        submit_button = self.driver.find_element(by=By.XPATH, value="//button[@type='submit' and "
                                                                    "@name='convert_submit']")

        # add input value in forms
        input_currency.send_keys('United States Dollar')
        input_value.send_keys(100)
        output_currency.send_keys('South Korean Won')

        # submit form
        submit_button.send_keys(Keys.RETURN)

        # check output currency
        output_currency = self.driver.find_element(by=By.NAME, value='output_currency')
        value = output_currency.get_attribute(name='value')
        with self.subTest('Check Output Currency in Form'):
            self.assertEqual(value, 'KRW')

        # compare output value with value stored in DB
        output_value = self.driver.find_element(by=By.NAME, value='output_value')
        value = output_value.get_attribute(name='value')
        # get corresponding data from stored database
        obj = CurrencyConvert.objects.filter(input_currency='USD',
                                             output_currency='KRW',
                                             input_value=100).order_by('-asked_on').first()
        # logging.getLogger().info('BBB')
        # logging.getLogger().info('Attribute type: {}'.format(type(value)))
        with self.subTest('Check Output Converted Value'):
            self.assertAlmostEqual(round(float(value), 2), round(obj.output_value, 2))

        with self.subTest('Second Submit - Change Input Value Check'):
            input_value = self.driver.find_element(by=By.NAME, value='input_value')
            submit_button = self.driver.find_element(by=By.XPATH, value="//button[@type='submit' and "
                                                                        "@name='convert_submit']")
            # logging.info('Input value: {}, Output value: {}'.format(input_value.get_attribute(name='value'),
            #                                                         output_value.get_attribute(name='value')))
            input_value.clear()
            input_value.send_keys(10)
            submit_button.send_keys(Keys.RETURN)

            new_output_value = self.driver.find_element(by=By.NAME, value='output_value')
            value = new_output_value.get_attribute(name='value')

            # get corresponding data from stored database
            obj = CurrencyConvert.objects.filter(input_currency='USD',
                                                 output_currency='KRW',
                                                 input_value=10).order_by('-asked_on').first()

            self.assertAlmostEqual(round(float(value), 2), round(obj.output_value, 2))

        with self.subTest('Third Submit - Change Input Value & Output Currency Check'):
            input_value = self.driver.find_element(by=By.NAME, value='input_value')
            output_currency = self.driver.find_element(by=By.NAME, value='output_currency')
            submit_button = self.driver.find_element(by=By.XPATH, value="//button[@type='submit' and "
                                                                        "@name='convert_submit']")

            input_value.clear()
            input_value.send_keys(10)
            output_currency.clear()
            output_currency.send_keys('BDT')
            submit_button.send_keys(Keys.RETURN)

            new_output_value = self.driver.find_element(by=By.NAME, value='output_value')
            value = new_output_value.get_attribute(name='value')

            # get corresponding data from stored database
            obj = CurrencyConvert.objects.filter(input_currency='USD',
                                                 output_currency='BDT',
                                                 input_value=10).order_by('-asked_on').first()

            self.assertAlmostEqual(round(float(value), 2), round(obj.output_value, 2))

        with self.subTest('Fourth Submit - Change Input and Output Currency Check'):
            input_currency = self.driver.find_element(by=By.NAME, value='input_currency')
            input_value = self.driver.find_element(by=By.NAME, value='input_value')
            output_currency = self.driver.find_element(by=By.NAME, value='output_currency')
            submit_button = self.driver.find_element(by=By.NAME, value='convert_submit')

            input_currency.clear()
            input_currency.send_keys('AUD')
            # input_value.clear()
            # input_value.send_keys(10)
            output_currency.clear()
            output_currency.send_keys('AED')
            submit_button.send_keys(Keys.RETURN)

            new_output_value = self.driver.find_element(by=By.NAME, value='output_value')
            value = new_output_value.get_attribute(name='value')

            # get corresponding data from stored database
            obj = CurrencyConvert.objects.filter(input_currency='AUD',
                                                 output_currency='AED',
                                                 input_value=10).order_by('-asked_on').first()

            self.assertAlmostEqual(round(float(value), 2), round(obj.output_value, 2))

        # logger.removeHandler(stream_handler)


class SearchTest(LiveServerTestCase):
    fixtures = ['mod.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create/open new Chrome session w/ webdriver
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(35)
        cls.driver.maximize_window()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def test_code_search(self):
        self.driver.get(f"{self.live_server_url}/convert")
        self.driver.find_element(by=By.NAME, value='search_codes_query').send_keys('dollar')
        self.driver.find_element(by=By.ID, value='search_codes_submit').send_keys(Keys.RETURN)

        wait = WebDriverWait(self.driver, 2)
        results_title = wait.until(EC.visibility_of_element_located((By.ID, 'search_header'))).text

        self.assertEqual(results_title, 'There are 23 currencies matching')

    def test_exchange_rates_search(self):
        self.driver.get(f"{self.live_server_url}/convert")
        self.driver.find_element(by=By.NAME, value='search_rates_query').send_keys('dollar')
        self.driver.find_element(by=By.ID, value='search_rates_submit').send_keys(Keys.RETURN)

        wait = WebDriverWait(self.driver, 2)
        results_title = wait.until(EC.visibility_of_element_located((By.ID, 'search_header'))).text

        self.assertEqual(results_title, 'There are 3 currencies matching')



