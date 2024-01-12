from flask import Flask, request, jsonify
import pytesseract
import base64
import spacy
from dateparser import parse as parse_date

app = Flask(__name__)

# Carrega o modelo de processamento de linguagem natural do spaCy para português
nlp = spacy.load("pt_core_news_sm")


def is_valid_date(candidate):
    try:
        parsed_date = parse_date(candidate, languages=['pt'])
        if parsed_date:
            return True
        else:
            return False
    except ValueError:
        return False


def extract_names(text):
    # Processa o texto usando spaCy
    doc = nlp(text)

    names = []

    # Itera sobre as entidades identificadas pelo spaCy
    for ent in doc.ents:
        if ent.label_ == "PERSON" or ent.label_ == "ORG":
            # Adiciona o nome ou instituição à lista
            names.append(ent.text)

    return names


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
    origin = None
    destiny = None

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

    # Extrai nomes de pessoas ou instituições
    names = extract_names(text)

    # Define "destiny" como o primeiro nome/instituição e "origin" como o segundo
    if len(names) >= 2:
        destiny = names[0]
        origin = names[1]

    for word in words:
        if ',' in word:
            try:
                value = float(word.replace(',', '.'))
            except ValueError:
                pass

    # Retorna o resultado da análise em um formato JSON
    result = {'date': date, 'value': value, 'success': True, 'origin': origin, 'destiny': destiny}
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)