from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import CurrencySerializer
from .models import Currency
from rest_framework import status
import requests
from .services import fetch_exchange_rate
from django.conf import settings

class ExchangeRateView(APIView):
    def get(self, request):
        provider_name = request.query_params.get('provider')
        source_currency = request.query_params.get('source')
        target_currency = request.query_params.get('target')
        date = request.query_params.get('date')
        
        try:
            exchange_rate = fetch_exchange_rate(provider_name, source_currency, target_currency, date)
            return Response({'rate': exchange_rate.rate}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ConvertAmountView(APIView):
    def __init__(self):
        self.api_key = settings.CURRENCYBEACON_API_KEY

    def get(self, request):
        source_currency = request.query_params.get('source')
        target_currency = request.query_params.get('target')
        amount = request.query_params.get('amount')
        params = {
            'from': source_currency,
            'to': target_currency,
            'amount': amount,
            'api_key': settings.CURRENCYBEACON_API_KEY
        }

        try:
            #API call to Currency Beacon's convert amount endpoint
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

