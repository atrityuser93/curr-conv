import requests, logging
from datetime import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.db import IntegrityError
from django.utils import timezone
from django.urls import reverse_lazy
# from django.db

from django.views.generic import ListView

from mysite.settings import API_KEY

from .forms import CurrencyConvertForm, CurrencyTickerDelete, CurrencyConvertDelete
from .models import CountryCodes, ExchangeRates


# Create your views here.
def home(request):
    """use form on home page to get input and output currecies"""

    if request.method == 'POST':
        form = CurrencyConvertForm(request.POST)
        if form.is_valid():
            logging.info('Validated form')
            input_curr_symbol = form.cleaned_data['input_currency']
            output_curr_symbol = form.cleaned_data['output_currency']
            input_value = form.cleaned_data['input_value']
            logging.info('Input currency: {} and Output currency: {}'.format(input_curr_symbol,
                                                                             output_curr_symbol))
            # currency conversion logic
            # get db value for given -> USD
            # conversion_to_usd = Currencies.object.all()
            # get db value for USD -> output
            conversion = fetch_conversion_rates(input_curr_symbol, output_curr_symbol)
            # output_value = convert_currency(input_value, input_curr_symbol, output_curr_symbol)
            output_value = input_value * conversion

            logging.info('{} {} is {} {}'.format(input_value, input_curr_symbol,
                                                 output_value, output_curr_symbol))
            # form = CurrencyConvertForm(data={'input_currency': CountryCodes.objects.all().get(pk=input_curr_symbol)})
            return render(request, template_name='converter/home.html',
                          context={'form': form, 'complete': True, 'output_value': output_value})

    # get initial value for all form fields

    # form = CurrencyConvertForm(initial={'input'})
    form = CurrencyConvertForm()

    return render(request, template_name='converter/home.html',
                  context={'form': form, 'complete': False})


def initial_form_value():
    """get values of your choosing to initialize form"""
    # input_curr_sym
    # output_curr_sym
    # input_val
    # output_val
    return None


def convert_currency(input_value, currency_in, currency_out):
    """perform actual conversion between input and
    output currency - given conversioon value"""
    conversion = fetch_conversion_rates(currency_in, currency_out)
    return None


def fetch_currency_symbols(request):
    """GET view to fetch all currencies and tickers to populate db"""

    # url_val to be made dynamic later -
    url_val = 'http://data.fixer.io/api/symbols'
    # use `requests` to fetch value from API
    api_response = requests.get(url=url_val, params={'access_key': API_KEY})
    # get json objects in response (provided api provides results as json objects)
    response = api_response.json()

    if response['success']:
        symbols = [_symb for _symb, _ in response['symbols'].items()]
        currency = [_country for _, _country in response['symbols'].items()]

        # save symbols and country to database
        objs_list, added_objs_list, boolean_list = [], [], []
        for i_symbol, i_currency in zip(symbols, currency):
            try:
                # logging.info('Before creation {}: {}'.format(i_symbol, i_currency))

                obj = CountryCodes.objects.create(code=i_symbol,
                                                  currency=i_currency,
                                                  )
                # logging.info('After creation {}: {}'.format(obj.code, obj.currency))
                added_objs_list.append(obj)
                # boolean_list.append(created)
            except IntegrityError:
                # change to http reponse that says db is already populated
                # logging.exception('IntegrityError exception. '
                #                   'Currency {} {} already present'.format(i_symbol, i_currency))
                objs_list.append(CountryCodes.objects.get(code=i_symbol))
                continue
                # return JsonResponse({'created': False, 'country': i_symbol,
                #                      'currency': i_currency,
                #                      'error': 'Currency already present in database'})
        # work with response data
        return JsonResponse({'created': len(objs_list), 'created and saved': len(added_objs_list)})

    return HttpResponse(response)


def delete_currency_symbols(request):
    """DELETE view to remove all currencies from db"""

    form = CurrencyTickerDelete()
    if request.method == 'POST':
        if request.POST['delete_confirm']:
            # delete all country codes in db
            CountryCodes.objects.all().delete()
            return redirect(reverse_lazy('symbol-list'))

        return render(request, template_name='converter/delete-currency-list.html',
                      context={'form': form})

    return render(request, template_name='converter/delete-currency-list.html',
                  context={'form': form})


class AvailableCurrencyListView(ListView):
    """list view to see all available currencies (and codes) in db"""

    model = CountryCodes
    template_name = 'converter/country-list.html'
    context_object_name = 'codes'

    def get_queryset(self):
        return super().get_queryset()


def delete_exchange_rates(request):
    """delete all collected exchange rates"""
    form = CurrencyConvertDelete()
    if request.method == 'POST':
        if request.POST['delete_confirm']:
            # delete all country codes in db
            ExchangeRates.objects.all().delete()
            return redirect(reverse_lazy('rates-list'))

        return render(request, template_name='converter/delete-exchange-rates.html',
                      context={'form': form})

    return render(request, template_name='converter/delete-exchange-rates.html',
                  context={'form': form})


class AvailableExchangeRatesView(ListView):
    """list view to see all available exchange rates"""
    
    model = ExchangeRates
    template_name = 'converter/exchange-list.html'
    context_object_name = 'rates'
    
    def get_queryset(self):
        return super().get_queryset()
    

def fetch_conversion_rates(symbol_in: CountryCodes, symbol_out: CountryCodes):

    # logging.info('fetch/update conversion rates symbol_in {} and symbol_out {}'.format(type(symbol_in),
    #                                                                                    type(symbol_out)))
    currency_in, currency_out = get_conversion_rates(symbol_in, symbol_out)
    logging.info('currency in: {} and currency out: {}'.format(currency_in.code,
                                                               currency_out.code))
    # use EUR as base currency (Determined by API capabilities)
    currency_in_2_out = currency_in.to_EUR/currency_out.to_EUR

    logging.info('1 {} is {} {}'.format(currency_in.code,
                                        currency_in_2_out,
                                        currency_out.code))
    return currency_in_2_out


def get_conversion_rates(symbol_1: CountryCodes, symbol_2: CountryCodes) -> \
        (ExchangeRates, ExchangeRates):
    """use fixer.io APIs to fetch latest conversion rates (once a day)"""

    # logging.info('fetch conversion rates')
    # url_val to be made dynamic later -
    url_val = 'http://data.fixer.io/api/latest'
    # get conversion value for given symbol within last one week
    # query_symbol = ExchangeRates.objects.filter(from_currency=symbol)
    one_week = datetime.today() - timezone.timedelta(days=7)

    currency_in = query_or_create(symbol=symbol_1, updated_on=one_week, url_val=url_val)
    currency_out = query_or_create(symbol=symbol_2, updated_on=one_week, url_val=url_val)

    # logging.info('Currency In type: {} Currency Out type: {}'.format(type(currency_in),
    #                                                                  type(currency_out)))

    # logging.info('Save object type 1: {} and 2: {}'.format(type(currency_in), type(currency_out)))
    return currency_in, currency_out


def query_or_create(symbol: CountryCodes, updated_on: timezone.datetime, url_val: str):
    """query db for existing value, if emtpy create new object and add to db"""

    # check if currency exchange is in db
    currency_query = ExchangeRates.objects.filter(code=symbol.code)
    if currency_query:
        # check if exchange rate is updated
        currency_query_time = currency_query.filter(updated_on__gt=updated_on).order_by("updated_on")
        logging.info('query_or_create (currency exists): currency_query_time {}'.format(type(currency_query_time)))

        if currency_query_time:
            # return relevant object if updated results are present
            objs = currency_query_time.first()
            logging.info('query_or_create (data exists): objs {}'.format(type(objs)))
            return objs

        else:
            # return updated conversion object by getting updates through API call
            response = request_api_call(url_val=url_val, symbol=symbol)
            objs = generate_conversions(response, symbol, old_obj=currency_query.values())
            objs.save()         # save updated object
            logging.info('query_or_create (data is old): objs {}'.format(type(objs)))
            return objs

    else:
        # if query set is empty get latest conversion rate for
        # non-existing row and add to db
        logging.info('query_or_create(data does not exist) '
                     'Creating new object for symbol {}'.format(symbol.code))
        currency_obj = create_convert_object(url_val, symbol)
        return currency_obj


def create_convert_object(url_val: str, symbol: CountryCodes, currency_list=None) -> (ExchangeRates, bool):
    """get new conversion values update database"""
    response = request_api_call(url_val, symbol)
    obj = generate_conversions(response, symbol)
    obj.save()
    # logging.info('Updated Object saved')
    return obj


# list of functions
# request API and get response for EUR (fixed based) to OTHER conversion rates
def request_api_call(url_val: str, symbol: CountryCodes):
    """call fixer.io api and get response as JSON objects.
    Provides EUR (fixed base) to OTHER conversion rates.
    Output is JSON"""

    currency_list = ['USD', 'GBP', 'JPY']

    # logging.info('Make API call for {}'.format(symbol))
    all_symbols = currency_list + symbol.get_currency_code_as_list()
    symbol_list = ','.join(all_symbols)
    # logging.info('{}'.format(symbol_list))
    api_response = requests.get(url=url_val, params={'access_key': API_KEY,
                                                     'symbols': symbol_list}
                                )
    return api_response.json()


# convert response to storable value
def generate_conversions(response, symbol: CountryCodes, old_obj: ExchangeRates = None) -> ExchangeRates:
    """convert JSON response to values that could be used
    for conversion between different currencies"""

    if response["success"]:
        usd_per_eur = response["rates"]["USD"]
        gbp_per_eur = response["rates"]["GBP"]
        jpy_per_eur = response["rates"]["JPY"]
        sym_per_eur = response["rates"][symbol.code]
        # convert to USD, GBP and JPY
        usd__sym = usd_per_eur / sym_per_eur
        gbp__sym = gbp_per_eur / sym_per_eur
        jpy__sym = jpy_per_eur / sym_per_eur

        logging.info('generate_conversions: {} to EUR: {}'.format(symbol.code, 1 / sym_per_eur))
        logging.info('generate_conversions: USD per EUR: {}'.format(usd_per_eur))
        logging.info('generate_conversions: {} to USD: {}'.format(symbol.code, usd__sym))

        if old_obj is None:
            # create ExchangeRates object w/o saving
            obj = ExchangeRates(code=symbol.code,
                                  currency=symbol.currency,
                                  to_USD=usd__sym,
                                  to_EUR=1/sym_per_eur,
                                  to_GBP=gbp__sym,
                                  to_JPY=jpy__sym)
            # logging.info('generate_conversions: obj type {}'.format(type(obj)))
            return obj
        else:
            # update existing ExchangeRates object
            if old_obj.code == symbol.code and \
                    old_obj.currency == symbol.currency:
                old_obj.to_USD = usd__sym
                old_obj.to_EUR = 1 / sym_per_eur
                old_obj.to_GBP = gbp__sym
                old_obj.to_JPY = jpy__sym
                logging.info('generate_conversion: Update objects. Not Saved')
            else:
                logging.info('generate_conversion: Currency codes do not match. Will not update data.')
            return old_obj
    else:
        logging.info('API call unsuccessful. Error: {} and Error code: {}'.format(response["error"]["info"],
                                                                                  response["error"]["code"]))
        obj = ExchangeRates()
        logging.info('generate_conversion: Empty obj type {}'.format(type(obj)))
        # return empty object
        return obj

# create object and save object to db
# update existing object
