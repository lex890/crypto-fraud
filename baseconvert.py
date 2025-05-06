import base64

def save_image_as_base64(input_image_path, output_text_path):
    
    with open(input_image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    with open(output_text_path, "w") as text_file:
        text_file.write(encoded_string)

    print(f"Base64 saved to {output_text_path}")

input_image_path = "./images/logo.png"  # Replace with your image path
output_text_path = "./images/logo_base64.txt"  # Replace with your desired output path

save_image_as_base64(input_image_path, output_text_path)
