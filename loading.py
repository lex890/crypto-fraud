import FreeSimpleGUI as sg
import threading
import time

# Simulate an API call (replace with real function)
def fetch_api_data():
    time.sleep(3)  # Simulated delay
    return {"data": "API response"}

# Function to show a loading screen
def show_loading_window():
    layout = [
        [sg.Text('Contacting API...', font=('Helvetica', 14))],
        [sg.ProgressBar(100, orientation='h', size=(30, 20), key='-PROG-')],
    ]
    return sg.Window('Loading', layout, finalize=True, keep_on_top=True, no_titlebar=True)

def main():
    # Start API call in a separate thread to avoid freezing UI
    response_data = {}

    def run_api():
        response_data['result'] = fetch_api_data()

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    loading_win = show_loading_window()
    prog_bar = loading_win['-PROG-']
    i = 0

    # Loop until thread is done
    while api_thread.is_alive():
        prog_bar.UpdateBar(i % 100)
        i += 5
        event, _ = loading_win.read(timeout=100)
        if event == sg.WIN_CLOSED:
            break

    loading_win.close()

    # Now show results (simulate or integrate into app)
    sg.popup('Done!', f"API Result: {response_data['result']['data']}")

# Run it
main()
