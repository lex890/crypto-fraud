import FreeSimpleGUI as sg
from . import risk_assessment as rsk

def main_screen(headings, data):
    layout = [
        #header and icon
        [
            sg.Image(filename='./images/main.png', size=(17, 15), pad=((25, 0), (25, 0)), enable_events=True, key='-HEADERICON-'), 
            sg.Text('Crypto Fraud Detection Tool', font=('Helvetica', 16), pad=((15, 0), (25, 0)), enable_events=True, key='-HEADER-'),
            sg.Push(),
            
        ],
        #search bar and bunch of buttons
        [
            [   
                sg.Button('', image_filename='./images/byalphaR.png',image_size=(50, 50), button_color=("#F0F0F0", sg.theme_background_color()), border_width=1, pad=((50, 0), (75, 0)), key=('-ALPHA-'), tooltip='Sort by Alpha'),
                sg.Button('', image_filename='./images/bynumberR.png',image_size=(50, 50), button_color=("#F0F0F0", sg.theme_background_color()), border_width=1, pad=((10, 0), (75, 0)), key=('-NUMBER-'), tooltip='Sort by Ranking(#)'),
                sg.Button('', image_filename='./images/bypriceR.png',image_size=(50, 50), button_color=("#F0F0F0", sg.theme_background_color()), border_width=1, pad=((10, 0), (75, 0)), key=('-PRICE-'), tooltip='Sort by Price($)'),

                sg.InputText(
                    default_text='',
                    size=(25, 1),
                    font=('Helvetica', 18),
                    pad=((200, 10), (75, 0)),
                    key='-SEARCHBAR-',
                    tooltip='Search Cryptocurrency',
                    text_color='gray'
                ),
                sg.Button(
                    '',
                    image_filename='./images/searchR.png',
                    image_size=(50, 50),
                    button_color=(sg.theme_background_color(), sg.theme_background_color()),
                    border_width=0,
                    key='-SBUTTON-',
                    pad=((0, 25), (75, 0))
                )
                
            ],
            # lower part of the main screen
            [
                sg.Table(
                    values=data,
                    headings=headings[:7],
                    max_col_width=10,
                    auto_size_columns=False,
                    justification='center',
                    col_widths=[5, 12, 16, 6, 6, 6, 18],
                    num_rows=15,
                    key='-TABLE-',
                    row_height=51,
                    font=('Helvetica', 12, 'bold'),
                    pad=((50, 0), (0, 0)),
                    hide_vertical_scroll=True,
                    enable_events=True
                ),
                sg.Column(rsk.score_window(data, headings), background_color="#E6E6E6", expand_y=True, expand_x=True, pad=((50, 50), (42, 40)),)
            ]
            
        ]
    ]
    window = sg.Window('Main App', layout, finalize=True, resizable=True)
    rsk.risk_assessment_window(window, data)
    window.Maximize()
    
    return window