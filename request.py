from datetime import datetime, timedelta
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import requests
import json
import time
import FreeSimpleGUI as sg
import table as tbl

cmc_listing_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
cmc_info_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'

def api_request(api_key, api_choice):
    currency = 'USD' # get_currency(api_choice)

    if api_choice == '1':
        parameters = {
            'start':'1',
            'limit':'50',
            'convert': currency
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
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
                    '#': ranking,
                    'Name': name,
                    'Current Price ('+currency+')': f"{price:,.2f}",
                    '1h%': f"{volume_1h:,.2f}",
                    '24h%': f"{volume_24h:,.2f}",
                    '7d%': f"{volume_7d:,.2f}",
                    'Market Cap ('+currency+')': f"{float(market_cap):,.2f}",

                    # Risk Assessment
                    'Logo': logo,
                    'Symbol': symbol,
                    'Description': description,
                    'Creation Date': date_added,
                    'Website': website,
                    'Source Code': source_code
                })
            # Save to CSV
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'./cryptodata/crypto_extended_{timestamp}.csv'
            headings, data = tbl.read_csv(tbl.export_to_csv(output, filename))
            return headings, data, filename

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            return sg.popup(f"Request failed: {e}")
        except KeyError as ke:
            return sg.popup(f"Response missing key: {ke}")

def get_currency(apichoice):
    valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'PHP']
    
    #return currency

def is_valid_cmc_api_key(api_key): # check coin market api key validity
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }

    response = requests.get(url, headers=headers)
    
    # If status_code is 200, the key is likely valid
    if response.status_code == 200:
        return True
    else:
        return False
    
def is_valid_cg_api_key(api_key):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return True
    else:
        return False