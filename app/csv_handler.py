import csv
from .score_assessment import calculate_initial_scores

filename = '../data/data_scores.csv'

def read_csv(filename):
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)

    if not data:
        return [], []

    headings = data[0]
    data = data[1:]
    return headings, data

def get_existing_scores():
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return {row['Symbol']: {
                'Trading Volume Consistency': row.get('Trading Volume Consistency', '5'),
                'Liquidity & Order Book Depth': row.get('Liquidity & Order Book Depth', '5'),
                'Token Age & Market History': row.get('Token Age & Market History', '5'),
                'Developer & Team Transparency': row.get('Developer & Team Transparency', '5'),
                'Smart Contract Audit & Security': row.get('Smart Contract Audit & Security', '5'),
                'Exchange Listings & Reputation': row.get('Exchange Listings & Reputation', '5'),
                'Community & Social Media Presence': row.get('Community & Social Media Presence', '5'),
                'Transaction Patterns & Anomalies': row.get('Transaction Patterns & Anomalies', '5'),
                'Whitepaper & Roadmap Execution': row.get('Whitepaper & Roadmap Execution', '5'),
                'Regulatory Compliance & Legal Standing': row.get('Regulatory Compliance & Legal Standing', '5')
            } for row in reader}
    except FileNotFoundError:
        return {}

def export_to_csv(output, filename):
    # Get existing scores
    existing_scores = get_existing_scores()
    
    # Add risk scores to each coin's data
    for coin_data in output:
        symbol = coin_data['Symbol']
        if symbol in existing_scores:
            # Add existing scores
            coin_data.update(existing_scores[symbol])
        else:
            # Calculate initial scores for new coins
            coin_data.update(calculate_initial_scores(coin_data))

    # Write to CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)

    print(f"✅ Data exported to {filename}")
    return filename

    