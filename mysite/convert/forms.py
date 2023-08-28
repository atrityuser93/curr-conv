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


class CurrencyConvertDisplayForm(ModelForm):
    """class used CurrencyConvert model to display results"""
    class Meta:
        model = CurrencyConvert
        fields = ('input_currency', 'input_value', 'output_currency', 'output_value')
        template_name = 'converter/'

    def save(self, commit=True):
        conv = super(CurrencyConvertDisplayForm, self).save(commit=False)
        if commit:
            conv.save()
        return conv


class CurrencyConvertDeleteForm(forms.Form):
    """delete all currency convert data"""
    delete_confirm = forms.BooleanField(label='confirm deletion',
                                        widget=forms.CheckboxInput(),
                                        help_text='Please confirm deletion',
                                        error_messages={'required': 'Please check box to confirm'},
                                        )
# class ConvertForm(ModelForm):
#     """model-based form for currency conversion"""
#
#     input_currency = forms.ModelChoiceField(queryset=CountryCodes.objects.all().order_by('currency'),
#                                             required=True, help_text='Convert from',
#                                             label='Convert from')
#     input_value = forms.FloatField(label='Amount', required=True)
#     output_currency = forms.ModelChoiceField(queryset=CountryCodes.objects.all().order_by('currency'),
#                                              required=True, help_text='Convert to',
#                                              label='Convert to')
#
#     class Meta:
#         model = CurrencyConvert
#         fields = ['input_currency', 'input_value', 'output_currency', 'output_value']
#
#     def save(self, commit=True):
#         conv = super(ConvertForm, self).save(commit=False)
#         conv.input_currency = self.cleaned_data["input_currency"].code
#         conv.output_currency = self.cleaned_data["output_currency"].code
#         logging.info('forms: conv obj type: {}'.format(type(conv)))
#         # conv.convert
#
#         if commit:
#             conv.save()
#
#         return conv

#
#     def save(self, commit=True):
#         conv = super(ConvertForm, self).save(commit=False)
#         conv.
#




