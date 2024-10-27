from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Currency, CurrencyExchangeRate
from .forms import CurrencyConversionForm
# Register your models here.

from .models import CurrencyProvider

@admin.register(CurrencyProvider)
class CurrencyProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')
    ordering = ('priority',)

@admin.register(CurrencyExchangeRate)
class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('source_currency', 'target_currency', 'rate', 'date')

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('convert/', self.admin_site.admin_view(self.convert_view), name='currency-convert'),
        ]
        return custom_urls + urls

    def convert_view(self, request):
        form = CurrencyConversionForm()
        converted_data = None

        if request.method == 'POST':
            form = CurrencyConversionForm(request.POST)
            if form.is_valid():
                source_currency = form.cleaned_data['source_currency']
                target_currencies = form.cleaned_data['target_currencies']
                amount = form.cleaned_data['amount']
                converted_data = self.perform_conversion(source_currency, target_currencies, amount)

        context = {
            'form': form,
            'converted_data': converted_data,
            'title': 'Currency Conversion',
        }
        return render(request, 'admin/currency_conversion.html', context)

    def perform_conversion(self, source_currency, target_currencies, amount):
        converted_data = {}
        for target_currency in target_currencies:
            try:
                # Get the exchange rate for the given date (e.g., today's date)
                exchange_rate = CurrencyExchangeRate.objects.get(
                    source_currency=source_currency,
                    target_currency=target_currency
                )
                converted_amount = amount * exchange_rate.rate
                converted_data[target_currency.code] = converted_amount
            except CurrencyExchangeRate.DoesNotExist:
                converted_data[target_currency.code] = "Rate not available"
        return converted_data