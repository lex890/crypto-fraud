import FreeSimpleGUI as sg

# Window layout with a Canvas
layout = [
    [sg.Canvas(key='-CANVAS-', size=(150, 50))],
    [sg.Text("Click the 'canvas button' above")],
    [sg.Exit()]
]

window = sg.Window("Canvas as Button", layout, finalize=True)

# Get the Tkinter Canvas object
tk_canvas = window['-CANVAS-'].TKCanvas

# Draw a button-like rectangle
button_id = tk_canvas.create_rectangle(0, 0, 150, 50, fill="lightblue", outline="black")
text_id = tk_canvas.create_text(75, 25, text="Canvas Button", font="Arial 12 bold")

# Define a click handler
def on_canvas_click(event):
    if 0 <= event.x <= 150 and 0 <= event.y <= 50:
        sg.popup("Canvas Button Clicked!")

# Bind the left mouse button click to the canvas
tk_canvas.bind("<Button-1>", on_canvas_click)

# Event loop
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == "Exit":
        break

window.close()
