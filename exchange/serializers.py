from rest_framework import serializers
from .models import Currency, CurrencyExchangeRate

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol']

class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchangeRate
        fields = '__all__'

# class ConvertAmountSerializer(serializers.Serializer):
#     source_currency = serializers.CharField(max_length=3)
#     target_currency = serializers.CharField(max_length=3)
#     amount = serializers.DecimalField(max_digits=10, decimal_places=2)
