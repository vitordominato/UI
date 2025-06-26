# firebase_utils.py

import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

firebase_initialized = False

def inicializar_firebase():
    """Inicializa o Firebase, garantindo que seja chamado apenas uma vez."""
    global firebase_initialized
    if firebase_initialized:
        return
    fb = st.secrets["FIREBASE"]
    cred = credentials.Certificate({
        "type": fb["type"],
        "project_id": fb["project_id"],
        "private_key_id": fb["private_key_id"],
        "private_key": fb["private_key"],
        "client_email": fb["client_email"],
        "client_id": fb["client_id"],
        "auth_uri": fb["auth_uri"],
        "token_uri": fb["token_uri"],
        "auth_provider_x509_cert_url": fb["auth_provider_x509_cert_url"],
        "client_x509_cert_url": fb["client_x509_cert_url"],
        "universe_domain": fb.get("universe_domain", "googleapis.com"),
    })
    database_url = st.secrets["DATABASE_URL_CONFIG"]["value"]
    firebase_admin.initialize_app(cred, {"databaseURL": database_url})
    firebase_initialized = True

def obter_leitos():
    """Retorna uma lista de leitos com dados gerais."""
    inicializar_firebase()
    ref = db.reference('leitos')
    data = ref.get()
    return [{**{"leito": k}, **v} for k, v in data.items()] if data else []

def salvar_leito(leito_id, dados: dict):
    """Grava ou atualiza dados do leito."""
    inicializar_firebase()
    ref = db.reference(f'leitos/{leito_id}')
    ref.set(dados)

def obter_ficha_clinica(leito_id):
    """Retorna a ficha clínica do leito, se houver."""
    inicializar_firebase()
    ref = db.reference(f'fichas_clinicas/{leito_id}')
    return ref.get() or {}

def salvar_ficha_clinica(leito_id, dados: dict):
    """Salva ou atualiza a ficha clínica do leito."""
    inicializar_firebase()
    ref = db.reference(f'fichas_clinicas/{leito_id}')
    ref.set(dados)

def limpar_ficha_clinica(leito_id):
    """Apaga a ficha clínica (botão Alta)."""
    inicializar_firebase()
    db.reference(f'fichas_clinicas/{leito_id}').delete()
