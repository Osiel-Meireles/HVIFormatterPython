import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import importlib
import time

from services import database


MODELOS_PARSERS = {
    "Abapa": "parser_abapa",
    "CottonMax": "parser_cottonmax",
}

def render():
    st.subheader("📄 Processar Laudos HVI")

    modelo_escolhido = st.selectbox("Selecione o modelo do laudo:", list(MODELOS_PARSERS.keys()))
    arquivos = st.file_uploader("Envie os PDFs", type=["pdf"], accept_multiple_files=True)
    produtor = st.text_input("Nome do produtor")
    corretora = st.text_input("Nome da corretora")
    
    # Opção de debug para ajudar na solução de problemas
    mostrar_debug = st.checkbox("Mostrar informações de debug", value=False)
    
    iniciar = st.button("🚀 Iniciar Processamento")

    if iniciar and arquivos and produtor and corretora:
        with st.spinner("Processando arquivos..."):
            df_final = pd.DataFrame()

            try:
                parser_module = importlib.import_module(f"parsers.{MODELOS_PARSERS[modelo_escolhido]}")
                if mostrar_debug:
                    st.write(f"Parser carregado: {MODELOS_PARSERS[modelo_escolhido]}")
            except ModuleNotFoundError:
                st.error(f"Parser para o modelo '{modelo_escolhido}' não encontrado.")
                return
            except Exception as e:
                st.error(f"Erro ao carregar o parser: {str(e)}")
                return

            for arq in arquivos:
                try:
                    # Mostrar informações do arquivo
                    if mostrar_debug:
                        st.write(f"Processando arquivo: {arq.name}")
                        st.write(f"Tamanho do arquivo: {arq.size} bytes")
                    
                    # Garantir que o arquivo está no início antes de processar
                    arq.seek(0)
                    
                    # Processar o arquivo com o parser
                    dados, colunas, lote, safra, data_hvi = parser_module.parse_modelo(arq)
                    
                    # Mostrar informações obtidas do parser
                    if mostrar_debug:
                        st.write(f"Lote: {lote}")
                        st.write(f"Safra: {safra}")
                        st.write(f"Data HVI: {data_hvi}")
                        st.write(f"Quantidade de dados encontrados: {len(dados)}")
                        if len(dados) > 0:
                            st.write("Exemplo de dados:")
                            st.write(dados[0])

                    if not dados:
                        st.warning(f"{arq.name}: Nenhum dado encontrado.")
                        continue

                    df = pd.DataFrame(dados, columns=colunas)
                    df["Produtor"] = produtor
                    df["Tipo"] = ""  

                    # Se debug estiver ativado, mostrar o DataFrame antes de inserir no banco
                    if mostrar_debug:
                        st.write("DataFrame criado:")
                        st.write(df.head())

                    id_fmt = database.inserir_formatacao(
                        lote=lote,
                        data_hvi=data_hvi,
                        safra=safra,
                        produtor=produtor,
                        responsavel=st.session_state.usuario_nome
                    )
                    
                    if mostrar_debug:
                        st.write(f"ID da formatação criada: {id_fmt}")
                        
                    database.inserir_fardos(id_fmt, df, st.session_state.usuario_nome)
                    df_final = pd.concat([df_final, df], ignore_index=True)
                
                except Exception as e:
                    st.error(f"Erro ao processar {arq.name}: {str(e)}")
                    if mostrar_debug:
                        import traceback
                        st.code(traceback.format_exc())

            if df_final.empty:
                st.error("Nenhum dado foi processado.")
                return

            def mm_para_pol(valor):
                try:
                    return round((float(valor) / 1000) * 39.3701, 2)
                except:
                    return "-"

            def multiplicar_mat(valor):
                try:
                    return int(round(float(valor) * 100))
                except:
                    return valor

           
            if "UHML" in df_final.columns:
                df_final["UHML_pol"] = df_final["UHML"].apply(mm_para_pol)
            
            if "MAT" in df_final.columns:
                df_final["MAT"] = df_final["MAT"].apply(multiplicar_mat)
                
            if "CG" in df_final.columns:
                df_final["CG"] = df_final["CG"].astype(str).str.replace("-", ".")
                
            if "FardoID" in df_final.columns:
                df_final["FardoID"] = df_final["FardoID"].astype(str).str.replace(".", "")
                
            df_final["PESO"] = ""

           
            colunas_export = [
                "Lote", "FardoID", "MIC", "UHML", "STR", "PESO", "SFI", "UI", "CSP",
                "ELG", "Rd", "+b", "TrID", "SCI", "MAT", "CG", "Produtor", "Tipo"
            ]
            
         
            for col in colunas_export:
                if col not in df_final.columns:
                    df_final[col] = ""

            export = df_final[colunas_export].rename(columns={
                "MIC": "MICRONAIR", "STR": "RES", "UI": "UNF", "Rd": "RD", "+b": "+B"
            })

            # Se debug estiver ativado, mostrar o DataFrame final
            if mostrar_debug:
                st.write("DataFrame para exportação:")
                st.write(export.head())

            buffer = BytesIO()
            export.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            nome_arquivo = f"Resumo_Oferta_{datetime.now().strftime('%Y-%m-%d')}_{produtor}_{corretora}.xlsx".replace(" ", "_")
            st.success(f"{len(export)} fardos processados com sucesso.")
            st.download_button("📥 Baixar Excel Consolidado", data=buffer, file_name=nome_arquivo)