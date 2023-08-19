from django.test import TestCase

from ..convert.models import CountryCodes


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

