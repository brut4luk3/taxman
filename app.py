from flask import Flask, request, jsonify
import pytesseract
import base64
from dateparser import parse as parse_date

app = Flask(__name__)

def is_valid_date(candidate):
    try:
        parsed_date = parse_date(candidate, languages=['pt'])
        if parsed_date:
            return True
        else:
            return False
    except ValueError:
        return False

@app.route('/taxman/api/extract_data_from_image', methods=['POST'])
def extract_data_from_image():
    # Extrai a imagem codificada em base64 do corpo da solicitação
    image_base64 = request.json['image_base64']

    # Decodifica a imagem e a salva em um arquivo temporário
    with open('temp.png', 'wb') as f:
        f.write(base64.b64decode(image_base64))

    # Usa o Tesseract para extrair o texto da imagem
    text = pytesseract.image_to_string('temp.png', lang='por')

    print(text)

    date = None
    value = None

    words = text.split()
    i = 0
    while i < len(words):
        if '/' in words[i]:
            potential_date = words[i]
            if is_valid_date(potential_date):
                date = potential_date
                break
        i += 1

    # Caso a data encontrada não seja válida, continua procurando
    while i < len(words) - 1 and (date is None or not is_valid_date(date)):
        i += 1
        if '/' in words[i]:
            potential_date = words[i]
            if is_valid_date(potential_date):
                date = potential_date

    for word in words:
        if ',' in word:
            try:
                value = float(word.replace(',', '.'))
            except ValueError:
                pass

    # Retorna o resultado da análise em um formato JSON
    if date is not None and value is not None:
        result = {'date': date, 'value': value, 'success': True}
    else:
        result = {'date': None, 'value': None, 'success': False}
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)