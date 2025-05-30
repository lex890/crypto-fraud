import FreeSimpleGUI as sg

layout = [
    [sg.Text("Choose an option:")],
    [sg.Combo(['Option 1', 'Option 2', 'Option 3'], default_value='Option 1', key='-COMBO-')],
    [sg.Button("Submit")]
]

window = sg.Window("Dropdown Example", layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Submit":
        sg.popup(f"You selected: {values['-COMBO-']}")

window.close()
