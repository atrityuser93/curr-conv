from django.urls import path

from . import views


urlpatterns = [path('convert/', views.home, name='convert-home'),
               path('convert/show/', views.ConvertCallsView.as_view(), name='convert-list'),
               path('convert/delete/', views.delete_convert_history, name='delete-conversions'),
               path('symbols/fetch/', views.fetch_currency_symbols, name='fetch-symbols'),
               path('symbols/delete/', views.delete_currency_symbols, name='delete-symbols'),
               path('symbols/show/', views.AvailableCurrencyListView.as_view(), name='symbol-list'),
               path('symbols/search/', views.SearchCountryCodesView.as_view(), name='codes-search'),
               path('rates/delete/', views.delete_exchange_rates, name='delete-rates'),
               path('rates/show/', views.AvailableExchangeRatesView.as_view(), name='rates-list'),
               path('rates/search/', views.SearchExchangeRatesView.as_view(), name='rates-search'),
               ]
