import FreeSimpleGUI as sg
import matplotlib.pyplot as plt
import image as img
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
    else:
      value = scores
      remainder = 10 - value 

    sizes = [value, remainder]
    fig, ax = plt.subplots(figsize=figsize, facecolor='none')
    ax.pie(sizes, 
           startangle=90,
           colors=['#2196F3', '#FFFFFF'])
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    # score in digit
    ax.text(0, 0.1, f'{value}', ha='center', va='center', fontsize=24, weight='bold')

    # score category
    ax.text(0, -0.30, 'Trustworthy', ha='center', va='center', fontsize=8)
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
          fig = create_pie_chart(scores[i-1]) # 10 small lol

      if canvas_key in window.AllKeysDict:
          draw_figure(window[canvas_key], fig)


def score_window(data):
    # crypto icon/logo
    logo = [[sg.Image(img.get_image(data[0][7]), size=(100, 100), key='-LOGO-')]]
    #crypto info name/symbol/rank/desc 
    info = [
        [
         sg.Text(f"#{data[0][0]}",              # crypto ranking
          font='Any 12 bold',
          pad=((10, 0), 0),
          text_color="#686868",
          key='-RANK-'),

         sg.Text(data[0][1],                    # crypto name
          font='Any 24 bold',
          key='-NAME-'),

         sg.Text(data[0][8],                    # crypto symbol
          font='Any 12 bold', 
          text_color='#a1a3a6',
          pad=((3, 0), (0, 5)),
          key='-SYMB-') 
        ],

        [sg.Text(f'Description: {data[0][9]}',  # crypto desc
         background_color="#e9e9e9", 
         font=('Courier New', 12),   
         size=(58, 12),
         auto_size_text=False, 
         justification='left',
         pad=((10, 10), (25, 10)),
         key='-DESC-')]
    ]
    # donut graphs scores
    assessment_score = [
        sg.Canvas(key=f"-SCORE{i+1}-", background_color=sg.theme_background_color(), size=(150, 150), expand_y=True)
        for i in range(10)
    ]

    score = [[sg.Canvas(key="-MAINSCORE-", background_color=sg.theme_background_color(), size=(300, 300))]]  # fix canvas space

    layout = [
        [
         sg.Column(logo, element_justification='center', vertical_alignment='top'),
         sg.Column(info, element_justification='left', vertical_alignment='top'),
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


