import pdfplumber

def parse_modelo(pdf_file):
    dados = []
    lote = "Desconhecido"
    safra = "Desconhecida"
    data_hvi = "Desconhecida"

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            linhas = texto.split("\n")

            for linha in linhas:
                if "Lote:" in linha:
                    partes = linha.split("Lote:")
                    if len(partes) > 1:
                        lote = partes[1].strip().split()[0]
                if "Safra:" in linha:
                    partes = linha.split("Safra:")
                    if len(partes) > 1:
                        safra = partes[1].strip().split()[0]
                if "Data:" in linha:
                    partes = linha.split("Data:")
                    if len(partes) > 1:
                        data_hvi = partes[1].strip().split()[0]

            for linha in linhas:
                if linha.startswith("00.0."):
                    linha_formatada = linha.replace(",", ".")
                    partes = linha_formatada.split()
                    if len(partes) >= 18: 
                        partes[0] = partes[0].replace(".", "")
                        partes.insert(0, lote)
                        dados.append(partes[:19])

    colunas = [
        "Lote", "FardoID", "UHML", "UHML_pol", "UI", "SFI", "STR", "ELG", "MIC", "MAT",
        "Rd", "+b", "CG", "TrCnt", "TrAr", "TrID", "SCI", "CSP", "Produtor"
    ]

    return dados, colunas, lote, safra, data_hvi