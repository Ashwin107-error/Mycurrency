from celery import shared_task
import requests
from datetime import datetime
from .models import Currency, CurrencyExchangeRate

@shared_task
def fetch_and_store_exchange_rates():
    # Specify your API key and URL
    try:
        API_KEY = 'z7vnFV1FLhChDhOuVeXg80AoQtNTWc6i'
        API_URL = 'https://api.currencybeacon.com/v1/historical'
        
        # Fetch all currencies from your database
        currencies = list(Currency.objects.values_list('code', flat=True))
        # currency_list = ','.join(currencies)
        # print(currency_list,"ZZZZZZZZZZZZ")

        # Prepare the API request parameters
        for base_currency in currencies:
            for target_currency in currencies:
                if base_currency==target_currency:
                    continue
        params = {
            'api_key': API_KEY,
            'symbols': target_currency,
            'base':base_currency,
            'date':datetime.today().strftime('%Y-%m-%d')
        }
        print(params,"PARAM")

        # Make a request to the third-party API
        response = requests.get(API_URL, params=params)
        data = response.json()
        print(data,"SDDDDDD")


        if response.status_code == 200 and 'rates' in data.get('response',{}):
            # rates = data['response'].get('rates',{})
            rate = data['response']['rates'].get(target_currency)
            print(rate,"TDDDDDDDDnnnDD")
            if rate:
                source_currency = Currency.objects.get(code=base_currency)
                target_currency_obj = Currency.objects.get(code=target_currency)
                print("yesssssssss")

                currency_exchange_rate,created = CurrencyExchangeRate.objects.update_or_create(
                        source_currency=source_currency,
                        target_currency=target_currency_obj,
                        date=data['response']['date'],
                        defaults={'rate': rate}
                    )
                if created:
                    print("A new CurrencyExchangeRate was created:", currency_exchange_rate)
                else:
                    print("An existing CurrencyExchangeRate was updated:", currency_exchange_rate)
                
                
    except Exception as e:
        print(e,"WWWWWWWWWWWW1111")
        return e
