from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ExchangeRateView,CurrencyViewSet,ConvertAmountView,CurrencyRateListView

router = DefaultRouter()
router.register('currencies', CurrencyViewSet)
urlpatterns = [
    path('exchange-rate/', ExchangeRateView.as_view(), name='exchange-rate'),
    path('convert-amount/', ConvertAmountView.as_view(), name='convert_amount'),
    path('currency-rates/', CurrencyRateListView.as_view(), name='currency-rate-list'),
    path('', include(router.urls))
]
