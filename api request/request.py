import csv
from datetime import datetime, timedelta
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
listing_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
info_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'

def get_currency():
    valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'PHP']
    currency = input(f"Please select the currency for price display ({', '.join(valid_currencies)}): ").upper()
    while currency not in valid_currencies:
        print(f"Invalid currency. Please select from: {', '.join(valid_currencies)}")
        currency = input("Enter a valid currency: ").upper()
    return currency

def get_apikey():
    apikey = input('Please enter your API KEY obtained from coinmarketcap website:')
    return apikey

apikey = get_apikey()
currency = get_currency()

parameters = {
  'start':'1',
  'limit':'10',
  'convert': currency
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': apikey,
}

session = Session()
session.headers.update(headers)

try:
    response = session.get(listing_url, params=parameters)
    listing_data = response.json()
    coins = listing_data.get('data', [])

    output = []
    historical_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    for coin in coins:
        coin_id = coin['id']
        name = coin['name']
        symbol = coin['symbol']
        price = coin['quote'][currency]['price']
        volume = coin['quote'][currency]['volume_24h']

        # Metadata
        info_response = session.get(info_url, params={'id': coin_id})
        info_data = info_response.json()
        coin_info = info_data['data'].get(str(coin_id), {})

        date_added = coin_info.get('date_added', 'N/A')
        if date_added != 'N/A':
          try:
              # Convert to datetime object and then format it to just the date (YYYY-MM-DD)
              date_added = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
          except ValueError:
              date_added = 'N/A'  # If the date is in an unexpected format, fallback to 'N/A'
        description = coin_info.get('description', 'N/A')
        logo = coin_info.get('logo','N/A')
        website_list = coin_info.get('urls', {}).get('website', [])
        website = website_list[0] if website_list else 'N/A'
        source_code_list = coin_info.get('urls', {}).get('source_code', [])
        source_code = source_code_list[0] if source_code_list else 'N/A'
        time.sleep(1)  # Avoid rate limits

        output.append({
            'Logo': logo,
            'Name': name,
            'Symbol': symbol,
            'Creation Date': date_added,
            'Current Price ('+currency+')': f"{price:,.2f}",
            '24h Volume ('+currency+')': f"{volume:,.2f}",
            'Description': description,
            'Website': website,
            'Source Code': source_code
        })
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'crypto_extended_{timestamp}.csv'
    # Save to CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)

    print("✅ Data exported to crypto_extended.csv")

except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(f"Request failed: {e}")
except KeyError as ke:
    print(f"Response missing key: {ke}")