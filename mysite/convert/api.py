from ninja import Router, Schema
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
    value: float = 1.0
    output_currency: str


@router.post('/convert/raw')
def convert_currency(request, data: ConvertSchema):
    """convert given input currency to output currency value"""
    # get currency conversion value
    conv_obj = CurrencyConvert(input_value=data.value,
                               input_currency=str(data.input_currency),
                               output_currency=str(data.output_currency),
                               )
    conv_obj.convert(url='http://data.fixer.io/api/latest',
                     api_key=settings.API_KEY)

    return {'input currency': conv_obj.input_currency,
            'input value': conv_obj.input_value,
            'output currency': conv_obj.output_currency,
            'output value': conv_obj.output_value}
