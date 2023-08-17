import datetime as dt

from django.db import models
from django.utils import timezone


# Create your models here.
class CountryCodes(models.Model):
    """model storing country code for each currency"""
    code = models.CharField(max_length=3, primary_key=True,
                            unique=True)
    currency = models.CharField(max_length=75, default=None)

    def __str__(self):
        return self.currency

    def get_currency_code_as_list(self):
        return [self.code]

    def get_currency_code(self):
        return self.code

    def get_currency_name(self):
        return self.currency


class ExchangeRates(models.Model):
    """db storing conversion values"""
    currency = models.CharField(max_length=75)     # from_currency
    code = models.CharField(max_length=3)

    to_USD = models.FloatField(default=0.0)     # conversion rate to USD for 1 from_currency
    to_EUR = models.FloatField(default=0.0)     # conversion rate to EUR for 1 from_currency
    to_GBP = models.FloatField(default=0.0)     # conversion rate to GBP for 1 from_currency
    to_JPY = models.FloatField(default=0.0)     # conversion rate to JPY for 1 from_currency
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.currency





