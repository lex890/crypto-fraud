import threading
import time
import FreeSimpleGUI as sg

# Loading screen window
def show_loading_window():
    layout = [
        [sg.Text('Contacting API...', font=('Helvetica', 14))],
        [sg.ProgressBar(100, orientation='h', size=(30, 20), key='-PROG-')]
    ]
    return sg.Window('Loading', layout, finalize=True, keep_on_top=True, no_titlebar=True)

# Main wrapper function
def run_with_loading(api_request, api_key, api_choice, currency_choice):
    result_holder = {}

    # Create and show the loading screen first
    loading_win = show_loading_window()
    prog_bar = loading_win['-PROG-']
    i = 0

    # Background API thread
    def target():
        try:
            result_holder['value'] = api_request(api_key, api_choice, currency_choice)
        except Exception as e:
            result_holder['error'] = e

    # Delay thread start to let GUI fully render one cycle
    thread_started = False

    while True:
        event, _ = loading_win.read(timeout=100)
        prog_bar.UpdateBar(i % 100)
        i += 5

        if not thread_started:
            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread_started = True

        if not thread.is_alive():
            break

        if event == sg.WIN_CLOSED:
            break

    loading_win.close()

    if 'error' in result_holder:
        raise result_holder['error']

    return result_holder['value']  # => (headings, data, filename)
    
