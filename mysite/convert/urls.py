from django.urls import path

from . import views


urlpatterns = [path('', views.home, name='convert-home'),
               path('symbols/fetch/', views.fetch_currency_symbols, name='fetch-symbols'),
               path('symbols/delete/', views.delete_currency_symbols, name='delete-symbols'),
               path('symbols/show/', views.AvailableCurrencyListView.as_view(), name='symbol-list'),
               ]
