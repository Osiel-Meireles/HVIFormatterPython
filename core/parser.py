import pdfplumber

def identificar_modelo(texto):
    if "BENEFICIADORA ELIANE" in texto.upper():
        return "BENEFICIADORA_ELIANE"
    elif "COTTON MAX" in texto.upper():
        return "COTTON_MAX"
    else:
        return "DESCONHECIDO"

def extrair_dados(pdf):
    dados_completos = []
    info_geral = []

    for page in pdf.pages:
        texto = page.extract_text()
        modelo = identificar_modelo(texto)

        lote, safra, data_hvi = "Desconhecido", "Desconhecida", "Desconhecida"
        linhas = texto.split("\n")

        for linha in linhas:
            if "LOTE:" in linha.upper():
                try:
                    lote = linha.upper().split("LOTE:")[1].strip().split()[0]
                except: pass
            if "SAFRA:" in linha.upper():
                try:
                    safra = linha.upper().split("SAFRA:")[1].strip().split()[0]
                except: pass
            if "DATA:" in linha.upper():
                try:
                    data_hvi = linha.upper().split("DATA:")[1].strip().split()[0]
                except: pass

        for linha in linhas:
            if linha.startswith("00.0."):
                partes = linha.replace(",", ".").split()
                partes.insert(0, lote)  # Adiciona o número do lote na frente
                dados_completos.append(partes)

        info_geral.append({
            "modelo": modelo,
            "lote": lote,
            "safra": safra,
            "data_hvi": data_hvi
        })

    return dados_completos, info_geral[-1] if info_geral else {}
