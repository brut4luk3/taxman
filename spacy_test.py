import spacy
import re
from dateparser import parse as parse_date

# Carregar o modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

# Verifica se a data é válida
def is_valid_date(candidate):
    try:
        parsed_date = parse_date(candidate, languages=['pt'])
        return parsed_date is not None
    except ValueError:
        return False

# Função para extrair informações
def extract_info(text):
    # Usar Tesseract e spaCy para processar o texto
    doc = nlp(text)

    # Encontrar data
    words = text.split()
    date = None
    for word in words:
        if '/' in word and is_valid_date(word):
            date = word
            break

    # Encontrar valor
    value_match = re.search(r'R\$\s?\d+(?:\.\d{3})*,\d{2}', text)
    value = value_match.group() if value_match else None

    # Encontrar nomes (foco em remetente e destinatário)
    names = re.findall(r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)+', text)

    # Filtrar nomes irrelevantes
    filtered_names = [name for name in names if not any(sub in name for sub in ["Nome", "CPF", "CNPJ", "Instituição", "Banco", "Agência", "Conta", "Destino", "Origem"])]

    # Supondo que os primeiros dois nomes relevantes são o destinatário e o remetente
    # Isso pode precisar de ajustes dependendo da estrutura dos seus textos
    if len(filtered_names) >= 2:
        destinatario = filtered_names[0]
        remetente = filtered_names[1]
    else:
        destinatario, remetente = None, None

    return {
        "date": date,
        "value": value,
        "destinatario": destinatario,
        "remetente": remetente
    }

# Testando com seus textos
texts = ["NU\r\n\r\nComprovante de\r\n\r\ntransfer\u00EAncia\r\n\r\n09\/12\/2023 - 18:29:54\r\n\r\nValor\r\n\r\nTipo de transfer\u00EAncia\r\n\r\nLg Destino\r\nNome\r\n\r\nCPF\r\nInstitui\u00E7\u00E3o\r\n\r\nTipo de conta\r\n\r\nLj Origem\r\nNome\r\nInstitui\u00E7\u00E3o\r\nAg\u00EAncia\r\nConta\r\n\r\nCPF\r\n\r\nR$312,00\r\n\r\nPix\r\n\r\nSTEFANY BUKOVITZ\r\n\r\n+, 184.059-+\r\n\r\nBCO DO BRASIL S.A.\r\n\r\nConta corrente\r\n\r\nIsadora Dyck\r\n\r\nNU PAGAMENTOS - IP\r\n\r\n0001\r\n\r\n27582598-3\r\n\r\n\u00ABee. 808.739-+\r\n\r\nNu Pagamentos S.A. - Institui\u00E7\u00E3o de Pagamento\r\n\r\nCNP) 18.236.120\/0001-58\r\n\r\nID da transa\u00E7\u00E3o:\r\n\r\nE18236120202312092129s50002b0b445\r\n\r\nEstamos aqui para ajudar se voc\u00EA tiver alguma\r\n\r\nd\u00FAvida.\r\n\r\nMe ajuda \u2014\r\n\r\nOuvidoria: 0800 887 0463, atendimento em dias\r\n\u00DAteis, das 09h \u00E0s 18h (hor\u00E1rio de S\u00E3o Paulo).", "inter\r\n\r\nPix enviado\r\nRS 400,00\r\n\r\nSobre a transa\u00E7\u00E3o\r\nData do pagamento Domingo, 10\/12\/2023\r\nHor\u00E1rio 21h32\r\n\r\nID da transa\u00E7\u00E3o\r\nE00416968202312110032ucadOhyIQxJ\r\n\r\nQuem recebeu\r\n\r\nNome Escola de Educacao Infantil Encantar\r\nCPF\/CNPJ 42.955.382\/0001-57\r\nInstitui\u00E7\u00E3o Coop Viacredi\r\n\r\nQuem pagou\r\nNome STEFANY BUKOVITZ 09018405990\r\nCPF\/CNPJ 36.532.156\/0001-60\r\n\r\nInstitui\u00E7\u00E3o Banco Inter S.A.", "pagamento realizado\r\n\r\nQ *s 207,00\r\n\r\nvalor pago via boleto\r\n\r\npara\r\n\r\nE> Associacao Desportiva Hering\r\ncnpj: 82.662.909\/0001-70\r\n\r\nde\r\n\r\nLucas Gabriel Reinert\r\n\r\n341 Ita\u00FA Unibanco S\/A - 9247 | 47705 - 3\r\ncpf: 050.665.059-62\r\n\r\nmensagem\r\nboletos\/t\u00EDtulos\r\n\r\n$= realizado em\r\n\r\n*\u201D 10\/12\/2023 \u00E0s 21:21:15\r\n\r\nvia\r\n\r\nApp Ita\u00FA\r\n\r\n| ver comprovante |\r\n\r\ncompartilhar"]
for text in texts:
    print(extract_info(text))