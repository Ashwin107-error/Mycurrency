Clone the repository
git clone https://github.com/yourusername/mycurrency.git --branch=development
cd mycurrency

Install Dependencies
pip install -r requirements.txt

Change Configurations
replace appropriate values for postgres and redis connection

Create a .env file in the root directory and add your environment variables:
CURRENCYBEACON_API_KEY=your_api_key_here
SUPPORTED_CURRENCIES = {'EUR', 'CHF', 'USD', 'GBP'}

Run Migrations
python manage.py makemigrations
python manage.py migrate

Create Superuser for django admin
python manage.py createsuperuser

Start Django Server
python manage.py runserver

API ENDPOINTS
GET /api/exchange-rate/?source=USD&target=INR&date=2024-10-27:---> Fetch the exchange rate between two currencies for a given date.
GET api/v1/currency-rates/?source=USD&date_from=2024-01-12&date_to=2024-02-28&symbols=INR,GBP:----> Wil return list of exchange rates for sepcific date range
GET /currencies/:---> List all available currencies.
POST /currencies/:---> Add a new currency.
PUT /currencies/<id>/:----> Update an existing currency.
DELETE /currencies/<id>/:---> Delete a currency

Historical Data Storing (Asynchronously)
using go    go run Historical_rates.go  ------> This command will start hiting the historical endpoint and loading them into the db concurrently

adding cronjob with python script
crontab -e
/pathtoyour/pythoninterpreter/python3 /pathtoscript/mycurrency/historical_rates.py


Back Office site
http://localhost:8000/admin/exchange/currency/convert/ ------>make sure you hit exchange-rate first to populate currency list in conversion

Go to admin panel 'Currency providers' change the priority to test which provider gets pereference


Suggestions and Discussions

-The Golang approach
I have used used .go to hava better performance in terms of asynchronously retrieving and loading historical data to our db as i assumed it was an assesment to get what would be the best result wrt to concurrency.

-Python approach
Couldve used asyncio and asyncpg2 to independently hit apis and load my db to have faster executions.

Collectively I can change both these scripts to run in infinite loops but since that doesnt seem very ideal, i have kept the max hits per execution as 30.

Insetad of cronjobs celery beat couldve been a better alternative for perdiodic tasks which i am already working on.

-Project Structure
This couldve been a more organised project structure as there might be more asynchronous tasks in future and maintaining a separate folder for the same wouldve been better like services as has been isolated 

-Backoffice admin panel
I tried to get the backoffice admin panale link to be traced right from the admin panel but couldnt do so though directly hitting the mentioned url will take you there.