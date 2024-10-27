from .adapters import CurrencyBeaconAdapter, CurrencyProvider,MockAdapter
from .models import CurrencyExchangeRate, Currency,CurrencyProvider

def fetch_exchange_rate(provider_name, source_currency, target_currency, date):
    providers = CurrencyProvider.objects.order_by('priority')
    for provider in providers:
        try:
            if provider.name == "CurrencyBeacon":
                adapter = CurrencyBeaconAdapter()
            elif provider.name == "Mockprovider":
                adapter = MockAdapter()
            else:
                raise ValueError("Unsupported provider")

            rate = adapter.get_exchange_rate(source_currency, target_currency, date)
            
            # Store the result in the database (simplified)

            source,_ = Currency.objects.get_or_create(code=source_currency)
            target,_ = Currency.objects.get_or_create(code=target_currency)
            exchange_rate, created = CurrencyExchangeRate.objects.update_or_create(
                source_currency=source,
                target_currency=target,
                date=date,
                defaults={'rate': rate, 'fallback_details': {"provider": provider_name}}
            )
            return exchange_rate
        except Exception as e:
            return None
        


