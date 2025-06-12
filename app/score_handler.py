import csv
import random

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

def get_scores(filepath):
    with open(filepath, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    header = rows[0]

    # Check if the file already has score headers
    if header[-len(score_header):] == score_header:
        print("✅ Scores already exist. Only adding scores to new rows if needed.")
        has_scores = True
    else:
        header += score_header
        has_scores = False

    updated_rows = [header]

    for row in rows[1:]:
        if has_scores and len(row) == len(header):  # Already has scores
            updated_rows.append(row)
        else:
            random_scores = [str(random.randint(1, 10)) for _ in score_header]
            updated_rows.append(row + random_scores)

    with open(filepath, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(updated_rows)
  