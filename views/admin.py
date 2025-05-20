import streamlit as st
import sqlite3
import pandas as pd
import bcrypt
import secrets

def render():
    st.subheader("👤 Painel de Administração de Usuários")

    conn = sqlite3.connect("laudos.db")
    cursor = conn.cursor()

    with st.form("novo_user"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        tipo = st.selectbox("Tipo", ["admin", "usuario"])
        regiao = st.selectbox("Região", ["MT", "BA"])
        cadastrar = st.form_submit_button("Cadastrar Usuário")

        if cadastrar:
            senha_temp = secrets.token_urlsafe(8)
            senha_hash = bcrypt.hashpw(senha_temp.encode(), bcrypt.gensalt()).decode()
            try:
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha_hash, tipo, regiao, senha_temporaria)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (nome, email, senha_hash, tipo, regiao))
                conn.commit()
                st.success(f"Usuário {nome} criado com sucesso! Senha temporária: {senha_temp}")
            except sqlite3.IntegrityError:
                st.error("Este e-mail já está cadastrado.")

    cursor.execute("SELECT id, nome, email, tipo, regiao FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    st.dataframe(pd.DataFrame(usuarios, columns=["ID", "Nome", "Email", "Tipo", "Região"]))
