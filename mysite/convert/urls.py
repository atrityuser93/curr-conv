from django.urls import path

from . import views


urlpatterns = [path('', views.home, name='convert-home'),
               path('symbols/fetch/', views.fetch_currency_symbols, name='fetch-symbols'),
               path('symbols/delete/', views.delete_currency_symbols, name='delete-symbols'),
               path('symbols/show/', views.AvailableCurrencyListView.as_view(), name='symbol-list'),
               path('rates/delete/', views.delete_exchange_rates, name='delete-rates'),
               path('rates/show/', views.AvailableExchangeRatesView.as_view(), name='rates-list'),
               path('show/', views.ConvertCallsView.as_view(), name='convert-list'),
               path('rates/search/', views.SearchExchangeRatesView.as_view(), name='rates-search'),
               ]
