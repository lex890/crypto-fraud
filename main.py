import FreeSimpleGUI as sg

sg.theme('LightGrey1')
sg.theme_button_color(('black', 'gainsboro'))

current_image = {
            '-IMAGE-': './images/resizedCMC.png',
        }

def login_screen():
    layout = [
        [
            sg.Image(filename='./images/resizedLogo.png', size=(50, 50)),
            sg.Text('Crypto Fraud Detection Tool', font=('Helvetica', 20), pad=(10, 30))
        ],

        [sg.Text('API Key', font=('Helvetica', 12), pad=((180, 0), (50, 0)))],

        [
            sg.Push(),
            sg.InputText(key='-API-', size=(40, 1), font=('Helvetica', 12), tooltip='Enter API Key'),
            sg.Image(filename='./images/resizedCMC.png', size=(50, 50), enable_events=True, key='-CRYPTO-',),
            sg.Push()
        ],

        [
            sg.Text('Enter your API key to access the service.', font=('Helvetica', 10),
                    pad=((176, 0), (0, 0))),
        ],

        [
            sg.Button('Clear', size=(10, 1), pad=((360, 0), (0, 0))),
            sg.Button('Confirm', size=(10, 1), pad=(5, 20))
        ],

        [
            sg.Push(),
            sg.Text('What is an API Key', font=('Helvetica', 10), enable_events=True, key='-HELP-',
                    pad=((0, 0), (100, 0))),
            sg.Text('❓', pad=((0, 0), (100, 0)))
        ]
    ]

    return sg.Window('Crypto Fraud Detection Tool', layout, size=(800, 450))


def main_app_screen():
    with open("./images/logo_base64.txt", "r") as f:
        logo_base64 = f.read()

    layout = [
        [
            sg.Image(filename='./images/main.png', size=(17, 15)), 
            sg.Text('Crypto Fraud Detection Tool', font=('Helvetica', 16))
        ],
        [sg.Button('', image_data=logo_base64, size=(17, 15))]
    ]
    return sg.Window('Main App', layout, size=(800, 450), modal=True)


def main():
    window = login_screen()

    while True:
        event, values = window.read()

        if event == '-CRYPTO-':
            if current_image['-IMAGE-'] == './images/resizedCG.png':
                new_image = './images/resizedCMC.png'
            else:
                new_image = './images/resizedCG.png'

            window['-CRYPTO-'].update(filename=new_image)
            current_image['-IMAGE-'] = new_image

        if event == sg.WIN_CLOSED:
            break
        elif event == 'Clear':
            window['-API-'].update('')
        elif event == 'Confirm':
            if values['-API-'].strip() == "": # Check if the API key is empty
                sg.popup('Please enter a valid API key.')
            else:
                window.hide()  # Hide login window
                main_window = main_app_screen()
                while True:
                    m_event, _ = main_window.read()
                    if m_event in (sg.WIN_CLOSED, 'Exit'):
                        main_window.close()
                        break
                window.un_hide()  # Return to login screen if needed
        elif event == '-HELP-':
            sg.popup('An API Key is a unique identifier used to authenticate a user or developer.')

    window.close()


if __name__ == '__main__':
    main()
