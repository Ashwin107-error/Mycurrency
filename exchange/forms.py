# exchange/forms.py
from django import forms
from .models import Currency

class CurrencyConversionForm(forms.Form):
    source_currency = forms.ModelChoiceField(queryset=Currency.objects.all(), label="Source Currency")
    target_currencies = forms.ModelMultipleChoiceField(queryset=Currency.objects.all(), label="Target Currencies")
    amount = forms.DecimalField(max_digits=20, decimal_places=2, label="Amount")
