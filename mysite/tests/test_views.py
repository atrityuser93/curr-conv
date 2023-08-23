import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from django.test import LiveServerTestCase, TransactionTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

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

    # def test_currency_convert_db(self):
    #     """Test whether the ConvertCurrency model db is present in test_db"""
    #     self.driver.get(f"{self.live_server_url}/converter/")
    #     obj = CurrencyConvert.objects.get(pk=6)
    #
    #     tests = [('Input Currency Check', 'input_currency', 'AUD'),
    #              ('Output Currency Check', 'output_currency', 'AED')]
    #
    #     for i_val in tests:
    #         with self.subTest(i_val[0]):
    #             self.assertEqual(getattr(obj, i_val[1]), i_val[2])
    #
    #     with self.subTest('Conversion Factor Check'):
    #         self.assertAlmostEqual(obj.conversion, 2.3778669025433716)

    def test_form(self):
        # use to access Django test session URL (for a closed session and independent session)
        self.driver.get(f"{self.live_server_url}/converter/")
        # self.driver.get("http://localhost:8081/converter/")
        # stream_handler = logging.StreamHandler(sys.stdout)
        # logger.addHandler(stream_handler)
        # find elements on form to submit
        input_currency = self.driver.find_element(by=By.NAME, value='input_currency')
        input_value = self.driver.find_element(by=By.NAME, value='input_value')
        output_currency = self.driver.find_element(by=By.NAME, value='output_currency')
        # submit_button = self.driver.find_element(by=By.CSS_SELECTOR, value="button")
        # submit_button = self.driver.find_element(by=By.CSS_SELECTOR, value="submit")
        submit_button = self.driver.find_element(by=By.XPATH, value="//button[@type='submit']")

        # add input value in forms
        input_currency.send_keys('United States Dollar')
        input_value.send_keys(100)
        output_currency.send_keys('South Korean Won')

        # submit form
        submit_button.send_keys(Keys.RETURN)

        # check output value
        # output_currency = self.driver.find_element(by=By.NAME, value='output_currency')
        # value = output_currency.get_attribute(name='value')
        output_value = self.driver.find_element(by=By.NAME, value='output_value')
        value = output_value.get_attribute(name='value')

        # logging.getLogger().info('BBB')
        # logging.getLogger().info('Attribute type: {}'.format(type(value)))

        # get data from existing db
        obj = CurrencyConvert.objects.all()[0]

        self.assertAlmostEqual(float(value), obj.output_value)

#     #     with self.subTest('Output Currency Check'):
#     #         self.assertEqual(value, 'USD')
#     #
#     #     # with self.subTest('Initial Return Value Check'):
#     #     #     self.assertAlmostEqual(float(value), 6.469818557291871)
#     #
#     #     with self.subTest('Second Submit - Change Input Value Check'):
#     #         # input_currency = self.driver.find_element(by=By.NAME, value='input_currency')
#     #         input_value = self.driver.find_element(by=By.NAME, value='input_value')
#     #     #     # output_currency = self.driver.find_element(by=By.NAME, value='output_currency')
#     #         output_value = self.driver.find_element(by=By.NAME, value='output_value')
#     #         submit_button = self.driver.find_element(by=By.CSS_SELECTOR, value="button")
#     #     #     submit_button = self.driver.find_element(by=By.CLASS_NAME, value="btn btn-primary")
#     #     #
#     #     #     logging.info('Input value: {}, Output value: {}'.format(input_value.get_attribute(name='value'),
#     #     #                                                             output_value.get_attribute(name='value')))
#     #         input_value.clear()
#     #         input_value.send_keys(20)
#     #         submit_button.send_keys(Keys.RETURN)
#     #
#     #         new_output_value = self.driver.find_element(by=By.NAME, value='output_value')
#     #         value = new_output_value.get_attribute(name='value')
#     #
#     #         self.assertAlmostEqual(float(value), 12.93963711458374)
#     #
#     #     with self.subTest('Third Submit - Change Output Currency Check'):
#     #         # input_currency = self.driver.find_element(by=By.NAME, value='input_currency')
#     #         input_value = self.driver.find_element(by=By.NAME, value='input_value')
#     #         output_currency = self.driver.find_element(by=By.NAME, value='output_currency')
#     #         submit_button = self.driver.find_element(by=By.CSS_SELECTOR, value="button")
#     #
#     #         input_value.clear()
#     #         input_value.send_keys(20)
#     #         output_currency.clear()
#     #         output_currency.send_keys('EUR')
#     #         submit_button.send_keys(Keys.RETURN)
#     #
#     #         # output_currency = self.driver.find_element(by=By.NAME, value='output_currency')
#     #         new_output_value = self.driver.find_element(by=By.NAME, value='output_value')
#     #         value = new_output_value.get_attribute(name='value')
#     #
#     #         self.assertAlmostEqual(float(value), 11.841200034576305)
#     #
#     #     with self.subTest('Fourth Submit - Change Input Currency Check'):
#     #         input_currency = self.driver.find_element(by=By.NAME, value='input_currency')
#     #         submit_button = self.driver.find_element(by=By.CSS_SELECTOR, value='button')
#     #
#     #         input_currency.clear()
#     #         input_currency.send_keys('EUR')
#     #         submit_button.send_keys(Keys.RETURN)
#     #
#     #         new_output_value = self.driver.find_element(by=By.NAME, value='output_value')
#     #         value = new_output_value.get_attribute(name='value')
#     #
#     #         self.assertAlmostEqual(float(value), 20)
#     #
#     #     # logger.removeHandler(stream_handler)



