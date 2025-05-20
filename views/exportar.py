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

  
    safras = df["Safra"].unique() if "Safra" in df.columns else []
    produtores = df["Produtor"].unique() if "Produtor" in df.columns else []
    lotes = df["Lote"].unique() if "Lote" in df.columns else []

    safra = st.selectbox("Filtrar por Safra", [""] + sorted(safras))
    produtor = st.selectbox("Filtrar por Produtor", [""] + sorted(produtores))
    lote = st.selectbox("Filtrar por Lote", [""] + sorted(lotes))

    if safra and "Safra" in df.columns:
        df = df[df["Safra"] == safra]
    if produtor and "Produtor" in df.columns:
        df = df[df["Produtor"] == produtor]
    if lote and "Lote" in df.columns:
        df = df[df["Lote"] == lote]

   
    if "UHML" in df.columns:
        df["UHML_pol"] = df["UHML"].apply(lambda v: round(float(v) / 1000 * 39.3701, 2) if str(v).replace(".", "", 1).isdigit() else v)
    else:
        df["UHML_pol"] = ""
        
    if "MAT" in df.columns:
        df["MAT"] = df["MAT"].apply(lambda x: int(round(float(x) * 100)) if str(x).replace(".", "", 1).isdigit() else x)
        
    if "CG" in df.columns:
        df["CG"] = df["CG"].astype(str).str.replace("-", ".")
        
    df["PESO"] = ""
    
    if "Tipo" not in df.columns:
        df["Tipo"] = ""


    colunas_necessarias = [
        "Lote", "FardoID", "MIC", "UHML_pol", "STR", "PESO", "SFI", "UI", 
        "CSP", "ELG", "Rd", "+b", "TrID", "SCI", "MAT", "CG", "Produtor", "Tipo"
    ]
    
    for col in colunas_necessarias:
        if col not in df.columns:
            df[col] = ""

    exportar = df[colunas_necessarias].rename(columns={
        "MIC": "MICRONAIR", 
        "UHML_pol": "UHML", 
        "STR": "RES", 
        "UI": "UNF", 
        "Rd": "RD", 
        "+b": "+B", 
        "TrID": "LEAF"
    })

    st.success(f"{len(exportar)} registros encontrados.")
    st.dataframe(exportar)

    buffer = BytesIO()
    exportar.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    nome = f"Resumo_Banco_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    st.download_button("📁 Baixar Excel com Registros", data=buffer, file_name=nome)