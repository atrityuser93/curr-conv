import requests, logging
from datetime import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse_lazy

from django.views.generic import ListView

from django.conf import settings

from .forms import CurrencyConvertForm, CurrencyTickerDelete, ExchangeRateDelete
from .forms import CurrencyConvertDeleteForm
from .models import CountryCodes, ExchangeRates, CurrencyConvert


# Create your views here.
def home(request):
    """use form on home page to get input and output currecies"""

    if request.method == 'POST':
        form = CurrencyConvertForm(request.POST)
        if form.is_valid():
            logging.info('Validated form')
            input_curr = form.cleaned_data['input_currency']
            output_curr = form.cleaned_data['output_currency']
            input_value = form.cleaned_data['input_value']

            # create conversion object (for storing call in db)
            one_week = datetime.today() - timezone.timedelta(days=7)

            # check for existing ExchangeRate instances that match
            input_object = input_curr.matching_exchange_rates(latest=one_week,
                                                              url='http://data.fixer.io/api/latest',
                                                              api_key=settings.API_KEY
                                                              )
            # logging.info(f'Line 41 in views.home: input_query object: {type(input_object)}')
            output_object = output_curr.matching_exchange_rates(latest=one_week,
                                                                url='http://data.fixer.io/api/latest',
                                                                api_key=settings.API_KEY)
            # logging.info(f'Line 57 in views.home: output_query object: {type(output_object)}')

            conv_obj = CurrencyConvert(input_value=input_value,
                                       input_currency=input_object,
                                       output_currency=output_object,
                                       )
            conv_obj.convert()

            logging.info('{} {} is {} {}'.format(conv_obj.input_value, conv_obj.input_currency,
                                                 conv_obj.output_value, conv_obj.output_currency))

            # form.cleaned_data["output_value"] = conv_obj.output_value
            form = CurrencyConvertForm(initial=conv_obj.to_dict())

            return render(request, template_name='converter/home.html',
                          context={'form': form, 'complete': True})

    # get initial value for all form fields

    # form = CurrencyConvertForm(initial={'input'})
    form = CurrencyConvertForm()

    return render(request, template_name='converter/home.html',
                  context={'form': form, 'complete': False})


def delete_convert_history(request):
    """Delete complete history of all fetched conversions.
    Only use for maintenance"""
    form = CurrencyConvertDeleteForm()
    if request.method == "POST":
        if request.POST['delete_confirm']:
            CurrencyConvert.objects.all().delete()
            return redirect(reverse_lazy('convert-list'))

        return render(request, template_name='converter/delete-conversions.html',
                      context={'form': form})
    return render(request, template_name='converter/delete-conversions.html',
                  context={'form': form})


class ConvertCallsView(ListView):
    """view all convert calls made so far"""
    model = CurrencyConvert
    template_name = 'converter/convert-list.html'
    context_object_name = 'calls'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-asked_on')


def fetch_currency_symbols(request):
    """GET view to fetch all currencies and tickers to populate db"""

    # url_val to be made dynamic later -
    url_val = 'http://data.fixer.io/api/symbols'
    # use `requests` to fetch value from API
    api_response = requests.get(url=url_val, params={'access_key': settings.API_KEY})
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
    form = ExchangeRateDelete()
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
        queryset = super().get_queryset()
        return queryset.order_by('base')
    

class SearchExchangeRatesView(ListView):
    model = ExchangeRates
    template_name = 'converter/search_rates.html'
    context_object_name = 'rates'

    def get_queryset(self):
        search_query = self.request.GET.get('search_rates_query')
        rates = ExchangeRates.objects.filter(Q(base__code=search_query) |
                                             Q(base__currency__contains=search_query))
        return rates

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['result_count'] = self.get_queryset().count()
        context['search_keyword'] = self.request.GET.get('search_rates_query')
        return context


class SearchCountryCodesView(ListView):
    model = CountryCodes
    template_name = 'converter/search_codes.html'
    context_object_name = 'codes'

    def get_queryset(self):
        search_query = self.request.GET.get('search_codes_query')
        codes = CountryCodes.objects.filter(Q(code__contains=search_query) |
                                            Q(currency__contains=search_query))
        return codes

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['result_count'] = self.get_queryset().count()
        context['search_keyword'] = self.request.GET.get('search_codes_query')
        return context

# create object and save object to db
# update existing object
