from django import forms

from .models import CountryCodes


class CurrencyTickerDelete(forms.Form):
    """form to enable use of DeleteView"""
    delete_confirm = forms.BooleanField(label='Confirm Deletion',
                                        widget=forms.CheckboxInput(),
                                        help_text='please confirm deletion',
                                        error_messages={'required': 'Please check box to confirm'},
                                        )


class CurrencyConvertDelete(forms.Form):
    """delete all exchange rate data"""
    delete_confirm = forms.BooleanField(label='confirm deletion',
                                        widget=forms.CheckboxInput(),
                                        help_text='please confirm deletion',
                                        error_messages={'required': 'Please check box to confirm'},
                                        )


class CurrencyConvertForm(forms.Form):
    """form to accept input and output currency"""

    # input_currency_name = forms.CharField(label='From (Currency) ')
    # input_country = forms.ModelChoiceField
    # new_query_set = CountryCodes.objects.all().only('code')
    input_currency = forms.ModelChoiceField(queryset=CountryCodes.objects.all().order_by('currency'),
                                            required=True, help_text='Convert from',
                                            label='Convert from')
    # input_currency_all = forms.ModelChoiceField(queryset=CountryCodes.objects.all(),
    #                                             required=True, help_text='Convert from',
    #                                             label='Convert from')
    input_value = forms.FloatField(label='Amount', required=True)
    # output_currency = forms.CharField(label='To (Currency)')
    output_currency = forms.ModelChoiceField(queryset=CountryCodes.objects.all().order_by('currency'),
                                             required=True, help_text='Convert to',
                                             label='Convert to')
    # output_value = forms.FloatField(label='Amount')





