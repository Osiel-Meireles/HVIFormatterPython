import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import importlib

from services import database

# Dicionário de modelos disponíveis
MODELOS_PARSERS = {
    "Abapa": "parser_abapa",
    "CottonMax": "parser_cottonmax",  # futuro parser
}

def render():
    st.subheader("📄 Processar Laudos HVI")

    modelo_escolhido = st.selectbox("Selecione o modelo do laudo:", list(MODELOS_PARSERS.keys()))
    arquivos = st.file_uploader("Envie os PDFs", type=["pdf"], accept_multiple_files=True)
    produtor = st.text_input("Nome do produtor")
    corretora = st.text_input("Nome da corretora")
    iniciar = st.button("🚀 Iniciar Processamento")

    if iniciar and arquivos and produtor and corretora:
        with st.spinner("Processando arquivos..."):
            df_final = pd.DataFrame()

            try:
                parser_module = importlib.import_module(f"parsers.{MODELOS_PARSERS[modelo_escolhido]}")
            except ModuleNotFoundError:
                st.error(f"Parser para o modelo '{modelo_escolhido}' não encontrado.")
                return

            for arq in arquivos:
                dados, colunas, lote, safra, data_hvi = parser_module.parse_modelo(arq)

                if not dados:
                    st.warning(f"{arq.name}: Nenhum dado encontrado.")
                    continue

                df = pd.DataFrame(dados, columns=colunas)
                df["Produtor"] = produtor

                id_fmt = database.inserir_formatacao(
                    lote=lote,
                    data_hvi=data_hvi,
                    safra=safra,
                    produtor=produtor,
                    responsavel=st.session_state.usuario_nome
                )
                database.inserir_fardos(id_fmt, df, st.session_state.usuario_nome)
                df_final = pd.concat([df_final, df], ignore_index=True)

            if df_final.empty:
                st.error("Nenhum dado foi processado.")
                return

            # Conversões e ajustes
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

            df_final["UHML"] = df_final["UHML_mm"].apply(mm_para_pol)
            df_final["MAT"] = df_final["MAT"].apply(multiplicar_mat)
            df_final["CG"] = df_final["CG"].astype(str).str.replace("-", ".")
            df_final["FardoID"] = df_final["FardoID"].astype(str).str.replace(".", "")
            df_final["PESO"] = ""
            df_final["Tipo"] = ""

            export = df_final[[
                "Lote", "FardoID", "MIC", "UHML", "STR", "PESO", "SFI", "UI", "CSP",
                "ELG", "Rd", "+b", "TrID", "SCI", "MAT", "CG", "Produtor", "Tipo"
            ]].rename(columns={
                "MIC": "MICRONAIR", "STR": "RES", "UI": "UNF", "Rd": "RD", "+b": "+B"
            })

            buffer = BytesIO()
            export.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            nome_arquivo = f"Resumo_Oferta_{datetime.now().strftime('%Y-%m-%d')}_{produtor}_{corretora}.xlsx".replace(" ", "_")
            st.success(f"{len(export)} fardos processados com sucesso.")
            st.download_button("📥 Baixar Excel Consolidado", data=buffer, file_name=nome_arquivo)
