import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

from services import database

def render():
    st.subheader("📋 Histórico de Formatações")

    dados = database.listar_formatacoes()

    if st.session_state.usuario_tipo != "admin":
        dados = [d for d in dados if d[7] == st.session_state.usuario_nome]

    if not dados:
        st.info("Nenhuma formatação registrada.")
        return

    df = pd.DataFrame(dados, columns=[
        "ID", "Lote", "Safra", "Produtor", "Data HVI", "Data Formatação", "Qtd Fardos", "Responsável"
    ])
    st.dataframe(df)

    selecao = st.selectbox("Selecione uma formatação para visualizar os fardos:", df["ID"])

    fardos = database.listar_fardos_por_formatacao(selecao)

    if fardos.empty:
        st.warning("Nenhum fardo encontrado para esta formatação.")
        return

    # Formatar colunas numéricas
    def converter_uhml(valor):
        try:
            return round((float(valor) / 1000) * 39.3701, 2)
        except:
            return "-"

    def multiplicar_mat(valor):
        try:
            return int(round(float(valor) * 100))
        except:
            return valor

    fardos["UHML"] = fardos["UHML_mm"].apply(converter_uhml)
    fardos["MAT"] = fardos["MAT"].apply(multiplicar_mat)
    fardos["CG"] = fardos["CG"].astype(str).str.replace("-", ".")
    fardos["PESO"] = ""
    fardos["Tipo"] = ""

    export = fardos[[
        "Lote", "FardoID", "MIC", "UHML", "STR", "PESO", "SFI", "UI", "CSP",
        "ELG", "Rd", "+b", "TrID", "SCI", "MAT", "CG", "Produtor", "Tipo"
    ]].rename(columns={
        "MIC": "MICRONAIR", "STR": "RES", "UI": "UNF", "Rd": "RD", "+b": "+B"
    })

    st.success(f"{len(export)} fardos encontrados.")
    st.dataframe(export)

    buffer = BytesIO()
    export.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    nome_excel = f"Resumo_Formatação_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

    st.download_button(
        label="📁 Baixar Excel",
        data=buffer,
        file_name=nome_excel,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
