import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

from services import database

def render():
    st.subheader("📋 Histórico de Formatações")

    dados = database.listar_formatacoes()

    if not dados:
        st.info("Nenhuma formatação registrada.")
        return


    if st.session_state.get("usuario_tipo") != "admin":
        usuario_nome = st.session_state.get("usuario_nome", "")
        dados = [d for d in dados if d[6] == usuario_nome]

    if not dados:
        st.info("Você não tem formatações registradas.")
        return

    df = pd.DataFrame(dados, columns=[
        "ID", "Lote", "Safra", "Produtor", "Data HVI", "Data Formatação", "Responsável", "Qtd Fardos"
    ])
    st.dataframe(df)

    selecao = st.selectbox("Selecione uma formatação para visualizar os fardos:", df["ID"])

    fardos = database.listar_fardos_por_formatacao(selecao)

    if fardos.empty:
        st.warning("Nenhum fardo encontrado para esta formatação.")
        return


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


    if "UHML" in fardos.columns:
        fardos["UHML_pol"] = fardos["UHML"].apply(converter_uhml)
    else:
        fardos["UHML_pol"] = ""
        
    if "MAT" in fardos.columns:
        fardos["MAT"] = fardos["MAT"].apply(multiplicar_mat)
        
    if "CG" in fardos.columns:
        fardos["CG"] = fardos["CG"].astype(str).str.replace("-", ".")
        
    fardos["PESO"] = ""
    
    if "Tipo" not in fardos.columns:
        fardos["Tipo"] = ""
    

    colunas_export = [
        "Lote", "FardoID", "MIC", "UHML_pol", "STR", "PESO", "SFI", "UI", "CSP",
        "ELG", "Rd", "+b", "TrID", "SCI", "MAT", "CG", "Produtor", "Tipo"
    ]
    
    for col in colunas_export:
        if col not in fardos.columns:
            fardos[col] = ""
    
    export = fardos[colunas_export].rename(columns={
        "MIC": "MICRONAIR", 
        "UHML_pol": "UHML", 
        "STR": "RES", 
        "UI": "UNF", 
        "Rd": "RD", 
        "+b": "+B",
        "TrID": "LEAF"
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