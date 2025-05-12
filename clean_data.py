import pandas as pd

# Carregar o arquivo de leitos
df_leitos = pd.read_excel('base/base_leitos.xlsx')

# Remover duplicatas mantendo o último registro
df_leitos = df_leitos.drop_duplicates(subset=['leito'], keep='last')

# Salvar o arquivo limpo
df_leitos.to_excel('base/base_leitos.xlsx', index=False)

print("Dados limpos com sucesso!")
