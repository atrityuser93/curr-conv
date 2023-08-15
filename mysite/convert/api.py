from ninja import Router
from .models import CountryCodes

router = Router()


@router.get('/symbols/show')
def currency_symbols_list(request):
    """provide list of all available currency symbols in json"""
    symbols = [{'currency': i_obj.currency, 'code': i_obj.currency}
               for i_obj in CountryCodes.objects.all()]
    return symbols


@router.get('/symbols/{currency_code}')
def currency_name(request, currency_code: str):
    """provide currency name for a given currency code"""
    obj = CountryCodes.objects.get(code=currency_code)
    return {'name': obj.currency}