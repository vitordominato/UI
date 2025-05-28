
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

def salvar_leito(leito_id, dados):
    inicializar_firebase()
    ref = db.reference(f'leitos/{leito_id}')
    ref.set(dados)  # Cria ou atualiza leito

def obter_leitos():
    inicializar_firebase()
    ref = db.reference('leitos')
    data = ref.get()
    if data:
        return [{**{'leito': k}, **v} for k, v in data.items()]
    return []

# Funções similares podem ser criadas para médicos, admissões, históricos etc.
