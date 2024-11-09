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
        
def get_currency_rate_list_service(source_currency, date_from, date_to,symbols):
    providers = CurrencyProvider.objects.order_by('priority')
    for provider in providers:
        try:
            if provider.name == "CurrencyBeacon":
                    adapter = CurrencyBeaconAdapter()
            elif provider.name == "Mockprovider":
                    adapter = MockAdapter()
            else:
                raise ValueError("Unsupported provider")
            
            rates_data = adapter.get_currency_rate_list(
                source_currency=source_currency,
                date_from=date_from,
                date_to=date_to,
                symbols=symbols
            )
            response_data = [
                {
                    "date": date,
                    "target_currency": target_currency,
                    "rate": rate
                }
                for date, target_rates in rates_data.items()
                for target_currency, rate in target_rates.items()
            ]

            return response_data

        except ValueError as e:
            raise ValueError(f"Error fetching rates: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error occurred: {e}")



