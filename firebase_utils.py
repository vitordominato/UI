
import firebase_admin
from firebase_admin import credentials, db
import os
import streamlit as st
import json

firebase_initialized = False

def inicializar_firebase():
    global firebase_initialized
    if not firebase_initialized:
        print(f"DEBUG: st.secrets['FIREBASE'] type: {type(st.secrets['FIREBASE'])}")
        print(f"DEBUG: st.secrets['FIREBASE'] keys: {st.secrets['FIREBASE'].keys() if isinstance(st.secrets['FIREBASE'], dict) else 'Not a dict'}")
        print(f"DEBUG: st.secrets['DATABASE_URL_CONFIG'] type: {type(st.secrets['DATABASE_URL_CONFIG'])}")
        print(f"DEBUG: st.secrets['DATABASE_URL_CONFIG'] value: {st.secrets['DATABASE_URL_CONFIG']}")
        cred = credentials.Certificate(st.secrets["FIREBASE"])
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["DATABASE_URL_CONFIG"]
        })
        firebase_initialized = True

# --- LEITOS ---
def salvar_leito(leito_id, dados):
    """Salva ou atualiza um leito no Firebase."""
    try:
        inicializar_firebase()
        ref = db.reference(f'leitos/{leito_id}')
        ref.set(dados)
    except Exception as e:
        print(f"Erro ao salvar leito: {e}")

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
