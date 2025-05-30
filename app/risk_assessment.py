import FreeSimpleGUI as sg
import matplotlib.pyplot as plt
from . import get_images as img
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sg.theme('LightGrey1')

# Helper function to draw on a PySimpleGUI Canvas 
def draw_figure(canvas_elem, figure):
    canvas = canvas_elem.TKCanvas # Tkinter widget
    figure_canvas_agg = FigureCanvasTkAgg(figure, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

# Create the pie chart figure
def create_pie_chart(scores, figsize=(1.5, 1.5)):
    if (figsize == (3, 3)):
      value = round(sum(scores) / 10)
      remainder = 10 - value
      fontsize_category = 12
      fontsize_score = 40
    else:
      value = scores
      remainder = 10 - value 
      fontsize_category = 8
      fontsize_score = 12

    sizes = [value, remainder]
    fig, ax = plt.subplots(figsize=figsize, facecolor='none')
    ax.pie(sizes, 
           startangle=90,
           colors=['#2196F3', '#FFFFFF'])
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    # score in digit
    ax.text(0, 0.1, f'{value}', ha='center', va='center', fontsize=fontsize_score, weight='bold')

    # score category
    ax.text(0, -0.30, 'Trustworthy', ha='center', va='center', fontsize=fontsize_category)
    ax.axis('equal')
    fig.tight_layout()
    return fig

def risk_assessment_window(window, scores):
    # Draw pie charts on all CANVAS elements
    for i in range(11):
      canvas_key = f'-SCORE{i}-' if i > 0 else '-MAINSCORE-'
      if canvas_key == '-MAINSCORE-':
          fig = create_pie_chart(scores, figsize=(3, 3)) # big circle score
      else: 
          fig = create_pie_chart(scores[i-1]) # 10 small

      if canvas_key in window.AllKeysDict:
          draw_figure(window[canvas_key], fig)


def update_risk_window(main_window, selected_row):
    main_window['-LOGO-'].update(data=img.get_image(selected_row[7]), size=(100, 100))
    main_window['-RANK-'].update(value=f'#{selected_row[0]}')
    main_window['-NAME-'].update(value=selected_row[1])
    main_window['-SYMB-'].update(value=selected_row[8])
    main_window['-DATE-'].update(value=f'Date Added: {selected_row[10]}')
    main_window['-DESC-'].update(value=f'Description: {selected_row[9]}')

def score_window(data):
    # crypto icon/logo
    logo = [[sg.Image(img.get_image(data[0][7]), size=(100, 100), key='-LOGO-')]]
    #crypto info name/symbol/rank/desc 
    info = [
        [
         sg.Text(f"#{data[0][0]}",              # crypto ranking
          font='Any 12 bold',
          pad=((10, 0), (13, 0)),
          text_color="#686868",
          key='-RANK-'),

         sg.Text(data[0][1],                    # crypto name
          font='Any 24 bold',
          key='-NAME-',
          pad=((5, 0), (20, 0))),

         sg.Text(data[0][8],                    # crypto symbol
          font='Any 12 bold', 
          text_color='#a1a3a6',
          pad=((3, 0), (20, 5)),
          key='-SYMB-'),

         sg.Push(),
         sg.Text(f'Date Added: {data[0][10]}',  # date added
          font='Any 12 bold', 
          text_color='#a1a3a6',
          pad=((0, 0), (0, 25)),
          key='-DATE-')
        ],
        
        [sg.Text(f'{data[0][9]}',  # crypto desc
         background_color="#fefefe", 
         font=('Courier New', 12),   
         size=(50, 12),
         auto_size_text=False, 
         justification='left',
         pad=((40, 0), (15, 5)),
         key='-DESC-')]
    ]
    assessment_criteria = ['Trading Volume Consistency', 'Liquidity & Order Book Depth', 'Token Age & Market History', 'Developer & Team Transparency', 'Smart Contract Audit & Security', 'Exchange Listings & Reputation', 'Community & Social Media Presence', 'Transaction Patterns & Anomalies', 'Whitepaper & Roadmap Execution', 'Regulatory Compliance & Legal Standing']

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


