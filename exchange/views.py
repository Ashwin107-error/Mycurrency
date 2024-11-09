from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import CurrencySerializer
from .models import Currency
from rest_framework import status
import requests
from rest_framework.exceptions import ValidationError
from .services import fetch_exchange_rate,get_currency_rate_list_service
from django.conf import settings


SUPPORTED_CURRENCIES = {'EUR', 'CHF', 'USD', 'GBP'}
def validate_currency_code(currency_code):
    if currency_code not in settings.SUPPORTED_CURRENCIES:
        raise ValidationError(f"Only the following currencies are supported for source,target and symbols: {(settings.SUPPORTED_CURRENCIES)}")
    
class ExchangeRateView(APIView):
    def get(self, request):
        provider_name = request.query_params.get('provider')
        source_currency = request.query_params.get('source')
        target_currency = request.query_params.get('target')
        date = request.query_params.get('date')
        
        validate_currency_code(source_currency)       #--------->to validate supported currencies
        validate_currency_code(target_currency)

        try:
            exchange_rate = fetch_exchange_rate(provider_name, source_currency, target_currency, date)
            return Response({'rate': exchange_rate.rate}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CurrencyRateListView(APIView):
    def get(self, request):
        source_currency = request.query_params.get('source')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        symbols = request.query_params.get('symbols')

        validate_currency_code(source_currency)
        validate_currency_code(symbols)
        
        try:
            rates_data = get_currency_rate_list_service(
                source_currency=source_currency,
                date_from=date_from,
                date_to=date_to,
                symbols=symbols
            )

            return Response(rates_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ConvertAmountView(APIView):
    def __init__(self):
        self.api_key = settings.CURRENCYBEACON_API_KEY

    def get(self, request):
        source_currency = request.query_params.get('source')
        target_currency = request.query_params.get('target')
        amount = request.query_params.get('amount')

        validate_currency_code(source_currency)
        validate_currency_code(target_currency)

        params = {
            'from': source_currency,
            'to': target_currency,
            'amount': amount,
            'api_key': settings.CURRENCYBEACON_API_KEY
        }

        try:
            response = requests.get('https://api.currencybeacon.com/v1/convert', params=params)
            response_data = response.json()

            if response.status_code != 200 or 'error' in response_data:
                return Response(
                    {'error': 'Currency conversion failed', 'details': response_data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            converted_amount = response_data.get('response', {}).get('value')

            return Response({
                'source_currency': source_currency,
                'target_currency': target_currency,
                'original_amount': float(amount),
                'converted_amount': round(float(converted_amount), 2)  #to round off the value
            })

        except requests.RequestException as e:
            return Response({'error': 'Failed to connect to currency provider'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

