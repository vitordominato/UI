import streamlit as st
import pandas as pd
from firebase_utils import obter_leitos, salvar_leito
from utils import garantir_colunas, sanitize_dict

st.set_page_config(page_title="Gestão de Leitos", layout="wide")
st.header("Painel de Leitos")

# Carrega os leitos do Firebase, sempre atualizados
@st.cache_data(ttl=30)
def get_leitos_cached():
    dados = obter_leitos()
    df = pd.DataFrame(dados)
    if df.empty:
        df = pd.DataFrame(columns=garantir_colunas([]))  # Garante todas as colunas mesmo vazio
    return df

# Botão para atualizar manualmente (opcional)
if st.button("🔄 Atualizar dados"):
    st.cache_data.clear()

df_leitos = garantir_colunas(get_leitos_cached())

# Listagem dos leitos
for _, leito in df_leitos.iterrows():
    with st.expander(f"Leito {leito['leito']} | {leito.get('nome','')}"):
        col1, col2, col3 = st.columns(3)
        novo_nome = col1.text_input("Nome do paciente", value=leito.get('nome', ''), key=f"nome_{leito['leito']}")
        novo_medico = col2.text_input("Médico", value=leito.get('medico', ''), key=f"medico_{leito['leito']}")
        novo_equipe = col3.text_input("Equipe", value=leito.get('equipe', ''), key=f"equipe_{leito['leito']}")
        
        col4, col5 = st.columns(2)
        nova_especialidade = col4.text_input("Especialidade", value=leito.get('especialidade', ''), key=f"especialidade_{leito['leito']}")
        nova_unidade = col5.text_input("Unidade", value=leito.get('unidade', ''), key=f"unidade_{leito['leito']}")
        novo_andar = st.text_input("Andar", value=leito.get('andar', ''), key=f"andar_{leito['leito']}")

        # Monta o dicionário do leito para salvar
        leito_dict = {
            'leito': leito['leito'],
            'nome': novo_nome,
            'medico': novo_medico,
            'equipe': novo_equipe,
            'especialidade': nova_especialidade,
            'unidade': nova_unidade,
            'andar': novo_andar,
            # Adicione outros campos necessários aqui
        }
        leito_dict = sanitize_dict(leito_dict)

        # Botão para salvar as alterações
        if st.button(f"Salvar alterações do leito {leito['leito']}", key=f"salvar_{leito['leito']}"):
            salvar_leito(leito['leito'], leito_dict)
            st.success("Alterações salvas! Outros usuários verão após atualizar a tela.")
            st.cache_data.clear()
