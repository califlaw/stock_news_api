import os
import requests
from pprint import pprint
import datetime
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

params_stock = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK_NAME,
    'apikey': os.environ.get('API_STOCKS')
}

response_stock = requests.get(STOCK_ENDPOINT, params=params_stock)
data = response_stock.json()['Time Series (Daily)']
data_list = [value for (key, value) in data.items()]

yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data['4. close']

before_yesterday_data = data_list[1]
before_yesterday_price = before_yesterday_data['4. close']

# Comparing the difference between yesterday's and today's price
difference = round(abs(float(before_yesterday_price) - float(yesterday_closing_price)), 2)
percentage = round(difference / float(before_yesterday_price) * 100, 3)

# Only if difference will be more than 1% then following code will be output.
if percentage > 1:
    params_news = {
        'apiKey': os.environ.get('API_NEWS'),
        'qInTitle': COMPANY_NAME,
    }
# Sending get request to news api. Taking only first three articles and then formatting it for more comprehensive sms.
    response_news = requests.get(NEWS_ENDPOINT, params=params_news)
    data = response_news.json()
    three_articles = data['articles'][:3]
    info_needed = [f"Headline: {x['title']}. \nBried: {x['description']}" for x in three_articles]

# Here I am connecting to Twilio API, that can sms/call etc via
    # virtual number to the real number(here is
    # I have my real number closed in .env I really was that project for some time.
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

# Looping through the info that i got from news api and sending it via Twilio to my phone number.
    for info in info_needed:
        message = client.messages \
            .create(
            body=info,
            from_=os.environ.get('TWILIO_NUMBER'),
            to=os.environ.get('PHONE_NUMBER'),
        )
