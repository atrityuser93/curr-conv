import requests, logging

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
# from django.utils import timezone
from django.urls import reverse_lazy
# from django.db

from django.views.generic import ListView

from django.conf import settings

from .forms import CurrencyConvertForm, CurrencyTickerDelete, CurrencyConvertDelete
from .forms import CurrencyConvertDisplayForm
from .models import CountryCodes, ExchangeRates, CurrencyConvert


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
            # logging.info('Input currency: {} and '
            #              'Output currency: {}'.format(input_curr_symbol,
            #                                           output_curr_symbol))
            logging.info('Input type: {} Output type: {}'.format(type(input_curr_symbol),
                                                                 type(output_curr_symbol)))
            # create conversion object (for storing call in db)
            conv_obj = CurrencyConvert(input_value=input_value,
                                       input_currency=str(input_curr_symbol.code),
                                       output_currency=str(output_curr_symbol.code),
                                       )
            conv_obj.convert(url='http://data.fixer.io/api/latest',
                             api_key=settings.API_KEY)
            # logging.info('home: convert object input_currency: %s{}, '
            #              'output_currency: %s{}'.format(conv_obj.input_currency,
            #                                             conv_obj.output_currency))
            # logging.info(conv_obj.input_currency)
            # logging.info(conv_obj.output_currency)

            logging.info('{} {} is {} {}'.format(conv_obj.input_value, conv_obj.input_currency,
                                                 conv_obj.output_value, conv_obj.output_currency))

            # form.cleaned_data["output_value"] = conv_obj.output_value
            form = CurrencyConvertDisplayForm(instance=conv_obj)
            # logging.info('{}'.format(vars(form)))

            return render(request, template_name='converter/home.html',
                          context={'form': form, 'complete': True})

    # get initial value for all form fields

    # form = CurrencyConvertForm(initial={'input'})
    form = CurrencyConvertForm()

    return render(request, template_name='converter/home.html',
                  context={'form': form, 'complete': False})


# class ConvertView(CreateView):
#     """class-based view to create a convert currency object"""
#     form_class = ConvertForm
#     success_url = reverse_lazy('convert-list')
#     template_name = 'converter/convert.html'
#
#     def form_valid(self, form):
#         """override class method when form.is_valid() is True"""
#         logging.info('form_valid: form is valid')
#         self.object = form.save(commit=False)
#         self.object.convert(url='http://data.fixer.io/api/latest',
#                             api_key=API_KEY)
#
#         logging.info('ConvertView: form.object type {}'.format(type(self.object)))
#         self.object.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#     def is_valid(self):
#         pass


def initial_form_value():
    """get values of your choosing to initialize form"""
    # input_curr_sym
    # output_curr_sym
    # input_val
    # output_val
    return None


class ConvertCallsView(ListView):
    """view all convert calls made so far"""
    model = CurrencyConvert
    template_name = 'converter/convert-list.html'
    context_object_name = 'calls'

    def get_queryset(self):
        return super().get_queryset()


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
    

# create object and save object to db
# update existing object
