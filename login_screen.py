import FreeSimpleGUI as sg

def login_screen():
    layout = [
        # logo and main heading
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





  

