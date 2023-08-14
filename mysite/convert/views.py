import requests, logging
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from django.db import IntegrityError
from django.utils import timezone

from django.views.generic import ListView

from mysite.settings import API_KEY

from .forms import CurrencyConvertForm, CurrencyTickerDelete
from .models import CountryCodes, CurrencyConvert


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
            # currency conversion logic
            # get db value for given -> USD
            # conversion_to_usd = Currencies.object.all()
            # get db value for USD -> output
            conversion = fetch_conversion_rates(input_curr_symbol, output_curr_symbol)
            output_value = input_value * conversion

            logging.info('{} {} is {} {}'.format(input_value, input_curr_symbol,
                                                 output_value, output_curr_symbol))
            return render(request, template_name='converter/home.html',
                          context={'form': form})

    form = CurrencyConvertForm()

    return render(request, template_name='converter/home.html',
                  context={'form': form})


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
                logging.info('Before creation {}: {}'.format(i_symbol, i_currency))
                obj, created = CountryCodes.objects.get_or_create(code=i_symbol,
                                                                  currency=i_currency,
                                                                  defaults={'currency': 'nameless currency'})
                logging.info('After creation {}: {}'.format(obj.code, obj.currency))
                added_objs_list.append(obj)
                boolean_list.append(created)
            except IntegrityError:
                # change to http reponse that says db is already populated
                logging.exception('IntegrityError exception. '
                                  'Currency {} {} already present'.format(i_symbol, i_currency))
                # return JsonResponse({'created': False, 'country': i_symbol,
                #                      'currency': i_currency,
                #                      'error': 'Currency already present in database'})
        # work with response data
        saved_objects = [True for i_value in boolean_list if i_value]
        return JsonResponse({'created': len(objs_list), 'saved': len(saved_objects)})

    return HttpResponse(response)


def delete_currency_symbols(request):
    """DELETE view to remove all currencies from db"""

    form = CurrencyTickerDelete()
    if request.method == 'POST':
        if request.POST['delete_confirm']:
            # delete all country codes in db
            CountryCodes.objects.all().delete()
            return HttpResponse('All currencies deleted')

        return render(request, template_name='converter/delete.html',
                      context={'form': form})

    return render(request, template_name='converter/delete.html',
                  context={'form': form})


class AvailableCurrencyListView(ListView):
    """list view to see all available currencies (and codes) in db"""

    model = CountryCodes
    template_name = 'converter/country-list.html'
    context_object_name = 'codes'

    def get_queryset(self):
        return super().get_queryset()


def fetch_conversion_rates(symbol_in, symbol_out):

    logging.info('fetch/update conversion rates')
    currency_in, currency_out = update_conversion_rates(symbol_in, symbol_out)
    # convert between currency_in and currency_out through USD
    currency_in_2_usd = currency_in.objects.values("to_USD")
    currency_out_2_usd = currency_out.objects.values("to_USD")

    currency_in_2_out = currency_out_2_usd / currency_in_2_usd

    logging.info('1 {} is {} {}'.format(currency_in, currency_in_2_out, currency_out))
    return currency_in_2_out


def update_conversion_rates(symbol_1, symbol_2):
    """use fixer.io APIs to fetch latest conversion rates (once a day)"""

    logging.info('fetch conversion rates')
    # url_val to be made dynamic later -
    url_val = 'http://data.fixer.io/api/latest'
    # get conversion value for given symbol within last one week
    # query_symbol = CurrencyConvert.objects.filter(from_currency=symbol)
    one_week = datetime.today() - timezone.timedelta(days=7)
    currency_in = CurrencyConvert.objects.filter(from_currency=symbol_1,
                                                 updated_on__gt=one_week)
    logging.info('{}'.format(currency_in))
    currency_out = CurrencyConvert.objects.filter(from_currency=symbol_2,
                                                  updated_on__gt=one_week)
    logging.info('{}'.format(currency_out))

    if not currency_in:
        # get latest conversion rate and update db
        currency_in, flag = save_convert_object(url_val, symbol_1)
        if flag:
            # new value added to db
            pass

    if not currency_out:
        # get latest conversion rate and update db
        currency_out, flag = save_convert_object(url_val, symbol_2)
        if flag:
            # new value added to db
            pass

    return currency_in, currency_out


def request_api_call(url_val, symbol, currency_list):
    """call fixer.io api and get conversion response as JSON objects"""

    if currency_list is not None:
        currency_list += ['USD', 'EUR', 'GBP', 'JPY']
    else:
        currency_list = ['USD', 'EUR', 'GBP', 'JPY']

    logging.info('Make API call for {}'.format(symbol))
    symbol_list = currency_list + symbol
    api_response = requests.get(url=url_val, params={'access_key': API_KEY,
                                                     'symbols': symbol_list}
                                )
    return api_response.json()


def save_convert_object(url_val, symbol, currency_list=None):
    """get new conversion values update database"""
    response = request_api_call(url_val, symbol, currency_list)

    if response["success"]:
        logging.info('API call successful')
        obj = CurrencyConvert(from_currency=symbol,
                              to_USD=response["rates"]["USD"],
                              to_EUR=1 / response["rates"]["EUR"],
                              to_GBP=response["rates"]["GBP"],
                              to_JPY=response["rates"]["JPY"]
                              )
        logging.info('{} to USD'.format(symbol, response["rates"]["USD"]))
        obj.save()
        logging.info('Updated Object saved')
        return obj, True

    else:
        logging.info('API call unsuccessful. Error: {} and Error code: {}'.format(response["error"]["info"],
                                                                                  response["error"]["code"]))
        return None, False

