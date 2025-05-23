import FreeSimpleGUI as sg
import login_screen as log
import main_screen as msc
import request as req
import image as img
import table as tbl

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
        event, values = window.read()
        print(event, values)
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        elif event == '-CRYPTO-':  # Toggle crypto image 
            if current_image['-IMAGE-'] == './images/resizedCG.png':
                new_image = cmc_img
            else:
                new_image = cg_img

            window['-CRYPTO-'].update(filename=new_image)
            current_image['-IMAGE-'] = new_image

        elif event == 'Clear': # clear the api key input  
            window['-API-'].update('')

        elif event == 'Confirm': # confirm button
            api_key = values.get('-API-', '').strip() #read API key
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
            
                filename = f'./cryptodata/data.csv'
                headings, data = tbl.read_csv(filename)

                main_window = msc.main_screen(headings, data)

                print('Data fetched successfully')
                # flags for buttons
                reverse_flag = True

                while True:
                    mm_event, mm_values = main_window.read()
                    print(mm_event)

                    if mm_event == '-TABLE-':
                        selected_row_indices = mm_values['-TABLE-']
                        if selected_row_indices:  
                            selected_index = selected_row_indices[0]
                            selected_row = data[selected_index]
                            
                            main_window['-LOGO-'].update(data=img.get_image(selected_row[7]), size=(100, 100))
                            main_window['-RANK-'].update(value=f'#{selected_row[0]}')
                            main_window['-NAME-'].update(value=selected_row[1])
                            main_window['-SYMB-'].update(value=selected_row[8])
                            main_window['-DESC-'].update(value=f'Description: {selected_row[9]}')

                    if mm_event == '-NUMBER-': # sort by ascending/descending
                        data.sort(key=lambda x: int(x[0]), reverse = reverse_flag)
                        reverse_flag = not reverse_flag
                        main_window['-TABLE-'].update(values=data)
                    if mm_event == '-ALPHA-': # sort by alphabetical order
                        data.sort(key=lambda x: x[1], reverse = reverse_flag)
                        reverse_flag = not reverse_flag
                        main_window['-TABLE-'].update(values=data)
                    if mm_event == '-PRICE-': # sort by current price
                        data.sort(key=lambda x: float(x[2].replace(',', '')), reverse = reverse_flag)
                        reverse_flag = not reverse_flag 
                        main_window['-TABLE-'].update(values=data)

                    if mm_event in (sg.WIN_CLOSED, 'Exit'):
                        print('closing now')
                        main_window.close()
                        break
                window.un_hide()

        elif event == '-HELP-':
            sg.popup('An API Key is a unique identifier used to authenticate a user or developer.')

    window.close()

if __name__ == '__main__':
    main()
