
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
            fb = st.secrets.get('FIREBASE')
            print("Tipo de st.secrets['FIREBASE']:", type(fb))
            print("Valor bruto de st.secrets['FIREBASE'] (primeiros 200 chars):", str(fb)[:200])
            print("Tipo de st.secrets['DATABASE_URL_CONFIG']:", type(st.secrets.get('DATABASE_URL_CONFIG')))
            print("Valor de st.secrets['DATABASE_URL_CONFIG']:", st.secrets.get('DATABASE_URL_CONFIG'))

            firebase_secret = st.secrets["FIREBASE"]
            # Aceita dict direto, ou faz json.loads() apenas se for string
            if isinstance(firebase_secret, str):
                try:
                    firebase_secret = json.loads(firebase_secret)
                    print("FIREBASE convertido de string para dict com sucesso.")
                except Exception as err_json:
                    print("ERRO ao fazer json.loads() do segredo Firebase:", err_json)
                    print("Valor bruto recebido:", repr(st.secrets["FIREBASE"]))
                    raise
            elif isinstance(firebase_secret, dict):
                print("FIREBASE já é dict, sem necessidade de conversão.")
            else:
                print("Tipo inesperado para FIREBASE:", type(firebase_secret))
                raise ValueError("FIREBASE em st.secrets não é string nem dict!")

            print("Campos presentes em firebase_secret:", list(firebase_secret.keys()))
            print("Tipos dos campos em firebase_secret:", {k: type(v) for k, v in firebase_secret.items()})
            obrigatorios = [
                'type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id',
                'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url'
            ]
            faltando = [k for k in obrigatorios if k not in firebase_secret]
            if faltando:
                print(f"ATENÇÃO: Faltam campos obrigatórios no segredo Firebase: {faltando}")
            else:
                print("Todos os campos obrigatórios presentes no segredo Firebase.")
            pk = firebase_secret.get('private_key', '')
            print(f"Início da private_key: {pk[:40]}")
            print(f"...Fim da private_key: {pk[-40:]}")
            print(f"Tamanho da private_key: {len(pk)}")
            cred = credentials.Certificate(firebase_secret)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["DATABASE_URL_CONFIG"]
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
