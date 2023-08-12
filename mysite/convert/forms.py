from django import forms

from .models import CurrencyConvert


class CurrencyConvertForm(forms.Form):
    """form to accept input and output currency"""

    input_currency = forms.CharField(label='Currency From')
    input_value = forms.FloatField(label='Amount')
    output_currency = forms.CharField(label='Currency To')
    output_value = forms.FloatField(label='Amount')





