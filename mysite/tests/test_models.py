import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from django.test import TestCase

from convert.models import CountryCodes         # works only because of above hack changing sys.apth


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
        self.assertEqual(curr.get_currency_code(), 'ABX')

    def test_get_currency_name(self):
        curr = CountryCodes.objects.get(pk='ABX')
        self.assertEqual(curr.get_currency_name(), 'This is a test currency to test the model')

