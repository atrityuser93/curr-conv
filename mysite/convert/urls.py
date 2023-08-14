from django.urls import path

from . import views


urlpatterns = [path('fetch-symbols/', views.fetch_currency_symbols, name='fetch-symbols'),
               ]
