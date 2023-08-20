import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from copy import copy
import datetime as dt

from django.test import TestCase
from django.utils import timezone

from convert.models import CountryCodes         # works only because of above hack changing sys.apth
from convert.models import ExchangeRates
from convert.models import CurrencyConvert


class CountryCodeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # set up objects used by all test methods
        CountryCodes.objects.create(code='ABX',
                                    currency='This is a test currency to test the model')

    def test_currency_label_max_length(self):
        curr = CountryCodes.objects.get(pk='ABX')
        max_length = curr._meta.get_field('currency').max_length
        self.assertEqual(max_length, 75)

    def test_get_currency_code(self):
        curr = CountryCodes.objects.get(pk='ABX')
        self.assertEqual(curr.get_currency_code(), 'ABX',
                         'Currency codes (ABX) do not match')

    def test_get_currency_name(self):
        curr = CountryCodes.objects.get(pk='ABX')
        self.assertEqual(curr.get_currency_name(),
                         'This is a test currency to test the model',
                         'Currency names do not match for ABX')


class ExchangeRatesTest(TestCase):
    """Test ExchangeRates model"""
    @classmethod
    def setUpTestData(cls):
        """setup data to test ExchangeRates model"""
        ExchangeRates.objects.create(code='ABX', currency='This is a test currency to test the model',
                                     to_USD=2.0, to_EUR=3.0, to_GBP=4.0, to_JPY=5.0)

    def test_updated_on(self):
        """check whether field updated_on is correct"""
        curr_obj = ExchangeRates.objects.get(pk=1)
        old_date = copy(curr_obj.updated_on)
        curr_obj.to_USD = 2.5
        curr_obj.updated_on = dt.datetime.now() + dt.timedelta(days=1)
        curr_obj.save()

        # checks if new value is updated
        curr = ExchangeRates.objects.get(pk=1)
        with self.subTest('to_USD Attribute check'):
            self.assertEqual(curr.to_USD, 2.5)

        with self.subTest('Updated on check'):
            self.assertGreater(curr.updated_on, old_date + dt.timedelta(days=1), '')

    def test_generate_conversions(self):
        response = {'success': True,
                    'rates': {'USD': 4.0, 'GBP': 2.0, 'JPY': 400, 'ABX': 500}}
        # get current objects
        obj = ExchangeRates.objects.get(pk=1)
        obj = obj.generate_conversions(response, symbol='ABX')

        subtest_checks = [('to_USD', 'USD Exchange Rate Check', 4/500),
                          ('to_EUR', 'EUR Exchange Rate Check', 1/500),
                          ('to_GBP', 'GBP Exchange Rate Check', 2/500),
                          ('to_JPY', 'JPY Exchange Rate Check', 400/500)]
        for field, error, check_values in subtest_checks:
            with self.subTest(error):
                self.assertEqual(getattr(obj, field), check_values,
                                 'Exchange rates do not match')


class CurrencyConvertTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        ExchangeRates.objects.create(code='ABX', currency='This is a test currency to test the model',
                                     to_USD=4/500, to_EUR=1/500, to_GBP=2/500, to_JPY=4/5)
        ExchangeRates.objects.create(code='USD', currency='This is a test US Dollar',
                                     to_USD=1.0, to_EUR=1/4, to_GBP=1/2, to_JPY=125)
        CurrencyConvert.objects.create(input_currency='ABX',
                                       output_currency='USD',
                                       input_value=10)

    def test_convert(self):
        """Test currency conversions"""
        conv = CurrencyConvert.objects.get(pk=1)
        conv.convert()

        with self.subTest('Test Conversion Factor'):
            self.assertEqual(conv.conversion, 0.008)

        with self.subTest('Test If Currency Converted'):
            self.assertEqual(conv.is_converted(), True, 'No Currency conversion')

        with self.subTest('Test Converted Value'):
            self.assertEqual(conv.converted(), 0.08)



