import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

def salvar_df_no_google_sheets(df, nome_planilha, nome_aba, cred_path):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open(nome_planilha).worksheet(nome_aba)
    sheet.clear()
    # Atualiza os dados: cabeçalho + valores
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# Exemplo de uso (descomente para testar isoladamente):
# df = pd.read_csv(os.path.join('data', 'leitos.csv'))
# salvar_df_no_google_sheets(df, 'hospital_app_dados', 'leitos', os.path.join('secrets', 'irah-app-14b9444a55a6.json'))
