import json
from flask import Flask, request
import pytesseract
import base64
import requests
import os
from dateparser import parse as parse_date

app = Flask(__name__)

# Verifies if the date is valid
def is_valid_date(candidate):
    try:
        parsed_date = parse_date(candidate, languages=['pt'])
        if parsed_date:
            return True
        else:
            return False
    except ValueError:
        return False

# Uses OpenAI Completions endpoint to proccess the name with advanced NPL
def extract_names_with_openai(text):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': os.getenv('SECRET_KEY')
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": "Você é um bot que visualiza o texto de um comprovante de pagamento transcrito pelo Tesseract e retorna apenas o nome do destinatário e remetente da transação."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0.7
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()
        content = response_json['choices'][0]['message']['content']
        lines = content.split('\n')
        destiny = lines[0].split(': ')[1] if len(lines) > 0 else None
        origin = lines[1].split(': ')[1] if len(lines) > 1 else None
        return destiny, origin

    else:
        return None, None

# This the main function that proccess the request
@app.route('/taxman/api/extract_data_from_image', methods=['POST'])
def extract_data_from_image():
    # Gets the image's Base64 code from the request body
    image_base64 = request.json['image_base64']

    # Creates a temp. file to proccess the image
    with open('temp.png', 'wb') as f:
        f.write(base64.b64decode(image_base64))

    # Uses Tesseract to extract text from image
    text = pytesseract.image_to_string('temp.png', lang='por')

    # Uncomment this lil bastard to debug this GODLY masterpiece of coding
    # print(text)

    date = None
    value = None
    origin = None
    destiny = None

    # Iterates the extracted text for potential dates
    words = text.split()
    i = 0
    while i < len(words):
        if '/' in words[i]:
            potential_date = words[i]
            if is_valid_date(potential_date):
                date = potential_date
                break
        i += 1

    # If he doesn't find any dates at first, he tries again on the next one
    while i < len(words) - 1 and (date is None or not is_valid_date(date)):
        i += 1
        if '/' in words[i]:
            potential_date = words[i]
            if is_valid_date(potential_date):
                date = potential_date

    # Calls the NPL function to catch names
    names = extract_names_with_openai(text)

    # Defines destiny as the first name/company and origin as the second (this is usually the case with most vouchers)
    if len(names) >= 2:
        destiny = names[0]
        origin = names[1]

    # Checks for texts with ',', those are usually monetary values
    for word in words:
        if ',' in word:
            try:
                value = float(word.replace(',', '.'))
            except ValueError:
                pass

    # Returns the JSON response
    result = {
        'date': date,
        'value': value,
        'destiny': destiny,
        'origin': origin,
        'success': True,
    }

    return json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == '__main__':
    app.run(debug=True)