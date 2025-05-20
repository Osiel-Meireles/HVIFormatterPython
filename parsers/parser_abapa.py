import pdfplumber
import re

def parse_abapa(pdf_file):
    """
    Parser específico para laudos de algodão da ABAPA (Laboratório de Análise de Fibra do Algodão)
    """
    dados = []
    
    # Metadados do laudo
    metadados = {
        "lote": "Desconhecido",
        "cliente": "Desconhecido",
        "fazenda": "Desconhecida",
        "usina": "Desconhecida",
        "safra": "Desconhecida",
        "data_hvi": "Desconhecida",
        "municipio": "Desconhecido",
        "produto": "Desconhecido"
    }

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            linhas = texto.split("\n")

            # Extrair metadados do cabeçalho
            for linha in linhas:
                if "Cliente:" in linha:
                    partes = linha.split("Cliente:")
                    if len(partes) > 1:
                        metadados["cliente"] = partes[1].strip().split("Lote:")[0].strip()
                
                if "Lote:" in linha:
                    partes = linha.split("Lote:")
                    if len(partes) > 1:
                        metadados["lote"] = partes[1].strip().split()[0]
                
                if "Fazenda:" in linha:
                    partes = linha.split("Fazenda:")
                    if len(partes) > 1:
                        metadados["fazenda"] = partes[1].strip().split("Data:")[0].strip()
                
                if "Data:" in linha:
                    partes = linha.split("Data:")
                    if len(partes) > 1:
                        metadados["data_hvi"] = partes[1].strip()
                
                if "Usina:" in linha:
                    partes = linha.split("Usina:")
                    if len(partes) > 1:
                        metadados["usina"] = partes[1].strip().split("Município:")[0].strip()
                
                if "Município:" in linha:
                    partes = linha.split("Município:")
                    if len(partes) > 1:
                        metadados["municipio"] = partes[1].strip()
                
                if "Safra:" in linha:
                    partes = linha.split("Safra:")
                    if len(partes) > 1:
                        metadados["safra"] = partes[1].strip().split("Latitude:")[0].strip()
                
                if "Produto:" in linha:
                    partes = linha.split("Produto:")
                    if len(partes) > 1:
                        metadados["produto"] = partes[1].strip().split("Longitude:")[0].strip()

            # Extrair dados dos fardos
            for i, linha in enumerate(linhas):
                # Padrão de identificação de linha de fardo
                if re.match(r'00\.0\.\d+\.\d+\.\d+\.\d+', linha):
                    # Obter o ID do fardo na primeira linha
                    fardo_id = linha.strip()
                    
                    # A próxima linha contém todos os dados do fardo
                    if i+1 < len(linhas):
                        dados_fardo = linhas[i+1].strip().replace(",", ".")
                        valores = dados_fardo.split()
                        
                        # Verificar se temos dados suficientes (todos os campos esperados)
                        if len(valores) >= 17:  # Todos os campos necessários do fardo
                            # Criar um registro completo com metadados e dados do fardo
                            registro = {
                                "Lote": metadados["lote"],
                                "FardoID": fardo_id,
                                "UHML_mm": valores[0],
                                "UHML_pol": valores[1],
                                "UI": valores[2],
                                "SFI": valores[3],
                                "STR": valores[4],
                                "ELG": valores[5],
                                "MIC": valores[6],
                                "Mat": valores[7],
                                "Rd": valores[8],
                                "+b": valores[9],
                                "CGrd": valores[10],
                                "TrCnt": valores[11],
                                "TrAr": valores[12],
                                "TrID": valores[13],
                                "SCI": valores[14],
                                "CSP": valores[15],
                                "Cliente": metadados["cliente"],
                                "Fazenda": metadados["fazenda"],
                                "Usina": metadados["usina"],
                                "Safra": metadados["safra"],
                                "Municipio": metadados["municipio"],
                                "Produto": metadados["produto"],
                                "Data_HVI": metadados["data_hvi"]
                            }
                            dados.append(registro)

    # Definir colunas na ordem desejada
    colunas = [
        "Lote", "FardoID", "UHML_mm", "UHML_pol", "UI", "SFI", "STR", "ELG", "MIC", "Mat",
        "Rd", "+b", "CGrd", "TrCnt", "TrAr", "TrID", "SCI", "CSP", 
        "Cliente", "Fazenda", "Usina", "Safra", "Municipio", "Produto", "Data_HVI"
    ]

    return dados, colunas, metadados

# Exemplo de uso:
# dados, colunas, metadados = parse_abapa("Laudo-Lote_258.pdf")