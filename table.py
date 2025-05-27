import csv

def read_csv(filename):
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)

    if not data:
        return [], []

    headings = data[0]
    data = data[1:]
    return headings, data


def export_to_csv(output, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)

    print(f"✅ Data exported to {filename}")
    return filename

    