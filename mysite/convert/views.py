import requests, json

from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from django.db import IntegrityError

from mysite.settings import API_KEY

from .forms import CurrencyConvertForm
from .models import CountryCodes, Currencies


# Create your views here.
def home(request):
    """use form on home page to get input and output currecies"""

    if request.method == 'POST':
        form = CurrencyConvertForm(request.POST)
        if form.is_valid():
            input_curr = form.cleaned_data['input_currency']
            output_curr = form.cleaned_data['output_currency']
            # currency conversion logic
            # get db value for given -> USD
            conversion_to_usd = Currencies.object.all()
            # get db value for USD -> output
            # input_currency
            # input_value
            # output_currency
            # output_value
            return render(request, template_name='/converter/home.html',
                          context={'form': form})

    form = CurrencyConvertForm()

    return render(request, template_name='/converter/home.html',
                  context={'form': form})


def fetch_currency_symbols(request):
    """GET view to fetch all currencies and tickers to populate db"""

    # url_val to be made dynamic later -
    url_val = 'http://data.fixer.io/api/symbols'
    api_response = requests.get(url=url_val, params={'access_key': API_KEY})
    # convert results to json (provided api provides results as json objects)
    response = api_response.json()

    if response['success']:
        symbols = [_symb for _symb, _ in response['symbols'].items()]
        currency = [_country for _, _country in response['symbols'].items()]

        # save symbols and country to database
        objs_list, boolean_list = [], []
        for i_symbol, i_currency in zip(symbols, currency):
            try:
                obj, created = Currencies.objects.get_or_create(code=i_symbol,
                                                                currency=i_currency,
                                                                defaults={'currency': 'nameless currency'})
                objs_list.append(obj)
                boolean_list.append(created)
            except IntegrityError:
                # change to http reponse that says db is already populated
                return JsonResponse({'created': False, 'country': i_symbol,
                                     'currency': i_currency,
                                     'error': 'Currency already present in database'})
        # work with response data
        saved_objects = [True for i_value in boolean_list if i_value]
        return JsonResponse({'created': len(objs_list), 'saved': len(saved_objects)})

    return HttpResponse(response)


