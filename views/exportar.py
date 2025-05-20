import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from services.database import consultar_registros_completos

def render():
    st.subheader("📤 Exportar Dados do Banco")

    df = consultar_registros_completos()

    if df.empty:
        st.info("Ainda não há registros salvos.")
        return

    safra = st.selectbox("Filtrar por Safra", [""] + sorted(df["Safra"].unique()))
    produtor = st.selectbox("Filtrar por Produtor", [""] + sorted(df["Produtor"].unique()))
    lote = st.selectbox("Filtrar por Lote", [""] + sorted(df["LOTE"].unique()))

    if safra:
        df = df[df["Safra"] == safra]
    if produtor:
        df = df[df["Produtor"] == produtor]
    if lote:
        df = df[df["LOTE"] == lote]

    df["UHML"] = df["UHML_mm"].apply(lambda v: round(float(v) / 1000 * 39.3701, 2) if str(v).replace(".", "", 1).isdigit() else v)
    df["MAT"] = df["MAT"].apply(lambda x: int(round(float(x) * 100)) if str(x).replace(".", "", 1).isdigit() else x)
    df["CG"] = df["CG"].astype(str).str.replace("-", ".")
    df["PESO"] = ""
    df["Tipo"] = ""

    exportar = df[[
        "LOTE", "FARDO", "MICRONAIR", "UHML", "RES", "PESO", "SFI", "UNF",
        "CSP", "ELG", "RD", "+B", "LEAF", "SCI", "MAT", "CG", "Produtor", "Tipo"
    ]]

    st.success(f"{len(exportar)} registros encontrados.")
    st.dataframe(exportar)

    buffer = BytesIO()
    exportar.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    nome = f"Resumo_Banco_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    st.download_button("📁 Baixar Excel com Registros", data=buffer, file_name=nome)