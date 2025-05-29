
import firebase_admin
from firebase_admin import credentials, db
import os

def inicializar_firebase():
    if not firebase_admin._apps:
        cred_path = os.path.join(os.path.dirname(__file__), "gestaoui-firebase-adminsdk-fbsvc-754e2cb053.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://gestaoui-default-rtdb.firebaseio.com/'
        })

# --- LEITOS ---
def salvar_leito(leito_id, dados):
    inicializar_firebase()
    ref = db.reference(f'leitos/{leito_id}')
    ref.set(dados)

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

def obter_admissoes():
    inicializar_firebase()
    ref = db.reference('admissoes')
    data = ref.get()
    if data:
        return [{**{'admissao_id': k}, **v} for k, v in data.items()]
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
