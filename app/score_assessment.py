from datetime import datetime

def calculate_initial_scores(coin_data):
    scores = {}
    
    # Trading Volume Consistency (based on 24h% change)
    try:
        volume_24h = float(coin_data['24h%'].replace(',', ''))
        if abs(volume_24h) < 5:
            scores['Trading Volume Consistency'] = '8'  # Stable
        elif abs(volume_24h) < 10:
            scores['Trading Volume Consistency'] = '6'  # Moderate
        else:
            scores['Trading Volume Consistency'] = '4'  # Volatile
    except:
        scores['Trading Volume Consistency'] = '5'  # Unknown

    # Token Age & Market History
    try:
        creation_date = datetime.strptime(coin_data['Creation Date'], '%Y-%m-%d')
        age_years = (datetime.now() - creation_date).days / 365
        if age_years > 3:
            scores['Token Age & Market History'] = '9'  # Very established
        elif age_years > 1:
            scores['Token Age & Market History'] = '7'  # Established
        else:
            scores['Token Age & Market History'] = '4'  # New
    except:
        scores['Token Age & Market History'] = '5'  # Unknown

    # Developer & Team Transparency
    if coin_data['Source Code'] != 'N/A':
        scores['Developer & Team Transparency'] = '8'  # Open source
    else:
        scores['Developer & Team Transparency'] = '3'  # Closed source

    # Exchange Listings & Reputation
    try:
        market_cap = float(coin_data['Market Cap (USD)'].replace(',', ''))
        if market_cap > 10000000000:  # > 10B
            scores['Exchange Listings & Reputation'] = '9'
        elif market_cap > 1000000000:  # > 1B
            scores['Exchange Listings & Reputation'] = '7'
        else:
            scores['Exchange Listings & Reputation'] = '5'
    except:
        scores['Exchange Listings & Reputation'] = '5'

    # Set default values for other metrics
    default_scores = {
        'Liquidity & Order Book Depth': '5',
        'Smart Contract Audit & Security': '5',
        'Community & Social Media Presence': '5',
        'Transaction Patterns & Anomalies': '5',
        'Whitepaper & Roadmap Execution': '5',
        'Regulatory Compliance & Legal Standing': '5'
    }
    scores.update(default_scores)
    
    return scores

def get_risk_level(score):
    """Convert numerical score to risk level description"""
    score = int(score)
    if score >= 7:
        return "Low Risk"
    elif score >= 4:
        return "Medium Risk"
    else:
        return "High Risk"

def calculate_overall_risk(scores):
    """Calculate overall risk score from individual metrics"""
    try:
        total = sum(int(score) for score in scores.values())
        return str(round(total / len(scores)))
    except:
        return '5'  # Default if calculation fails 