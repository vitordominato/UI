import streamlit as st

st.set_page_config(page_title="Gestão Hospitalar", layout="wide")

st.sidebar.title("Menu")
page = st.sidebar.radio("", ["Painel de Leitos", "Admissão"])

if page == "Painel de Leitos":
    import pages._1_leitos as leitos
    leitos.app()
elif page == "Admissão":
    import pages._2_admissao as adm
    adm.app()
