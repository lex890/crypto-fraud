from datetime import datetime, timedelta
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import requests
import time
import FreeSimpleGUI as sg
from . import csv_handler as tbl
import json
import csv

cmc_listing_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
cmc_info_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'

def api_request(api_key, api_choice, currency_choice):
    
    if api_choice == '1':
        currency = currency_choice  # combo box input
        parameters = {
            'start':'1',
            'limit':'14',
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

                if 'data' not in info_data:
                    print(f"❌ No 'data' in response for coin ID {coin_id}")
                    print("🔎 Full response:", info_data)
                    continue  # Skip this coin

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
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            filename = f'./data/CMC_crypto_extended_{timestamp}.csv'
            headings, data = tbl.read_csv(tbl.export_to_csv(output, filename))
            print(type(data))

            return headings, data, filename

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print('nuh uh')
            return sg.popup(f"Request failed: {e}")
        except KeyError as ke:
            print(f'KeyError: {ke}')
            import traceback
            traceback.print_exc()
            return sg.popup(f"Response missing key: {ke}")

    elif api_choice == '2':
        apicheck = f'https://pro-api.coingecko.com/api/v3/ping?x_cg_pro_api_key={api_key}'
        requests.get(apicheck)  # just ping

        vs_currency = currency_choice.lower()
        cg_market_url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': vs_currency,
            'order': 'market_cap_desc',
            'per_page': 14,
            'page': 1,
            'sparkline': 'false',
            'price_change_percentage': '24h,7d'
        }

        market_data = requests.get(cg_market_url, params=params).json()
        output = []

        for idx, coin in enumerate(market_data, start=1):
            coin_id = coin['id']
            name = coin['name']
            symbol = coin['symbol']
            price = coin['current_price']
            market_cap = coin.get('market_cap', 'N/A')
            volume_24h = coin.get('price_change_percentage_24h_in_currency', 'N/A')
            volume_7d = coin.get('price_change_percentage_7d_in_currency', 'N/A')
            logo = coin.get('image', 'N/A')

            # Detailed metadata
            cg_coin_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            cg_coin_info = requests.get(cg_coin_url).json()

            description = cg_coin_info.get('description', {}).get('en', '').split('.')[0] if cg_coin_info.get('description', {}).get('en') else 'N/A'

            # Safe access for website
            homepage_links = cg_coin_info.get('links', {}).get('homepage', [])
            website = homepage_links[0] if homepage_links else 'N/A'

            # Safe access for GitHub source code
            github_links = cg_coin_info.get('links', {}).get('repos_url', {}).get('github', [])
            source_code = github_links[0] if github_links else 'N/A'

            creation_date = cg_coin_info.get('genesis_date', 'N/A')

            # CoinGecko doesn't provide 1h%, so we use 'N/A'
            output.append({
                '#': idx,
                'Name': name,
                'Current Price ('+vs_currency+')': f"{price:,.2f}",
                '1h%': 'N/A',
                '24h%': f"{volume_24h:,.2f}" if isinstance(volume_24h, (float, int)) else 'N/A',
                '7d%': f"{volume_7d:,.2f}" if isinstance(volume_7d, (float, int)) else 'N/A',
                'Market Cap ('+vs_currency+')': f"{float(market_cap):,.2f}" if isinstance(market_cap, (float, int)) else 'N/A',

                'Logo': logo,
                'Symbol': symbol.upper(),
                'Description': description,
                'Creation Date': creation_date,
                'Website': website,
                'Source Code': source_code
            })

            time.sleep(1)  # avoid rate limiting

        # Save to CSV
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'./data/CG_crypto_extended_cg_{timestamp}.csv'
        headings, data = tbl.read_csv(tbl.export_to_csv(output, filename))
        print(headings, data, filename)
        return headings, data, filename


def is_valid_cmc_api_key(api_key):
    url = cmc_listing_url
    try:
        headers = {'X-CMC_PRO_API_KEY': api_key}
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except Exception:
        return False
    
def is_valid_cg_api_key(api_key):
    url = 'https://api.coingecko.com/api/v3/pro'
    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception:
        return False
    
def cg_get_historical_price(coin_id, date_str, currency):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={date_str}"
    try:
        response = requests.get(url)
        data = response.json()
        return data['market_data']['current_price'].get(currency, 'N/A')
    except Exception:
        return 'N/A'
    
def get_api_choice(imagepath):
    api_choice = 'CoinMarketCap' if imagepath == './images/resizedCMC.png' else 'CoinGecko'
    return api_choice 

def get_cfg_key(imagepath):
    cfg_key = 'CMCKEY' if imagepath == './images/resizedCMC.png' else 'CGKEY'
    return cfg_key 

def fetch_next_cryptocurrencies(offset, api_key, api_choice, currency_choice):
    """Fetch the next set of cryptocurrencies starting from the given offset"""
    try:
        if api_choice == '1':  # CoinMarketCap
            return fetch_cmc_next_cryptocurrencies(api_key, offset, currency_choice)
        else:  # CoinGecko
            return fetch_cg_next_cryptocurrencies(offset, currency_choice)
    except Exception as e:
        print(f"Error fetching next cryptocurrencies: {str(e)}")
        return []

def fetch_cmc_next_cryptocurrencies(api_key, offset, currency_choice):
    """Fetch next cryptocurrencies from CoinMarketCap"""
    parameters = {
        'start': str(offset + 1),
        'limit': '14',
        'convert': currency_choice
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

        for coin in cmc_coins:
            ranking = coin['cmc_rank']
            name = coin['name']
            symbol = coin['symbol']
            price = coin['quote'][currency_choice]['price']
            volume_1h = coin['quote'][currency_choice]['percent_change_1h']
            volume_24h = coin['quote'][currency_choice]['percent_change_24h']
            volume_7d = coin['quote'][currency_choice]['percent_change_7d']
            market_cap = coin['quote'][currency_choice]['market_cap']

            # Metadata
            coin_id = coin['id']
            info_response = session.get(cmc_info_url, params={'id': coin_id})
            info_data = info_response.json()

            if 'data' not in info_data:
                print(f"❌ No 'data' in response for coin ID {coin_id}")
                continue

            coin_info = info_data['data'].get(str(coin_id), {})

            date_added = coin_info.get('date_added', 'N/A')
            if date_added != 'N/A':
                try:
                    date_added = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
                except ValueError:
                    date_added = 'N/A'
            description = coin_info.get('description', 'N/A')
            logo = coin_info.get('logo','N/A')
            website_list = coin_info.get('urls', {}).get('website', [])
            website = website_list[0] if website_list else 'N/A'
            source_code_list = coin_info.get('urls', {}).get('source_code', [])
            source_code = source_code_list[0] if source_code_list else 'N/A'
            time.sleep(1)  # Avoid rate limits

            output.append([
                ranking,
                name,
                f"{price:,.2f}",
                f"{volume_1h:,.2f}",
                f"{volume_24h:,.2f}",
                f"{volume_7d:,.2f}",
                f"{float(market_cap):,.2f}",
                logo,
                symbol,
                description,
                date_added,
                website,
                source_code
            ])

            
        print('next 14: ', type(output))
        
        return output

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(f"Request failed: {e}")
        return []
    except KeyError as ke:
        print(f'KeyError: {ke}')
        return []

def fetch_cg_next_cryptocurrencies(offset, currency_choice):
    """Fetch next cryptocurrencies from CoinGecko"""
    cg_market_url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': currency_choice.lower(),
        'order': 'market_cap_desc',
        'per_page': 14,
        'page': (offset // 14) + 1,
        'sparkline': 'false',
        'price_change_percentage': '24h,7d'
    }

    try:
        market_data = requests.get(cg_market_url, params=params).json()
        output = []

        for idx, coin in enumerate(market_data, start=offset + 1):
            coin_id = coin['id']
            name = coin['name']
            symbol = coin['symbol']
            price = coin['current_price']
            market_cap = coin.get('market_cap', 'N/A')
            volume_24h = coin.get('price_change_percentage_24h_in_currency', 'N/A')
            volume_7d = coin.get('price_change_percentage_7d_in_currency', 'N/A')
            logo = coin.get('image', 'N/A')

            # Detailed metadata
            cg_coin_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            cg_coin_info = requests.get(cg_coin_url).json()

            description = cg_coin_info.get('description', {}).get('en', '').split('.')[0] if cg_coin_info.get('description', {}).get('en') else 'N/A'
            homepage_links = cg_coin_info.get('links', {}).get('homepage', [])
            website = homepage_links[0] if homepage_links else 'N/A'
            github_links = cg_coin_info.get('links', {}).get('repos_url', {}).get('github', [])
            source_code = github_links[0] if github_links else 'N/A'
            creation_date = cg_coin_info.get('genesis_date', 'N/A')

            output.append({
                '#': idx,
                'Name': name,
                f'Current Price ({currency_choice})': f"{price:,.2f}",
                '1h%': 'N/A',
                '24h%': f"{volume_24h:,.2f}" if isinstance(volume_24h, (float, int)) else 'N/A',
                '7d%': f"{volume_7d:,.2f}" if isinstance(volume_7d, (float, int)) else 'N/A',
                f'Market Cap ({currency_choice})': f"{float(market_cap):,.2f}" if isinstance(market_cap, (float, int)) else 'N/A',
                'Logo': logo,
                'Symbol': symbol.upper(),
                'Description': description,
                'Creation Date': creation_date,
                'Website': website,
                'Source Code': source_code
            })

            time.sleep(1)  # avoid rate limiting

        return output

    except Exception as e:
        print(f"Error fetching CoinGecko data: {str(e)}")
        return []