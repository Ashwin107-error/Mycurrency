import requests
import traceback
import random
from abc import ABC, abstractmethod
from django.conf import settings

class CurrencyProvider(ABC):
    @abstractmethod
    def get_exchange_rate(self, source_currency, target_currency, date):
        """Fetches exchange rates between two currencies for a given date."""
        pass

class CurrencyBeaconAdapter(CurrencyProvider):
    def __init__(self):
        self.api_key = settings.CURRENCYBEACON_API_KEY
        print(self.api_key)

    def get_exchange_rate(self, source_currency, target_currency, date):
        try:
            print(source_currency,target_currency,date)
            url ="https://api.currencybeacon.com/v1/historical"
            params = {
                "api_key": self.api_key,
                "date": date,
                "base": source_currency,
                "symbols": target_currency,
            }
            response = requests.get(url=url, params=params)
            data = response.json()
            if response.status_code == 200 and 'rates' in data.get('response',{}):
                return data['response']['rates'].get(target_currency)
            else:
                raise ValueError("Failed to fetch rates from CurrencyBeacon")
        except:
            traceback.print_exc() 

class MockAdapter(CurrencyProvider):
    def get_exchange_rate(self, source_currency, target_currency, date):
        """Simulate fetching exchange rates with random values."""
        rate = round(random.uniform(0.5, 1.5), 6)  # Random rate between 0.5 and 1.5
        print(f"Mock rate for {source_currency} to {target_currency} on {date}: {rate}")
        return rate           
