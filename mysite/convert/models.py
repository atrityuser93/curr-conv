from __future__ import annotations
from datetime import datetime
import logging
import requests

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

    def matching_exchange_rates(self, latest, url='', api_key=''):
        """get xchange rates that match the given CountryCodes object"""
        exchange_rate_obj = self.exchangerates_set.select_related().\
            filter(updated_on__gt=latest).order_by('updated_on').first()
        if exchange_rate_obj is None:
            logging.info('CountryCodes.matching_exchange_rates(): No Rates Found')
            exchange_rate_obj = ExchangeRates(base=self, url=url)
            exchange_rate_obj.save(api_key=api_key)
        return exchange_rate_obj


class ExchangeRates(models.Model, object):
    """db storing conversion values"""
    base = models.ForeignKey(CountryCodes, on_delete=models.CASCADE)
    to_USD = models.FloatField(default=0.0)     # conversion rate to USD for 1 from_currency
    to_EUR = models.FloatField(default=0.0)     # conversion rate to EUR for 1 from_currency
    to_GBP = models.FloatField(default=0.0)     # conversion rate to GBP for 1 from_currency
    to_JPY = models.FloatField(default=0.0)     # conversion rate to JPY for 1 from_currency
    updated_on = models.DateTimeField(default=timezone.now)
    url = models.URLField(max_length=250, default='')

    def __str__(self):
        return self.base.code

    def save(self, *args, **kwargs):
        # logging.info(f"Line 57 in ExchangeRates.save(): {kwargs['api_key']}")
        if 'api_key' in kwargs.keys():
            self.populate_conversions(api_key=kwargs['api_key'])
        else:
            self.populate_conversions()
        return super(ExchangeRates, self).save()

    def eur_per_unit(self):
        return self.to_EUR

    # @classmethod
    # def create_rates(cls, **kwargs):
    #     # obj = ExchangeRates(kwargs)
    #     # logging.info(f"ExchnageRates.create_rates(): Object Attributes base {type(kwargs['base'])}")
    #     # obj.populate_conversions(kwargs['api_key'])
    #     return cls(kwargs)

    def _request_api_call(self, api_key: str):
        """call fixer.io api and get response as JSON objects.
        Provides EUR (fixed base) to OTHER conversion rates.
        Output is JSON"""

        logging.info(f'ExchnageRates._request_api_call(): Object Attributes base {self.base_id}')
        currency_list = ['USD', 'GBP', 'JPY', self.base.get_currency_code()]
        symbol_list = ','.join(currency_list)
        # logging.info('{}'.format(symbol_list))
        if not api_key:
            return {'success': False, 'rates': {'USD': None, 'GBP': None, 'JPY': None},
                    'error': {'info': 'No API Key give', 'code': 101}}

        api_response = requests.get(url=self.url, params={'access_key': api_key,
                                                          'symbols': symbol_list}
                                    )
        return api_response.json()

    def _calculate_conversions(self, response):
        """convert JSON response to values that could be used
        for conversion between different currencies"""

        if response["success"]:
            usd_per_eur = response["rates"]["USD"]
            gbp_per_eur = response["rates"]["GBP"]
            jpy_per_eur = response["rates"]["JPY"]
            sym_per_eur = response["rates"][self.base.get_currency_code()]
            # convert to USD, GBP and JPY
            usd__sym = usd_per_eur / sym_per_eur
            gbp__sym = gbp_per_eur / sym_per_eur
            jpy__sym = jpy_per_eur / sym_per_eur

            # logging.info('generate_conversions: {} to EUR: {}'.format(symbol.code, 1 / sym_per_eur))
            # logging.info('generate_conversions: USD per EUR: {}'.format(usd_per_eur))
            # logging.info('generate_conversions: {} to USD: {}'.format(symbol.code, usd__sym))

            self.to_USD = usd__sym
            self.to_EUR = 1 / sym_per_eur
            self.to_GBP = gbp__sym
            self.to_JPY = jpy__sym
            self.updated_on = timezone.now()
            logging.info('generate_conversion: Update objects. '
                         'Not Saved. \n Updated on: {}'.format(self.updated_on))
            # self.save(update_fields=['to_USD', 'to_EUR', 'to_GBP', 'to_JPY', 'updated_on'])

        else:
            if 'error' not in response.keys() and 'code' not in response.keys():
                logging.info('API call unsuccessful. Error undetermined.')

            logging.info('API call unsuccessful. Error: {} and '
                         'Error code: {}'.format(response["error"]["info"],
                                                 response["error"]["code"]))

    def populate_conversions(self, api_key=''):
        """Populate ExchangeRate model attributes"""
        response = self._request_api_call(api_key=api_key)
        self._calculate_conversions(response)


class CurrencyConvert(models.Model):
    """db to store different conversions - db of records"""
    input_currency = models.ForeignKey(ExchangeRates, on_delete=models.CASCADE,
                                       related_name='input_rate')
    output_currency = models.ForeignKey(ExchangeRates, on_delete=models.CASCADE,
                                        related_name='output_rate')
    input_value = models.FloatField(default=1.0)
    output_value = models.FloatField(default=0.0)
    conversion = models.FloatField(default=1.0)
    _is_converted = models.BooleanField(default=False)
    asked_on = models.DateTimeField(default=timezone.now)

    # self.convert()

    def __str__(self):
        return self.input_currency

    def save(self, *args, **kwargs):
        # logging.info('models: %s{} and %s{}'.format(self.input_currency, self.output_currency))
        return super(CurrencyConvert, self).save(*args, **kwargs)

    def convert(self, **kwargs):
        """Implements currency conversion logic between input and output currencies"""

        # logging.info('models: In type: {} Out type {}'.format(type(curr_in), type(curr_out)))
        # use EUR as base currency (Determined by API capabilities)
        # self.conversion = currency_in.to_EUR / currency_out.to_EUR
        self.conversion = self.input_currency.eur_per_unit() / \
                          self.output_currency.eur_per_unit()

        self.convert_currency()         # perform currency conversion
        self.save(**kwargs)             # save object after conversion

        return self

    def convert_currency(self):
        """convert between currency values"""
        self.output_value = self.conversion * self.input_value
        self._is_converted = True

    def converted(self):
        return self.output_value

    def is_converted(self):
        return self._is_converted

    def dict(self):
        """return class instance as a dictionary of key value pairs"""
        return self.__dict__

    def _get_conversion_rates(self, url, api_key) -> (ExchangeRates, ExchangeRates):
        """use fixer.io APIs to fetch latest conversion rates (once a day)"""

        # logging.info('fetch conversion rates')
        # get conversion value for given symbol within last one week
        one_week = datetime.today() - timezone.timedelta(days=7)

        currency_in = self._query_or_create(symbol=str(self.input_currency), updated_on=one_week,
                                            url_val=url, api_key=api_key)
        currency_out = self._query_or_create(symbol=str(self.output_currency), updated_on=one_week,
                                             url_val=url, api_key=api_key)

        # logging.info('Currency In type: {} Currency Out type: {}'.format(type(currency_in),
        #                                                                  type(currency_out)))
        # logging.info('Save object type 1: {} and 2: {}'.format(type(currency_in), type(currency_out)))
        return currency_in, currency_out

    def _query_or_create(self, symbol: str, updated_on: timezone.datetime,
                         url_val: str, api_key: str) -> ExchangeRates:
        """query db for existing value, if emtpy create new object and add to db"""

        # check if currency exchange is in db
        currency_query = ExchangeRates.objects.filter(code=symbol,
                                                      updated_on__gt=updated_on).order_by("updated_on")
        if currency_query:
            # check if exchange rate is updated
            # currency_query_time = currency_query.filter(updated_on__gt=updated_on).order_by("updated_on")
            objs = currency_query.first()
            logging.info('query_or_create (updated rates exists): '
                         'currency object {}'.format(objs))
            return objs

        # if query set is empty get latest conversion rate for
        # symbol and add to db
        logging.info('query_or_create(data does not exist/data is old): '
                     'creating new/updated record for {}'.format(symbol))
        # response = self._request_api_call(url_val=url_val, symbol=symbol, api_key=api_key)
        # new ExchangeRates obj
        curr_obj = CountryCodes.objects.all().get(pk=symbol)
        objs = ExchangeRates(code=curr_obj.code, currency=curr_obj.currency)
        response = self._request_api_call(url_val=url_val, symbol=curr_obj.code, api_key=api_key)
        objs = objs.generate_conversions(response, symbol=curr_obj.code)
        # save new exchange obj
        objs.save()
        return objs

    @staticmethod
    def _request_api_call(url_val: str, symbol: str, api_key: str):
        """call fixer.io api and get response as JSON objects.
        Provides EUR (fixed base) to OTHER conversion rates.
        Output is JSON"""

        currency_list = ['USD', 'GBP', 'JPY', symbol]

        # logging.info('Make API call for {}'.format(symbol))
        symbol_list = ','.join(currency_list)
        # logging.info('{}'.format(symbol_list))
        api_response = requests.get(url=url_val, params={'access_key': api_key,
                                                         'symbols': symbol_list}
                                    )
        return api_response.json()






