import requests
import traceback
import random
import curlify
from abc import ABC, abstractmethod
from django.conf import settings
from datetime import datetime,timedelta

class CurrencyProvider(ABC):
    @abstractmethod
    def get_exchange_rate(self, source_currency, target_currency, date):   #to fetch exchange rates between two currencies for a given date
        pass

    @abstractmethod
    def get_currency_rate_list(self, source_currency, date_from, date_to):  #to fetch a list of currency rates over a date range
        """Fetches a list of currency rates over a date range."""
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

    def get_currency_rate_list(self, source_currency, date_from, date_to,symbols):
        url = "https://api.currencybeacon.com/v1/timeseries"
        params = {
            "api_key": self.api_key,
            "base": source_currency,
            "start_date": date_from,
            "end_date": date_to,
            "symbols":symbols
        }
        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code == 200:
            return data['response']
        else:
            raise ValueError("Failed to fetch time series rates from CurrencyBeacon")
        
class MockAdapter(CurrencyProvider):
    def get_exchange_rate(self, source_currency, target_currency, date,):
        rate = round(random.uniform(0.5, 1.5), 6)  # Random rate between 0.5 and 1.5
        print(f"Mock rate for {source_currency} to {target_currency} on {date}: {rate}")
        return rate       

    def get_currency_rate_list(self, source_currency, date_from, date_to, symbols):
        current_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        mock_rates = {}

        # Split symbols if it's a string, allowing single or multiple currency codes
        target_currencies = symbols.split(',') if isinstance(symbols, str) else symbols

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Generate mock rates for each target currency
            daily_rates = {
                target_currency: round(random.uniform(0.8, 1.2), 6)
                for target_currency in target_currencies
                if target_currency != source_currency
            }
            
            # Add the daily rates to the mock_rates dictionary
            mock_rates[date_str] = daily_rates
            current_date += timedelta(days=1)
        
        return mock_rates

