import FreeSimpleGUI as sg
import login_screen as log
import main_screen as msc
import request as req
import image as img
import table as tbl
import risk_assessment as rsk
import search_screen as src
import re

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
    login_window = log.login_screen() #should be login first "log.login_screen()"

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
                validity = req.is_valid_cmc_api_key(api_key)
            else:
                validity = req.is_valid_cg_api_key(api_key)

            if not validity: 
                sg.popup('Please enter a valid API key.')
            else:
                print(validity, api_choice, api_key)

                login_window.hide()
            
                file_path = f'./cryptodata/dataa.csv'
                headings, data = tbl.read_csv(file_path)

                main_window = msc.main_screen(headings, data, file_path)

                print('Data fetched successfully')
                # flags for buttons
                reverse_flag = True

                # main menu loop
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
                        search_window = src.search_screen(user_search, file_path)
                        
                        while True:
                            sw_event, sw_values = search_window.read()

                            match = pattern.match(sw_event)
                            if match:
                                element_type = match.group(1)  # 'ICON' or 'NAME'
                                index = int(match.group(2))    # '0', '1', etc.
                                print(f'Clicked {element_type} at index {index}')
                                search_window.close()
                                break
                                

                            if sw_event in (sg.WIN_CLOSED, 'Exit'):
                                search_window.close()
                                break

                    if mw_event in (sg.WIN_CLOSED, 'Exit'):
                        print('closing now')
                        main_window.close()
                        break
                login_window.un_hide()

        elif lw_event == '-HELP-':
            sg.popup('An API Key is a unique identifier used to authenticate a user or developer.')

    login_window.close()

if __name__ == '__main__':
    main()

