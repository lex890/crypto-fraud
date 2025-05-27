import FreeSimpleGUI as sg
from fuzzywuzzy import process
import csv
import image as img

def load_crypto_data(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data

def get_search_terms(data):
    terms = []
    for row in data:
        terms.append(row['Name'])
        terms.append(row['Symbol'])
    return terms

def format_large_number(num):
    try:
        num = float(num.replace(',', ''))  # Remove commas and convert to float
    except (ValueError, AttributeError):
        return num  # Return as-is if not a number

    if num >= 1_000_000_000:
        return f"{int(num / 1_000_000_000)}B"
    elif num >= 1_000_000:
        return f"{int(num / 1_000_000)}M"
    elif num >= 1_000:
        return f"{int(num / 1_000)}K"
    else:
        return str(int(num))  # Return whole number if < 1,000


def search_crypto(query, data, search_terms, threshold=60, limit=10):
    query = query.strip()
    matches = process.extract(query, search_terms, limit=limit)
    seen = set()
    result_list = []

    for match, score in matches:
        if score >= threshold:
            for row in data:
                if (row['Name'] == match or row['Symbol'] == match) and row['Symbol'] not in seen:
                    seen.add(row['Symbol'])
                    result_list.append((
                        row['#'],
                        row['Name'],
                        row['Symbol'],
                        row['Logo'],
                        row['Market Cap (USD)'],
                        row['Current Price (USD)'],
                        row['24h%']
                    ))

    return result_list if result_list else "❌ No good match found."


def search_screen(user_search, file_path):
    if not user_search.strip():
        return sg.Window("Invalid", [[sg.Text("No search performed.")]], finalize=True)

    csv_data = load_crypto_data(file_path)
    search_terms = get_search_terms(csv_data)
    result = search_crypto(user_search, csv_data, search_terms)
    search_header, search_window = generate_results(result, user_search)

    

    layout = [
        [
            sg.Column(
                search_header, 
                size=(650, 100),
                background_color=sg.theme_background_color(),
                pad=((25, 0), (35, 0))
            ),
            sg.Push()
        ],
        [
            sg.Push(),
            sg.Column(
                search_window, 
                size=(650, 800), 
                background_color="#f6f6f6", 
                scrollable=True,
                vertical_scroll_only=True,
                pad=(0, (0, 45))
            ),
            sg.Push()
        ]
        
    ]

    return sg.Window('Search Result', layout, size=(850, 650))

def generate_results(result, user_search):
    if not isinstance(result, list):  # Handle no results case
        return [[sg.Text(result, font=('Helvetica', 14), text_color='red')]], [[sg.Text("Try a different search term.", font=('Helvetica', 12))]]

    search_header = [
        [
            sg.Button(
                '',
                image_filename='./images/searchSZ.png',
                image_size=(35, 35),
                button_color=(sg.theme_background_color(), sg.theme_background_color()),
                border_width=0,
                key='-SBUTTON-',
                pad=((0, 15), 0)
            ),
            sg.Text(
                f'Search: {user_search}', 
                font=('Helvetica', 16),
                text_color='#d1d1d1'
            )
        ]
    ]

    list_tab = []

    for index, item in enumerate(result):
        image = [
            [sg.Image(img.get_image(item[3]), size=(65, 65), background_color="#eaeaea", key=f'-ICON{index+1}-', enable_events=True)]
        ]

        info = [
            [sg.Button(f'{item[1]}', font=('League Spartan', 12, 'bold'), button_color="#eaeaea", border_width=0, key=f'-NAME{index+1}-'),
             sg.Text(f'#{item[0]}', font=('League Spartan', 12, 'bold'), background_color="#eaeaea", border_width=0, text_color='#919191') 
             ],
             [
                sg.Text(
                    f'{item[2]}', font=('League Spartan', 12, 'bold'), background_color="#eaeaea", 
                    pad=((8, 0), 0),
                    text_color='#919191')
             ]
        ]

        nums = [
            [sg.Text(f'MCap: {format_large_number(item[4])}', font=('League Spartan', 12, 'bold'), background_color="#eaeaea")],
            [sg.Text(f'Vol(24h): ${format_large_number(item[6])}', font=('League Spartan', 12, 'bold'), background_color="#eaeaea")]
        ]

        price = [
            [sg.Text(f'${item[5]}', font=('League Spartan', 12, 'bold'), background_color="#eaeaea")]
        ]

        card = [
            sg.Column(image, size=(80, 80), background_color="#eaeaea"),
            sg.Column(info, size=(150, 60), background_color="#eaeaea"),
            sg.Column(nums, size=(180, 60), background_color="#eaeaea"),
            sg.Column(price, size=(120, 60), background_color="#eaeaea")
        ]

        list_tab.append([sg.Column(
                [card], 
                size=(600, 85), 
                background_color="#eaeaea", 
                pad=((20, 0), (10, 7))
            )
        ])

    search_window = list_tab

    return search_header, search_window
