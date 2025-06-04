import re
import app
import FreeSimpleGUI as sg

sg.theme('LightGrey1')
sg.theme_button_color(('black', 'gainsboro'))
pattern = re.compile(r'^-(ICON|NAME)(\d+)-$')
cmc_img = './images/resizedCMC.png'
cg_img = './images/resizedCG.png'

current_image = {
    '-IMAGE-': './images/resizedCMC.png',
}
currency_choice = 'USD'
data = []


def main():
    current_page = 1
    rows_per_page = 14
    login_window = app.login_screen()
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

        elif lw_event == '-KEYSTORE-':
            api_choice = 'CoinMarketCap' if current_image['-IMAGE-'] == './images/resizedCMC.png' else 'CoinGecko'
            cfg_key = 'CMCKEY' if current_image['-IMAGE-'] == './images/resizedCMC.png' else 'CGKEY'
            new_api_key = app.load_api_key(api_choice, cfg_key)
            login_window['-API-'].update(value=new_api_key) 
        
        elif lw_event == '-SAVEKEY-':
            api_key = lw_values.get('-API-', '').strip() #read API key
            api_choice = 'CoinMarketCap' if current_image['-IMAGE-'] == './images/resizedCMC.png' else 'CoinGecko'
            cfg_key = 'CMCKEY' if current_image['-IMAGE-'] == './images/resizedCMC.png' else 'CGKEY'
            app.save_api_key(api_choice, api_key, cfg_key)

        elif lw_event == 'Clear': # clear the api key input  
            login_window['-API-'].update('')

        elif lw_event == 'Confirm': # confirm button
            api_key = lw_values.get('-API-', '').strip() #read API key
            currency_choice = lw_values.get('-CURRENCY-')
            print(f"API Key Entered: '{api_key}'")  # Add logging
            print(f"Currency Choice: '{currency_choice}'")  # Add logging
            api_choice = '1' if current_image['-IMAGE-'] == './images/resizedCMC.png' else '2'
        
            if (api_choice == '1'):
                validity = app.is_valid_cmc_api_key(api_key)
            else:
                validity = app.is_valid_cg_api_key(api_key)


            if not validity and api_choice == '1': # coingecko wont ping if its free tier
                sg.popup('Please enter a valid API key.')
            else:
                print(validity, api_choice, api_key)

                login_window.hide()

                result = app.run_with_loading(app.api_request, api_key, api_choice, currency_choice)

                headings, data, filepath = result #remove
                print(headings, data, filepath)

                main_window = app.main_screen(headings, data)
                print('Data fetched successfully')
                reverse_flag = True
                while True:
                    mw_event, mw_values = main_window.read()
                    print(mw_event)

                    if mw_event == '-SCORE-CLICKED-':
                        key = mw_values[mw_event]
                        # Show popup here
                        if key in app.descriptions:
                            title, msg = app.descriptions[key]
                            sg.popup(title, msg, title=title, font=("Helvetica", 12), keep_on_top=True)

                    if mw_event == '-MAIN-CLICKED-':
                        sg.Window(
                            "Risk Score Guide",
                            [
                                [sg.Text("Score Interpretation", font=("Helvetica", 14, "bold"))],
                                [sg.Text("1 - 3   : High-Risk/Fraudulent (Avoid)", text_color="red", font=("Helvetica", 10, "bold"))],
                                [sg.Text("4 - 6   : Medium Risk (Caution)", text_color="orange", font=("Helvetica", 10, "bold"))],
                                [sg.Text("7 - 10  : Trustworthy (Safe to interact with)", text_color="green", font=("Helvetica", 10, "bold"))],
                                [sg.Button("OK", size=(10, 1))]
                            ],
                            modal=True,
                            keep_on_top=True
                        ).read(close=True) 

                    if mw_event == '-TABLE-':
                        selected_row_indices = mw_values['-TABLE-']
                        print(selected_row_indices)
                        if selected_row_indices:  
                            selected_index = selected_row_indices[0]
                            selected_row = data[selected_index]
                            current_row = int(selected_row[0]) - 1
                            app.update_risk_window(main_window, selected_row)
                            app.risk_assessment_window(main_window, data, current_row)

                    if mw_event in ('-HEADERICON-', 'HEADER'):
                        main_window.close()
                        break

                    elif mw_event == '-NEXT-':
                        max_pages = (len(data) + rows_per_page - 1) // rows_per_page
                        if current_page < max_pages:
                            current_page += 1
                            main_window['-TABLE-'].update(values=app.get_page_data(data, current_page, rows_per_page))
                            main_window['-PAGENO-'].update(str(current_page))
                    elif mw_event == '-PREV-':
                        if current_page > 1:
                            current_page -= 1
                            main_window['-TABLE-'].update(values=app.get_page_data(data, current_page, rows_per_page))
                            main_window['-PAGENO-'].update(str(current_page))

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

                        search_window, key_to_data = app.search_screen(user_search, filepath)
                        
                        while True:
                            sw_event, _ = search_window.read()

                            if sw_event == '-CBUTTON-':
                                search_window.close()

                            if user_search == '' or sw_event in (sg.WIN_CLOSED, 'Exit'):
                                search_window.close()
                                break

                            if isinstance(sw_event, str):
                                match = pattern.match(sw_event)
                                if match:
                                    current_row = int(key_to_data[sw_event][0]) - 1
                                    app.update_risk_window(main_window, key_to_data[sw_event])
                                    app.risk_assessment_window(main_window, data, current_row)
                                    
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
