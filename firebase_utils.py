
import firebase_admin
from firebase_admin import credentials, db
import os
import streamlit as st
import json

firebase_initialized = False

def inicializar_firebase():
    global firebase_initialized
    if not firebase_initialized:
        try:
            print("\n===== DEBUG INICIALIZAR FIREBASE =====")
            print("Chaves disponíveis em st.secrets:", list(st.secrets.keys()))
            fb = st.secrets["FIREBASE"]
            print("Tipo de st.secrets['FIREBASE']:", type(fb))
            print("Campos disponíveis em st.secrets['FIREBASE']:", list(fb.keys()))
            # Monta o dict esperado pelo credentials.Certificate
            firebase_secret = {
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
            }
            print("Campos presentes em firebase_secret:", list(firebase_secret.keys()))
            pk = firebase_secret.get('private_key', '')
            print(f"Início da private_key: {pk[:40]}")
            print(f"...Fim da private_key: {pk[-40:]}")
            print(f"Tamanho da private_key: {len(pk)}")
            cred = credentials.Certificate(firebase_secret)
            # DATABASE_URL_CONFIG sempre é um dict com 'value' no Streamlit Cloud
            database_url = st.secrets["DATABASE_URL_CONFIG"]["value"]
            print("DEBUG: database_url =", database_url)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            firebase_initialized = True
            print("DEBUG: Firebase inicializado com sucesso!\n")
        except Exception as e:
            print("===== ERRO AO INICIALIZAR FIREBASE =====")
            import traceback
            traceback.print_exc()
            print("Valor bruto de st.secrets['FIREBASE']:", repr(st.secrets.get('FIREBASE')))
            raise

# --- LEITOS ---
def salvar_leito(leito_id, dados):
    """Salva ou atualiza um leito no Firebase."""
    try:
        inicializar_firebase()
        ref = db.reference(f'leitos/{leito_id}')
        ref.set(dados)
    except Exception as e:
        print(f"Erro ao salvar leito: {e}")

def salvar_ficha_clinica(leito_id, dados):
    """Salva ou atualiza a ficha clínica de um leito no Firebase."""
    try:
        inicializar_firebase()
        ref = db.reference(f'fichas_clinicas/{leito_id}')
        ref.set(dados)
    except Exception as e:
        print(f"Erro ao salvar ficha clínica: {e}")

def obter_ficha_clinica(leito_id):
    """Obtém a ficha clínica de um leito no Firebase."""
    try:
        inicializar_firebase()
        ref = db.reference(f'fichas_clinicas/{leito_id}')
        return ref.get() or {}
    except Exception as e:
        print(f"Erro ao obter ficha clínica: {e}")
        return {}

def obter_leitos():
    inicializar_firebase()
    ref = db.reference('leitos')
    data = ref.get()
    if data:
        return [{**{'leito': k}, **v} for k, v in data.items()]
    return []

# --- MÉDICOS ---
def salvar_medico(medico_id, dados):
    inicializar_firebase()
    ref = db.reference(f'medicos/{medico_id}')
    ref.set(dados)

def excluir_medico(medico_id):
    inicializar_firebase()
    ref = db.reference(f'medicos/{medico_id}')
    ref.delete()

def obter_medicos():
    inicializar_firebase()
    ref = db.reference('medicos')
    data = ref.get()
    if data:
        return [{**{'medico_id': k}, **v} for k, v in data.items()]
    return []

# --- ADMISSÕES ---
def salvar_admissao(admissao_id, dados):
    inicializar_firebase()
    ref = db.reference(f'admissoes/{admissao_id}')
    ref.set(dados)

def excluir_admissao(admissao_id):
    inicializar_firebase()
    ref = db.reference(f'admissoes/{admissao_id}')
    ref.delete()

def obter_admissoes():
    inicializar_firebase()
    ref = db.reference('admissoes')
    data = ref.get()
    if data:
        return [{**{'admissao_id': k}, **v} for k, v in data.items()]
    return []

# --- ADMITIDOS ---
def salvar_admitido(admitido_id, dados):
    inicializar_firebase()
    ref = db.reference(f'admitidos/{admitido_id}')
    ref.set(dados)

def obter_admitidos():
    inicializar_firebase()
    ref = db.reference('admitidos')
    data = ref.get()
    if data:
        return [{**{'admitido_id': k}, **v} for k, v in data.items()]
    return []

# --- HISTÓRICO DE ADMISSÕES ---
def salvar_historico_admissao(hist_id, dados):
    inicializar_firebase()
    ref = db.reference(f'historico_admissoes/{hist_id}')
    ref.set(dados)

def obter_historico_admissoes():
    inicializar_firebase()
    ref = db.reference('historico_admissoes')
    data = ref.get()
    if data:
        return [{**{'hist_id': k}, **v} for k, v in data.items()]
    return []
