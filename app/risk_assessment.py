import FreeSimpleGUI as sg
import matplotlib.pyplot as plt
from . import get_images as img
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sg.theme('LightGrey1')

figure_canvas_agg_dict = {}
score_data_for_canvas = {}

def draw_figure(canvas_elem, figure, key, data_for_chart, is_main_score=False): 
    canvas = canvas_elem.TKCanvas
    if key in figure_canvas_agg_dict:
        figure_canvas_agg_dict[key].get_tk_widget().forget()
        plt.close('all')  # close previous matplotlib figures

    # Draw new figure
    figure_canvas_agg = FigureCanvasTkAgg(figure, master=canvas)
    figure_canvas_agg.draw()
    widget = figure_canvas_agg.get_tk_widget()
    widget.pack(side='top', fill='both', expand=1)

    widget.configure(cursor="hand2")

    # Store the data and is_main_score status associated with this key
    score_data_for_canvas[key] = {'data': data_for_chart, 'is_main': is_main_score}

    def on_click(event, canvas_key=key):
        if canvas_key == '-SCORE1-':
            sg.popup("Trading Volume Consistency",
                    "Checks if trading volume is stable over time.\n"
                    "Sudden unexplained spikes or drops may indicate manipulation.")
                    
        elif canvas_key == '-SCORE2-':
            sg.popup("Liquidity & Order Book Depth",
                    "Evaluates how easily tokens can be bought or sold without affecting the price.\n"
                    "Thin order books are common in scams or pump-and-dump schemes.")
                    
        elif canvas_key == '-SCORE3-':
            sg.popup("Token Age & Market History",
                    "Older tokens with long-term trading history are generally more trustworthy.\n"
                    "Recently launched tokens may be more prone to fraud.")
                    
        elif canvas_key == '-SCORE4-':
            sg.popup("Developer & Team Transparency",
                    "Assesses the public presence and credibility of the developers.\n"
                    "Anonymous or unverifiable teams are considered high risk.")
                    
        elif canvas_key == '-SCORE5-':
            sg.popup("Smart Contract Audit & Security",
                    "Checks if the token's smart contract has undergone third-party audits.\n"
                    "Unaudited or poorly written contracts may be vulnerable to exploits.")
                    
        elif canvas_key == '-SCORE6-':
            sg.popup("Exchange Listings & Reputation",
                    "Verifies if the token is listed on reputable exchanges.\n"
                    "Listing on major exchanges often indicates vetting and legitimacy.")
                    
        elif canvas_key == '-SCORE7-':
            sg.popup("Community & Social Media Presence",
                    "Analyzes activity on platforms like Twitter, Reddit, and Telegram.\n"
                    "Organic engagement suggests community trust and interest.")
                    
        elif canvas_key == '-SCORE8-':
            sg.popup("Transaction Patterns & Anomalies",
                    "Looks for suspicious patterns like repetitive large transfers,\n"
                    "wallet clustering, or sudden inactivity — common in scams.")
                    
        elif canvas_key == '-SCORE9-':
            sg.popup("Whitepaper & Roadmap Execution",
                    "Evaluates the quality and realism of the project's whitepaper and roadmap.\n"
                    "Empty buzzwords or no progress suggest a potential scam.")
                    
        elif canvas_key == '-SCORE10-':
            sg.popup("Regulatory Compliance & Legal Standing",
                    "Checks for known legal issues or warnings from authorities.\n"
                    "Projects compliant with regulations are generally safer.")

        

    widget.bind("<Button-1>", on_click)

    # Store reference
    figure_canvas_agg_dict[key] = figure_canvas_agg

# Helper function to draw a matplotlib figure on a PySimpleGUI Canvas element
def draw_figure_on_sg_canvas(canvas_elem, figure):
    # This is a generic function to draw a figure on any PySimpleGUI Canvas
    # It ensures the canvas is cleared before drawing a new figure
    for child in canvas_elem.TKCanvas.winfo_children():
        child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(figure, master=canvas_elem.TKCanvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# Create the pie chart figure
def create_pie_chart(score_data, figsize=(1.75, 1.75)):
    if (figsize == (3, 3)): # Used for the main score
        scores = [int(x) for x in score_data]
        value = round(sum(scores) / 10)
        fontsize_category = 12
        fontsize_score = 40
    else: # Used for individual scores and the score info window
        value = int(score_data)
        fontsize_category = 8
        fontsize_score = 16

    remainder = 10 - value
    if 8 <= value <= 10:
        category = "Trustworthy"
        color = "#07DB07"
    elif 6 <= value <= 7:
        category = "Moderate"
        color = "#DBB407"
    elif 4 <= value <= 5:
        category = "Questionable"
        color = "#DB6D07"
    else:
        category = "Untrustworthy"
        color = "#DB3807"

    sizes = [value, remainder]
    fig, ax = plt.subplots(figsize=figsize, facecolor='none')
    ax.pie(sizes,
           startangle=90,
           colors=[color, "#EEEEEE"])
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    # score in digit
    ax.text(0, 0.1, f'{value}', ha='center', va='center', fontsize=fontsize_score, weight='bold')

    # score category
    ax.text(0, -0.30, category, ha='center', va='center', fontsize=fontsize_category)
    ax.axis('equal')
    fig.tight_layout()
    return fig

def risk_assessment_window(window, data, row=0):
    score_data = data[row]

    for i in range(11):
        canvas_key = f'-SCORE{i}-' if i > 0 else '-MAINSCORE-'

        if canvas_key == '-MAINSCORE-':
            chart_data = score_data[13:23] # This is the data used for the main score
            fig = create_pie_chart(chart_data, figsize=(3, 3))
            is_main_score_flag = True
        else:
            chart_data = score_data[13 + (i - 1)] # Data for individual score
            fig = create_pie_chart(chart_data)
            is_main_score_flag = False

        if canvas_key in window.AllKeysDict:
            canvas_elem = window[canvas_key]

            draw_figure(canvas_elem, fig, canvas_key, chart_data, is_main_score_flag) # Pass data and flag


def update_risk_window(main_window, selected_row):
    main_window['-LOGO-'].update(data=img.get_image(selected_row[7]), size=(100, 100))
    main_window['-RANK-'].update(value=f'#{selected_row[0]}')
    main_window['-NAME-'].update(value=selected_row[1])
    main_window['-SYMB-'].update(value=selected_row[8])
    main_window['-DATE-'].update(value=f'Date Added: {selected_row[10]}')
    main_window['-DESC-'].update(value=f'Description: {selected_row[9]}')

def score_window(data, headings):
    # crypto icon/logo
    logo = [[sg.Image(img.get_image(data[0][7]), size=(100, 100), key='-LOGO-')]]
    #crypto info name/symbol/rank/desc
    info = [
        [
         sg.Text(f"#{data[0][0]}",           # crypto ranking
           font='Any 12 bold',
           pad=((10, 0), (13, 0)),
           text_color="#686868",
           key='-RANK-'),

         sg.Text(data[0][1],                   # crypto name
           font='Any 24 bold',
           key='-NAME-',
           pad=((5, 0), (20, 0))),

         sg.Text(data[0][8],                   # crypto symbol
           font='Any 12 bold',
           text_color='#a1a3a6',
           pad=((3, 0), (20, 5)),
           key='-SYMB-'),

         sg.Push(),
         sg.Text(f'Date Added: {data[0][10]}',   # date added
           font='Any 12 bold',
           text_color='#a1a3a6',
           pad=((0, 0), (0, 25)),
           key='-DATE-')
        ],

        [sg.Text(f'{data[0][9]}',   # crypto desc
           background_color="#fefefe",
           font=('Courier New', 12),
           size=(50, 12),
           auto_size_text=False,
           justification='left',
           pad=((40, 0), (15, 5)),
           key='-DESC-')]
    ]
    assessment_criteria = headings[13:23]
    print(assessment_criteria)
    # donut graphs scores
    assessment_score = [
        sg.Canvas(key=f"-SCORE{i+1}-", background_color=sg.theme_background_color(), size=(150, 150), expand_y=True, tooltip=assessment_criteria[i])
        for i in range(10)
    ]

    score = [[sg.Canvas(key="-MAINSCORE-", background_color=sg.theme_background_color(), size=(300, 300), tooltip='Overall Assessment Score')]]  # fix canvas space

    layout = [
        [
         sg.Column(logo, element_justification='center', vertical_alignment='top'),
         sg.Column(info, element_justification='left', vertical_alignment='top', size=(560, 306)),
         sg.Column(score, element_justification='center', vertical_alignment='top')
        ],

        [
         sg.Column([assessment_score[:5]], element_justification='center', expand_x=True, expand_y=True)
        ],

        [
         sg.Column([assessment_score[5:]], element_justification='center', expand_x=True, expand_y=True)
        ]
    ]

    return layout


    