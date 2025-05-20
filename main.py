import streamlit as st
st.set_page_config(page_title="SIFHVI", layout="wide")

from core import auth
from views import processar, historico, admin, exportar

# Realiza login
if not auth.login():
    st.stop()

# Menu lateral
st.sidebar.title("Menu")
st.sidebar.markdown(f"**Usuário:** {st.session_state.usuario_nome}")

if st.sidebar.button("Sair"):
    st.session_state.clear()
    auth.cookies.clear()
    st.rerun()

# Navegação
opcoes = ["Processar PDF", "Histórico de Formatações"]
if st.session_state.usuario_tipo == "admin":
    opcoes.append("Painel Administrativo")
    opcoes.append("Exportar do Banco")

escolha = st.sidebar.radio("Escolha uma opção:", opcoes)

if escolha == "Processar PDF":
    processar.render()
elif escolha == "Histórico de Formatações":
    historico.render()
elif escolha == "Painel Administrativo":
    admin.render()
elif escolha == "Exportar do Banco":
    exportar.render()
