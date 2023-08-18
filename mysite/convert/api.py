from ninja import Router, Schema, Form
from django.conf import settings

from .models import CountryCodes, CurrencyConvert


router = Router()


@router.get('/symbols/show')
def currency_symbols_list(request):
    """provide list of all available currency symbols in json"""
    symbols = {i_obj.currency: i_obj.code for i_obj in CountryCodes.objects.all()}
    result = {'success': True, 'symbols': symbols}
    return 200, result


@router.get('/symbols/{currency_code}')
def currency_name(request, currency_code: str):
    """provide currency name for a given currency code"""
    obj = CountryCodes.objects.get(code=currency_code)
    return 200, {'code': currency_code, 'name': obj.currency}


class ConvertSchema(Schema):
    input_currency: str = 'USD'
    input_value: float = 1.0
    output_currency: str = 'JPY'
    output_value: float = 0.0
    api_url: str = 'http://data.fixer.io/api/latest'
    api_key: str = settings.API_KEY


@router.post('/convert/raw')
def convert_currency_raw(request, data: ConvertSchema):
    """Convert given input currency to output currency value.
    Input data is provided as raw data (JSON form)"""
    # create converter class instance
    conv_obj = CurrencyConvert(input_value=data.input_value,
                               input_currency=str(data.input_currency),
                               output_currency=str(data.output_currency),
                               )
    # get currency conversion value
    conv_obj.convert(url=data.api_url,
                     api_key=data.api_key)

    return 200, {'input currency': conv_obj.input_currency,
                 'input value': conv_obj.input_value,
                 'output currency': conv_obj.output_currency,
                 'output value': conv_obj.output_value}


@router.post('/convert')
def convert_currency(request, payload: ConvertSchema = Form(...)):
    """Convert given input currency to output currency value.
            Input data is provided as form-encoded data"""
    kwargs = payload.dict()
    needed_keys = ['input_currency', 'input_value', 'output_currency']
    options = {key: value for key, value in kwargs.items()
               if key in needed_keys}
    conv_obj = CurrencyConvert.objects.create(**options)
    conv_obj.convert(kwargs['api_url'], kwargs['api_key'])
    return 200, {'success': conv_obj.is_converted(),
                 'value': conv_obj.output_value}



