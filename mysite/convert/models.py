import datetime as dt

from django.db import models
from django.utils import timezone


# Create your models here.
class CountryCodes(models.Model):
    """model storing country code for each currency"""
    code = models.CharField(max_length=3, primary_key=True,
                            unique=True)
    currency = models.CharField(max_length=75, default=None)


class Currencies(models.Model):
    """model storing currency to USD conversion rates"""
    country = models.CharField(max_length=25)
    code = models.CharField(max_length=3, default='XXX')
    currency = models.FloatField(name='Currency')
    usd_rate = models.FloatField(name='USD')
    fetched_on = models.DateTimeField(default=timezone.now)

    # def is_fetched_today(self):
    #     """check if obj fetched today"""
    #     return self.fetched_on

    def get_fetched_on(self):
        return self.fetched_on

    def __str__(self):
        return self.country


class CurrencyConvert(models.Model):
    """db storing conversion values"""
    from_currency = models.CharField(max_length=10)     # from_currency
    from_value = models.FloatField(default=1.0)         # from_value
    to_currency = models.CharField(max_length=10)       # to_currency
    to_value = models.FloatField(default=1.0)            # to_value
    conversion = models.FloatField(default=0.0)         # conversion rate
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.from_currency



