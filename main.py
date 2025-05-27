import FreeSimpleGUI as sg
import risk_assessment as rsk
import login_screen as log
import main_screen as msc
import request as req
import image as img



sg.theme('LightGrey1')
sg.theme_button_color(('black', 'gainsboro'))

cmc_img = './images/resizedCMC.png'
cg_img = './images/resizedCG.png'

current_image = {
    '-IMAGE-': './images/resizedCMC.png',
}

data = []

def main():
    window = log.login_screen() #should be login first "log.login_screen()"

    # Main event loop
    while True:
        lw_event, lw_values = window.read()
        print(lw_event, lw_values)
        if lw_event in (sg.WIN_CLOSED, 'Exit'):
            break

        elif lw_event == '-CRYPTO-':  # Toggle crypto image 
            if current_image['-IMAGE-'] == './images/resizedCG.png':
                new_image = cmc_img
            else:
                new_image = cg_img

            window['-CRYPTO-'].update(filename=new_image)
            current_image['-IMAGE-'] = new_image

        elif lw_event == 'Clear': # clear the api key input  
            window['-API-'].update('')

        elif lw_event == 'Confirm': # confirm button
            api_key = lw_values.get('-API-', '').strip() #read API key
            api_choice = '1' if current_image['-IMAGE-'] == './images/resizedCMC.png' else 2
            
            if (api_choice == '1'):
                validity = req.is_valid_cmc_api_key(api_key)
            else:
                validity = req.is_valid_cg_api_key(api_key)

            if not validity: 
                sg.popup('Please enter a valid API key.')
            else:
                print(validity, api_choice, api_key)

                window.hide()
            
                try:
                    result = req.api_request(api_key, api_choice)
                    
                    if not result or not isinstance(result, tuple) or len(result) != 2:
                        raise ValueError("Unexpected response format from API.")

                    headings, data, filename = result

                    if not headings or not isinstance(headings, list) or not all(isinstance(h, str) for h in headings):
                        raise ValueError("Invalid or missing table headings.")

                    if not data or not isinstance(data, list) or not all(isinstance(row, (list, tuple)) and len(row) == len(headings) for row in data):
                        raise ValueError("Invalid or mismatched data rows.")

                except Exception as e:
                    sg.popup_error(f"Failed to fetch valid data from API:\n{str(e)}")
                    window.un_hide()
                    return

                main_window = msc.main_screen(headings, data)

                print('Data fetched successfully')
                # flags for buttons
                reverse_flag = True

                while True:
                    mw_event, mw_values = main_window.read()
                    print(mw_event)

                    if mw_event == '-TABLE-':
                        selected_row_indices = mw_values['-TABLE-']
                        print(selected_row_indices)
                        if selected_row_indices:  
                            selected_index = selected_row_indices[0]
                            selected_row = data[selected_index]
                            rsk.update_risk_window(main_window, selected_row)


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

                    if mw_event in (sg.WIN_CLOSED, 'Exit'):
                        print('closing now')
                        main_window.close()
                        break
                window.un_hide()

        elif lw_event == '-HELP-':
            sg.popup('An API Key is a unique identifier used to authenticate a user or developer.')

    window.close()

if __name__ == '__main__':
    main()
