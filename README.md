Clone the repository
git clone https://github.com/yourusername/mycurrency.git
cd mycurrency

Install Dependencies
pip install -r requirements.txt

Create a .env file in the root directory and add your environment variables:
CURRENCYBEACON_API_KEY=your_api_key_here

Run Migrations
python manage.py migrate

Create Superuser for django admin
python manage.py createsuperuser

Start Django Server
python manage.py runserver

Start Celery Worker
celery -A mycurrency worker --loglevel=info

Start celery beat
celery -A mycurrency beat --loglevel=info

API ENDPOINTS
GET /api/exchange-rate/?source=USD&target=INR&date=2024-10-27: Fetch the exchange rate between two currencies for a given date.
GET /currencies/: List all available currencies.
POST /currencies/: Add a new currency.
PUT /currencies/<id>/: Update an existing currency.
DELETE /currencies/<id>/: Delete a currency

Back Office site
http://localhost:8000/admin/exchange/currency/convert/