import datetime as dt

from django.db import models
from django.utils import timezone


# Create your models here.
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



