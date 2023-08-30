import logging
from django import forms
from django.forms import ModelForm

from .models import CountryCodes, CurrencyConvert


class CurrencyTickerDelete(forms.Form):
    """form to enable use of DeleteView"""
    delete_confirm = forms.BooleanField(label='Confirm Deletion',
                                        widget=forms.CheckboxInput(),
                                        help_text='please confirm deletion',
                                        error_messages={'required': 'Please check box to confirm'},
                                        )


class ExchangeRateDelete(forms.Form):
    """delete all exchange rate data"""
    delete_confirm = forms.BooleanField(label='confirm deletion',
                                        widget=forms.CheckboxInput(),
                                        help_text='Please confirm deletion',
                                        error_messages={'required': 'Please check box to confirm'},
                                        )


class CurrencyConvertForm(forms.Form):
    """form to accept input and output currency"""

    # input values
    input_currency = forms.ModelChoiceField(queryset=CountryCodes.objects.all().order_by('currency'),
                                            required=True, help_text='Convert from',
                                            label='Convert from')
    input_value = forms.FloatField(label='Amount', required=True)
    # output values
    output_currency = forms.ModelChoiceField(queryset=CountryCodes.objects.all().order_by('currency'),
                                             required=True, help_text='Convert to',
                                             label='Convert to')
    output_value = forms.FloatField(label='Amount', required=False)


class CurrencyConvertDeleteForm(forms.Form):
    """delete all currency convert data"""
    delete_confirm = forms.BooleanField(label='confirm deletion',
                                        widget=forms.CheckboxInput(),
                                        help_text='Please confirm deletion',
                                        error_messages={'required': 'Please check box to confirm'},
                                        )




