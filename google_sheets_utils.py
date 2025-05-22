import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import json

def salvar_df_no_google_sheets(df, nome_planilha, nome_aba, cred_path=None):
    import streamlit as st
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    cred_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    # Diagnóstico: mostrar status da variável de ambiente
    if cred_json is None:
        st.warning("[DIAGNÓSTICO] GOOGLE_SHEETS_CREDENTIALS NÃO encontrada no ambiente!")
    elif not cred_json.strip():
        st.warning("[DIAGNÓSTICO] GOOGLE_SHEETS_CREDENTIALS está VAZIA!")
    else:
        st.warning("[DIAGNÓSTICO] GOOGLE_SHEETS_CREDENTIALS encontrada e não-vazia (tamanho: {} caracteres)".format(len(cred_json)))
    if cred_json and cred_json.strip():
        creds_dict = json.loads(cred_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    elif cred_path is not None:
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
    else:
        raise RuntimeError("Credencial do Google Sheets não encontrada: defina a variável de ambiente GOOGLE_SHEETS_CREDENTIALS no deploy em nuvem, ou forneça cred_path localmente.")
    client = gspread.authorize(creds)
    sheet = client.open(nome_planilha).worksheet(nome_aba)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# Exemplo de uso (descomente para testar isoladamente):
# df = pd.read_csv(os.path.join('data', 'leitos.csv'))
# salvar_df_no_google_sheets(df, 'hospital_app_dados', 'leitos', os.path.join('secrets', 'irah-app-14b9444a55a6.json'))
