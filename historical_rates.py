import requests
import json
import time
import psycopg2
from datetime import datetime, timedelta
import redis
from django.conf import settings

def init_db():
    conn = psycopg2.connect(
        dbname="ashwin",
        user="ashwin",
        password="routemobile",
        host="localhost"
    )
    conn.autocommit = True
    return conn

def init_redis():
    r = redis.Redis(host='localhost', port=6379, db=0)
    return r

def get_last_processed_date(redis_client):
    last_date = redis_client.get('last_processed_date')
    if last_date:
        return datetime.strptime(last_date.decode('utf-8'), '%Y-%m-%d')
    return datetime(1997, 10, 14)

def set_last_processed_date(redis_client, date):
    redis_client.set('last_processed_date', date.strftime('%Y-%m-%d'))

def fetch_historical_rates(date, base_currency):
    url = f"https://api.currencybeacon.com/v1/historical"
    params = {
        'api_key':'gWuM4ulV3MKDUEIfW4M3kqbHA5O5HBzg',
        'date': date.strftime('%Y-%m-%d'),
        'base': base_currency
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(data,"qssqsq")
    # Ensure data structure is correct and contains rates
    if response.status_code == 200 and 'rates' in data['response'] and data['response']['rates']:
        print(f"Fetched data for date {date}")
        return data
    else:
        print(f"No rates available for date {date}. Skipping.")
        return None

# Store data in the database
def store_in_database(conn, api_response):
    cur = conn.cursor()
    date = api_response['response']['date']
    base_currency = api_response['response']['base']
    rates = api_response['response']['rates']

    # Prepare and execute SQL insertion, handling duplicates
    for currency_code, rate in rates.items():
        try:
            cur.execute(
                """
                INSERT INTO currencyrate (date, base_currency, currency_code, rate)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (date, currency_code) DO NOTHING
                """,
                (date, base_currency, currency_code, rate)
            )
            print(f"Stored rate for date {date} and currency {currency_code}")
        except Exception as e:
            print(f"Failed to insert rate for {date} - {currency_code}: {e}")
    cur.close()

def main():
    conn = init_db()
    redis_client = init_redis()

    base_currency = "USD"
    current_date = get_last_processed_date(redis_client)

    successful_responses = 0
    max_responses = 30

    while successful_responses < max_responses:
        api_response = fetch_historical_rates(current_date, base_currency)
        
        if api_response:
            store_in_database(conn, api_response)
            set_last_processed_date(redis_client, datetime.strptime(api_response['response']['date'], '%Y-%m-%d'))
            successful_responses += 1
        current_date += timedelta(days=1)

    conn.close

if __name__ == "__main__":
    main()