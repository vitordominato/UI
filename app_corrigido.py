
import streamlit as st

# Simulação de variável de controle
if "editando" not in st.session_state:
    st.session_state.editando = True

st.title("Painel de Leitos")

if st.session_state.editando:
    with st.form("formulario"):
        st.text_input("Nome do paciente")
        voltar = st.form_submit_button("🔙 Voltar")
        if voltar:
            st.session_state.editando = None
            st.experimental_rerun()
else:
    st.write("Lista de leitos será exibida aqui.")
