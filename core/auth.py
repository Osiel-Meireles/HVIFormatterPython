import streamlit as st
import sqlite3
import bcrypt
from streamlit_cookies_manager import EncryptedCookieManager
from dotenv import load_dotenv
import os

# Configuração inicial
load_dotenv()
cookies = EncryptedCookieManager(prefix="sifhvi_", password=os.getenv("COOKIE_PASSWORD"))

# Funções auxiliares
def autenticar_usuario(email, senha):
    conn = sqlite3.connect("laudos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, senha_hash, tipo, regiao, senha_temporaria FROM usuarios WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.checkpw(senha.encode(), user[2].encode()):
        return {
            "id": user[0],
            "nome": user[1],
            "tipo": user[3],
            "regiao": user[4],
            "senha_temporaria": bool(user[5])
        }
    return None

def atualizar_senha(usuario_id, nova_senha):
    conn = sqlite3.connect("laudos.db")
    cursor = conn.cursor()
    senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
    cursor.execute("UPDATE usuarios SET senha_hash = ?, senha_temporaria = 0 WHERE id = ?", (senha_hash, usuario_id))
    conn.commit()
    conn.close()

def login():
    try:
        cookies_ready = cookies._cookie_manager is not None
    except:
        cookies_ready = False

    if cookies_ready:
        if cookies.get("usuario_id") and not st.session_state.get("usuario_autenticado"):
            st.session_state.usuario_autenticado = True
            st.session_state.usuario_id = int(cookies.get("usuario_id"))
            st.session_state.usuario_nome = cookies.get("usuario_nome")
            st.session_state.usuario_tipo = cookies.get("usuario_tipo")
            st.session_state.usuario_regiao = cookies.get("usuario_regiao")
            st.session_state.senha_temporaria = False

    if "usuario_autenticado" not in st.session_state:
        st.session_state.usuario_autenticado = False

    if not st.session_state.usuario_autenticado:
        st.markdown("<h3 style='text-align: center;'>Plataforma SIFHVI</h3>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center;'>Faça login para acessar</h5>", unsafe_allow_html=True)
        with st.container():
            with st.form("login_form", clear_on_submit=True):
                email = st.text_input("Email")
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar"):
                    usuario = autenticar_usuario(email, senha)
                    if usuario:
                        st.session_state.usuario_autenticado = True
                        st.session_state.usuario_id = usuario["id"]
                        st.session_state.usuario_nome = usuario["nome"]
                        st.session_state.usuario_tipo = usuario["tipo"]
                        st.session_state.usuario_regiao = usuario["regiao"]
                        st.session_state.senha_temporaria = usuario["senha_temporaria"]
                        cookies["usuario_id"] = str(usuario["id"])
                        cookies["usuario_nome"] = usuario["nome"]
                        cookies["usuario_tipo"] = usuario["tipo"]
                        cookies["usuario_regiao"] = usuario["regiao"]
                        cookies.save()
                        st.rerun()
                    else:
                        st.error("Email ou senha incorretos.")
        return False

    elif st.session_state.senha_temporaria:
        st.warning("Você está usando uma senha temporária. Altere-a para continuar.")
        with st.form("trocar_senha_form"):
            nova = st.text_input("Nova senha", type="password")
            confirmar = st.text_input("Confirmar nova senha", type="password")
            if st.form_submit_button("Atualizar senha"):
                if nova != confirmar:
                    st.error("As senhas não coincidem.")
                elif len(nova) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                else:
                    atualizar_senha(st.session_state.usuario_id, nova)
                    st.session_state.senha_temporaria = False
                    st.success("Senha atualizada com sucesso!")
                    st.rerun()
        return False

    return True
