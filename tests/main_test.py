import sys
import os
import FreeSimpleGUI as sg
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import matplotlib.pyplot as plt
import app

sg.theme('LightGrey1')
sg.theme_button_color(('black', 'gainsboro'))
pattern = re.compile(r'^-(ICON|NAME)(\d+)-$')
cmc_img = './images/resizedCMC.png'
cg_img = './images/resizedCG.png'

current_image = {
    '-IMAGE-': './images/resizedCMC.png',
}

data = []

def main():
    login_window = app.login_screen() #should be login first "log.login_screen()"

    # Main event loop
    while True:
        lw_event, lw_values = login_window.read()
        print(lw_event, lw_values)
        if lw_event in (sg.WIN_CLOSED, 'Exit'):
            break

        elif lw_event == '-CRYPTO-':  # Toggle crypto image 
            if current_image['-IMAGE-'] == './images/resizedCG.png':
                new_image = cmc_img
            else:
                new_image = cg_img

            login_window['-CRYPTO-'].update(filename=new_image)     # crypto logo
            current_image['-IMAGE-'] = new_image                    # update image container

        elif lw_event == 'Clear': # clear the api key input  
            login_window['-API-'].update('')

        elif lw_event == 'Confirm': # confirm button
            api_key = lw_values.get('-API-', '').strip() #read API key
            api_choice = '1' if current_image['-IMAGE-'] == './images/resizedCMC.png' else 2
            
            if (api_choice == '1'):
                validity = app.is_valid_cmc_api_key(api_key)
            else:
                validity = app.is_valid_cg_api_key(api_key)

            if not validity: 
                sg.popup('Please enter a valid API key.')
            else:
                print(validity, api_choice, api_key)

                login_window.hide()
            
                file_path = f'./data/data.csv'
                headings, data = app.read_csv(file_path)

                main_window = app.main_screen(headings, data)

                print('Data fetched successfully')
                # flags for buttons
                reverse_flag = True

                # main menu loop
                while True:
                    mw_event, mw_values = main_window.read()
                    print(mw_event)

                    if mw_event == '-TABLE-':
                        print('im here')
                        selected_row_indices = mw_values['-TABLE-']
                        print(selected_row_indices)
                        if selected_row_indices:
                            selected_index = selected_row_indices[0]
                            selected_row = data[selected_index]
                            current_row = int(selected_row[0]) - 1
                            app.update_risk_window(main_window, selected_row)
                            app.risk_assessment_window(main_window, data, current_row)

                    # sorting buttons
                    if mw_event == '-NUMBER-': # sort by ascending/descending
                        data.sort(key=lambda x: int(x[0]), reverse = reverse_flag)
                        reverse_flag = not reverse_flag
                        main_window['-TABLE-'].update(values=data)
                    if mw_event == '-ALPHA-': # sort by alphabetical order
                        data.sort(key=lambda x: x[1], reverse = reverse_flag)
                        reverse_flag = not reverse_flag
                        main_window['-TABLE-'].update(values=data)
                    if mw_event == '-PRICE-': # sort by current price
                        data.sort(key=lambda x: float(x[2].replace(',', '')), reverse = reverse_flag)
                        reverse_flag = not reverse_flag 
                        main_window['-TABLE-'].update(values=data)
                    
                    # search button
                    if mw_event == '-SBUTTON-':
                        user_search = mw_values['-SEARCHBAR-']

                        if user_search == '':
                            continue  

                        search_window, key_to_data = app.search_screen(user_search, file_path)
                        
                        while True:
                            sw_event, _ = search_window.read()

                            if user_search == '' or sw_event in (sg.WIN_CLOSED, 'Exit'):
                                search_window.close()
                                break

                            if isinstance(sw_event, str):
                                match = pattern.match(sw_event)
                                if match:
                                    app.update_risk_window(main_window, key_to_data[sw_event])
                                    search_window.close()
                                    break

                    if mw_event in (sg.WIN_CLOSED, 'Exit'):
                        print('closing now')
                        main_window.close()
                        break
                login_window.un_hide()  

        elif lw_event == '-HELP-':
            sg.popup('Your API Key allows the app to access data from providers like CoinGecko or CoinMarketCap. Keep it private.')

    login_window.close()

if __name__ == '__main__':
    main()

