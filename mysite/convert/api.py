from ninja import Router, Schema
from .models import CountryCodes

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


@router.post('/convert')
def convert_currency(request, data: ConvertSchema):
    """convert given input currency to output currency value"""
    return {'input': data.input_currency, 'value': data.value,
            'output': data.output_currency}
