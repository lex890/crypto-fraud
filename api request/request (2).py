import csv
from datetime import datetime, timedelta
import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time

cmc_listing_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
cmc_info_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
apisavailable = ['1','2']
apichoice = input('Choose an API to use: 1 for CoinMarketCap and 2 for CoinGecko:')
while apichoice not in apisavailable:
    print(f"Choose an API to use: {', '.join(apisavailable)}")
    apichoice = input("Enter a valid api: ").upper()
def get_currency():
    valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'PHP']
    if apichoice== '1':
        currency = input(f"Please select the currency for price display ({', '.join(valid_currencies)}): ").upper()
        while currency not in valid_currencies:
            print(f"Invalid currency. Please select from: {', '.join(valid_currencies)}")
            currency = input("Enter a valid currency: ").upper()
    elif apichoice== '2':
        currency = input(f"Please select the currency for price display ({', '.join(valid_currencies)}): ").upper()
        while currency not in valid_currencies:
            print(f"Invalid currency. Please select from: {', '.join(valid_currencies)}")
            currency = input("Enter a valid currency: ").upper()        
    return currency
def get_apikey():
    if apichoice =='1':
        apikey = input('Please enter your API KEY obtained from coinmarketcap website:')
    elif apichoice =='2':
        apikey = input('Please enter your API KEY obtained from coingecko website:')
    return apikey
def cg_get_historical_price(coin_id, date_str, currency):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={date_str}"
    try:
        response = requests.get(url)
        data = response.json()
        return data['market_data']['current_price'].get(currency, 'N/A')
    except Exception:
        return 'N/A'

apikey = get_apikey()
currency = get_currency()
if apichoice== '2':
    x_cg_pro_api_key = apikey
    apicheck = f'https://pro-api.coingecko.com/api/v3/ping?x_cg_pro_api_key={x_cg_pro_api_key}'
    auth = requests.get(apicheck).json()
    vs_currency = currency.lower()
    historical_date = (datetime.now() - timedelta(days=30)).strftime('%d-%m-%Y')
    cg_market_url = "https://api.coingecko.com/api/v3/coins/markets"
    limit = 5
    params = {
        'vs_currency': vs_currency,
        'order': 'market_cap_desc',
        'per_page': limit,
        'page': 1,
        'sparkline': 'false'
    }
    market_data = requests.get(cg_market_url, params=params).json()
    output = []
    for index, coin in enumerate(market_data, start=1):
        coin_id = coin['id']
        name = coin['name']
        symbol = coin['symbol']
        price = coin['current_price']
        volume = coin['total_volume']

        # Step 2: Get full metadata
        cg_coin_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        cg_coin_info = requests.get(cg_coin_url).json()

        description = cg_coin_info.get('description', {}).get('en', '').split('.')[0]
        website = cg_coin_info.get('links', {}).get('homepage', [''])[0] or 'N/A'
        source_code = cg_coin_info.get('links', {}).get('repos_url', {}).get('github', [''])[0] or 'N/A'
        creation_date = cg_coin_info.get('genesis_date', 'N/A')

        # Step 3: Historical price
        hist_price = cg_get_historical_price(coin_id, historical_date, vs_currency)
        time.sleep(1)  # prevent rate-limiting
        # coin gecko
        output.append({
            # Basic Information
            'Number': index, 
            'Name': name,
            'Symbol': symbol.upper(),
            'Creation Date': creation_date,

            # Pricing & Volume
            f'Current Price ({vs_currency.upper()})': f"{price:,.2f}",
            f'24h Volume ({vs_currency.upper()})': f"{volume:,.2f}",
            f'Price on {historical_date} ({vs_currency.upper()})': f"{hist_price:,.2f}" if isinstance(hist_price, (float, int)) else hist_price,
            '1h Volume': 'N/A',       # Placeholder
            '7d Volume': 'N/A',       # Placeholder
            'Market Cap': 'N/A',      # Placeholder

            # Metadata & Links
            'Logo': 'N/A',            # CoinGecko API requires separate call for image if needed
            'Ranking': 'N/A',         # Placeholder
            'Description': description,
            'Website': website,
            'Source Code': source_code
        })

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'coingecko_crypto_data_{timestamp}.csv'
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)

    print(f"✅ Data saved to {filename}")
elif apichoice=='1':        
    parameters = {
    'start':'1',
    'limit':'50',
    'convert': currency
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': apikey,
    }
    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(cmc_listing_url, params=parameters)
        cmc_listing_data = response.json()
        cmc_coins = cmc_listing_data.get('data', [])

        output = []
        historical_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        for coin in cmc_coins:
            ranking = coin['cmc_rank']
            name = coin['name']
            symbol = coin['symbol']
            price = coin['quote'][currency]['price']
            volume_1h = coin['quote'][currency]['percent_change_1h']
            volume_24h = coin['quote'][currency]['percent_change_24h']
            volume_7d = coin['quote'][currency]['percent_change_7d']
            market_cap = coin['quote'][currency]['market_cap']

            # Metadata
            coin_id = coin['id']
            info_response = session.get(cmc_info_url, params={'id': coin_id})
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
            # coin market cap
            output.append({
                # Table Information
                'Ranking': ranking,
                'Name': name,
                'Current Price ('+currency+')': f"{price:,.2f}",
                '1h Volume': f"{volume_1h:,.2f}",
                '24h Volume': f"{volume_24h:,.2f}",
                '7d Volume': f"{volume_7d:,.2f}",
                'Market Cap': f"{market_cap}",

                # Risk Assessment
                'Logo': logo,
                'Symbol': symbol,
                'Description': description,
                'Creation Date': date_added,
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