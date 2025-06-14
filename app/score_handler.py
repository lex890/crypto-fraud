import csv
import random
import requests
import pandas as pd
from datetime import datetime
import time
import configparser
import os

score_header = [
    "Trading Volume Consistency",
    "Liquidity & Order Book Depth",
    "Token Age & Market History",
    "Developer & Team Transparency",
    "Smart Contract Audit & Security",
    "Exchange Listings & Reputation",
    "Community & Social Media Presence",
    "Transaction Patterns & Anomalies",
    "Whitepaper & Roadmap Execution",
    "Regulatory Compliance & Legal Standing"
]

GITHUB_TOKEN = None
BITQUERY_API_KEY = 'ory_at_VHgEV5HL8Q310nA0oyK3Biwcy-44I1e7N4Tg2uXxYg0.tmtNPoS41mkqEhJ0k-kw6nDoiG34iex34ROwJk-_02c' 

def score_trading_volume_consistency(volume_24h, market_cap):
    if not market_cap:
        return 1
    ratio = float(str(volume_24h).replace(',', '')) / float(str(market_cap).replace(',', ''))
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
    market_cap = float(str(market_cap).replace(',', ''))
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

def evaluate_cryptos(cryptos, currency_choice):
    results = []
    for coin in cryptos:
        
        rank_number = coin.get('#')
        crypto_name = coin.get('Name') 
        print('retrieved: ', crypto_name)
        current_price = coin.get(f'Current Price ('+currency_choice+')')
        volume_1h = coin.get('1h%')
        volume_24h = coin.get('24h%')
        volume_7d = coin.get('7d%')
        market_cap = coin.get(f'Market Cap ('+currency_choice+')')
        logo_link = coin.get('Logo')
        symbol = coin.get('Symbol')
        description = coin.get('Description')
        creation_date = coin.get('Creation Date')
        website = coin.get('Website')
        source_code = coin.get('Source Code')

        score_volume = 10 if crypto_name == 'Bitcoin' else score_trading_volume_consistency(volume_24h, market_cap)
        score_liquidity = 10 if crypto_name == 'Bitcoin' else score_market_cap_liquidity(market_cap)
        score_age = 10 if crypto_name == 'Bitcoin' else score_token_age(creation_date)
        score_dev = 10 if crypto_name == 'Bitcoin' else score_developer_transparency(symbol)
        score_audit = 10 if crypto_name == 'Bitcoin' else score_contract_audit(symbol)
        score_exchange = 10 if crypto_name == 'Bitcoin' else score_exchange_listings(symbol)
        score_social = 10 if crypto_name == 'Bitcoin' else score_social_media_presence(symbol)
        score_txn = 10 if crypto_name == 'Bitcoin' else score_transaction_patterns(symbol)
        score_whitepaper = 10 if crypto_name == 'Bitcoin' else score_whitepaper_roadmap(symbol)
        score_regulation = 10 if crypto_name == 'Bitcoin' else score_regulatory_compliance(symbol)

        scores = {
            # Table Information
            '#': rank_number,
            'Name': crypto_name,
            'Current Price ('+currency_choice+')': current_price,
            '1h%': volume_1h,
            '24h%': volume_24h,
            '7d%': volume_7d,
            'Market Cap ('+currency_choice+')': market_cap,
            # Risk Assessment
            'Logo': logo_link,
            'Symbol': symbol,
            'Description': description,
            'Creation Date': creation_date,
            'Website': website,
            'Source Code': source_code,
            # Scoring
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