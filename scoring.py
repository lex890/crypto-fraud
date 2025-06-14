import requests
import pandas as pd
from datetime import datetime
import time
import configparser
import os

# Load API key from config file
def load_api_key(config_path='./keys/settings.cfg', key_name='cmckey'):
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path)
        return config.get('CoinMarketCap', key_name, fallback='')
    return ''

API_KEY = load_api_key()
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
}


# GitHub token if available (for better rate limits)
GITHUB_TOKEN = None  # Replace with your token or load from file/env

BITQUERY_API_KEY = 'ory_at_VHgEV5HL8Q310nA0oyK3Biwcy-44I1e7N4Tg2uXxYg0.tmtNPoS41mkqEhJ0k-kw6nDoiG34iex34ROwJk-_02c'

# Define scoring functions
def score_trading_volume_consistency(volume_24h, market_cap):
    if not market_cap:
        return 1
    ratio = volume_24h / market_cap
    if ratio >= 0.5:
        return 10
    elif ratio >= 0.25:
        return 8
    elif ratio >= 0.1:
        return 6
    elif ratio >= 0.05:
        return 4
    return 2

def score_market_cap_liquidity(market_cap):
    if market_cap >= 10_000_000_000:
        return 10
    elif market_cap >= 1_000_000_000:
        return 8
    elif market_cap >= 100_000_000:
        return 6
    elif market_cap >= 10_000_000:
        return 4
    return 2

def score_token_age(date_added):
    try:
        delta = (datetime.now() - datetime.strptime(date_added, '%Y-%m-%dT%H:%M:%S.%fZ')).days
    except:
        return 1
    if delta >= 1825:
        return 10
    elif delta >= 1095:
        return 8
    elif delta >= 365:
        return 6
    elif delta >= 180:
        return 4
    return 2    

def score_developer_transparency(symbol):
    try:
        response = requests.get(f'https://api.github.com/search/repositories?q={symbol}+in:name&sort=stars',
                                headers={'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {})
        data = response.json()
        items = data.get('items', [])
        if not items:
            return 3
        repo = items[0]
        commits_url = repo['commits_url'].split('{')[0]
        commits_resp = requests.get(commits_url)
        commit_count = len(commits_resp.json())
        if commit_count >= 1000:
            return 10
        elif commit_count >= 500:
            return 8
        elif commit_count >= 100:
            return 6
        return 4
    except:
        return 3

def score_contract_audit(symbol):
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{symbol.lower()}'
        response = requests.get(url)
        data = response.json()

        links = data.get('links', {})
        homepage = links.get('homepage', [''])[0]
        repos = links.get('repos_url', {}).get('github', [])

        platforms = data.get('platforms', {})
        contracts_present = bool(platforms)

        score = 2
        if contracts_present:
            score += 4
        if repos:
            score += 2
        if homepage:
            score += 2

        return min(score, 10)
    except:
        return 3

def score_exchange_listings(symbol):
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{symbol.lower()}'
        resp = requests.get(url)
        tickers = resp.json().get('tickers', [])
        count = len(tickers)
        if count >= 50:
            return 10
        elif count >= 20:
            return 8
        elif count >= 10:
            return 6
        return 4
    except:
        return 3

def score_social_media_presence(symbol):
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{symbol.lower()}'
        response = requests.get(url)
        data = response.json()
        community_data = data.get('community_data', {})
        followers = community_data.get('twitter_followers', 0)
        if followers >= 100000:
            return 10
        elif followers >= 50000:
            return 8
        elif followers >= 10000:
            return 6
        return 4
    except:
        return 3

def score_transaction_patterns(symbol):
    try:
        query = {
            "query": """
            query ($network: EthereumNetwork!, $symbol: String!) {
              ethereum(network: $network) {
                transfers(currency: {is: $symbol}) {
                  count
                }
              }
            }
            """,
            "variables": {"network": "ethereum", "symbol": symbol}
        }
        headers = {
            "X-API-KEY": BITQUERY_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post("https://graphql.bitquery.io/", json=query, headers=headers)
        count = response.json().get("data", {}).get("ethereum", {}).get("transfers", [{}])[0].get("count", 0)
        if count >= 100000:
            return 10
        elif count >= 10000:
            return 8
        elif count >= 1000:
            return 6
        return 4
    except:
        return 3

def score_whitepaper_roadmap(symbol):
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{symbol.lower()}'
        response = requests.get(url)
        data = response.json()
        description = data.get('description', {}).get('en', '')
        links = data.get('links', {})

        whitepaper = links.get('homepage', [''])[0]
        roadmap = links.get('repos_url', {}).get('github', [])

        score = 2
        if whitepaper:
            score += 3
        if roadmap:
            score += 3
        if len(description) > 300:
            score += 2

        return min(score, 10)
    except:
        return 3

def score_regulatory_compliance(symbol):
    try:
        url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
        response = requests.get(url, headers=headers, params={'symbol': symbol})
        data = response.json().get('data', {}).get(symbol, {})
        tags = data.get('tags', [])

        score = 2
        if 'stablecoin' in tags:
            score += 2
        if any(tag for tag in tags if 'compliant' in tag.lower() or 'regulat' in tag.lower()):
            score += 4
        if 'binance-smart-chain' in tags or 'ethereum' in tags:
            score += 2

        return min(score, 10)
    except:
        return 3

def fetch_crypto_data():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '14',
        'convert': 'USD'
    }
    response = requests.get(url, headers=headers, params=parameters)
    return response.json().get('data', [])

def evaluate_cryptos(cryptos):
    results = []
    for coin in cryptos:
        name = coin.get('name')
        symbol = coin.get('symbol')
        quote = coin.get('quote', {}).get('USD', {})
        market_cap = quote.get('market_cap', 0)
        volume_24h = quote.get('volume_24h', 0)
        date_added = coin.get('date_added', '')

        score_volume = score_trading_volume_consistency(volume_24h, market_cap)
        score_liquidity = score_market_cap_liquidity(market_cap)
        score_age = score_token_age(date_added)
        score_dev = score_developer_transparency(symbol)
        score_audit = score_contract_audit(symbol)
        score_exchange = score_exchange_listings(symbol)
        score_social = score_social_media_presence(symbol)
        score_txn = score_transaction_patterns(symbol)
        score_whitepaper = score_whitepaper_roadmap(symbol)
        score_regulation = score_regulatory_compliance(symbol)

        scores = {
            'Name': name,
            'Symbol': symbol,
            'Trading Volume Consistency': score_volume,
            'Liquidity and Order Book Depth': score_liquidity,
            'Token Age and Market History': score_age,
            'Developer and Team Transparency': score_dev,
            'Smart Contract Audit and Security Measures': score_audit,
            'Exchange Listings and Reputation': score_exchange,
            'Community and Social Media Presence': score_social,
            'Transaction Patterns and Anomalies': score_txn,
            'Whitepaper and Roadmap Assessment': score_whitepaper,
            'Regulatory Compliance and Legal Standing': score_regulation,
        }

        scores['Total Score'] = sum([v for k, v in scores.items() if isinstance(v, int)])
        results.append(scores)
        time.sleep(1)  # To prevent rate limit issues with public APIs
    return results

def save_scores_to_csv(results):
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"crypto_scores_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved results to {filename}")

# Main logic
if __name__ == '__main__':
    #raw data
    crypto_data = fetch_crypto_data()

    # data with socres
    scores = evaluate_cryptos(crypto_data)
    
    save_scores_to_csv(scores)

    print('fetch_crypto_data: ', crypto_data)
    print('evaluate_cryptos: ', scores)
