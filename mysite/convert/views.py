from django.shortcuts import render
from django.http import Http404
from .forms import CurrencyConvertForm
from .models import Currencies


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
