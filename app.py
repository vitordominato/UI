
import streamlit as st
from firebase_utils import (
    obter_leitos, salvar_leito,
    obter_medicos, salvar_medico,
    obter_admissoes, salvar_admissao,
    obter_historico_admissoes, salvar_historico_admissao
)
import pandas as pd

st.set_page_config(page_title="Gestão Hospitalar Integrada", layout="wide")
st.title("Gestão Hospitalar Integrada")
st.write("Todas as informações estão sincronizadas em tempo real via Firebase.")

# --- Navegação ---
abas = ["Leitos", "Médicos", "Admissões", "Históricos", "Relatórios"]
aba = st.sidebar.selectbox("Escolha a seção:", abas)

# --- LEITOS ---
if aba == "Leitos":
    st.header("Painel de Leitos")
    leitos_lista = obter_leitos()
    df_leitos = pd.DataFrame(leitos_lista)

    def ficha_clinica_form(leito_id, dados_leito):
        st.subheader(f"Editar Ficha Clínica - Leito {leito_id}")
        nome = st.text_input("Nome do Paciente", value=dados_leito.get("nome", ""), key=f"nome_{leito_id}")
        medico = st.text_input("Médico Responsável", value=dados_leito.get("medico", ""), key=f"medico_{leito_id}")
        equipe = st.text_input("Equipe", value=dados_leito.get("equipe", ""), key=f"equipe_{leito_id}")
        operadora = st.text_input("Operadora", value=dados_leito.get("operadora", ""), key=f"operadora_{leito_id}")
        risco_assistencial = st.selectbox(
            "Risco Assistencial",
            ["", "Baixo", "Médio", "Alto"],
            index=["", "Baixo", "Médio", "Alto"].index(dados_leito.get("risco_assistencial", "")),
            key=f"risco_{leito_id}"
        )
        if st.button("Salvar Ficha Clínica", key=f"save_{leito_id}"):
            novos_dados = {
                "nome": nome,
                "medico": medico,
                "equipe": equipe,
                "operadora": operadora,
                "risco_assistencial": risco_assistencial,
            }
            salvar_leito(leito_id, novos_dados)
            st.success("Ficha clínica salva! Atualize a página.")

    # Listagem e edição dos leitos
    if df_leitos.empty:
        st.info("Nenhum leito cadastrado.")
    else:
        for idx, row in df_leitos.iterrows():
            leito_id = row['leito']
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown(f"**Leito: {leito_id}**")
                st.write(f"Paciente: {row.get('nome', '')}")
                st.write(f"Médico: {row.get('medico', '')}")
                st.write(f"Risco: {row.get('risco_assistencial', '')}")
            with col2:
                if st.button("Editar Ficha Clínica", key=f"edit_{leito_id}"):
                    ficha_clinica_form(leito_id, row)

    # Cadastro de novo leito
    st.header("Cadastrar Novo Leito")
    novo_leito_id = st.text_input("Número/ID do novo leito", key="novo_leito_id")
    if st.button("Adicionar Leito"):
        if novo_leito_id.strip() == "":
            st.warning("Digite o número/ID do leito.")
        else:
            salvar_leito(novo_leito_id, {})
            st.success(f"Leito {novo_leito_id} cadastrado! Atualize para visualizar.")

# --- MÉDICOS ---
elif aba == "Médicos":
    st.header("Cadastro e Lista de Médicos")
    novo_medico_id = st.text_input("ID do médico (ex: CRM ou nome)", key="novo_medico_id")
    novo_nome_medico = st.text_input("Nome do médico", key="novo_nome_medico")
    nova_especialidade = st.text_input("Especialidade", key="nova_especialidade")
    if st.button("Cadastrar Médico"):
        if novo_medico_id.strip() == "" or novo_nome_medico.strip() == "":
            st.warning("Preencha o ID e o nome do médico.")
        else:
            salvar_medico(novo_medico_id, {
                "nome": novo_nome_medico,
                "especialidade": nova_especialidade
            })
            st.success(f"Médico {novo_nome_medico} cadastrado!")

    # Listagem
    medicos_lista = obter_medicos()
    if medicos_lista:
        st.subheader("Médicos cadastrados:")
        df_medicos = pd.DataFrame(medicos_lista)
        st.dataframe(df_medicos)
    else:
        st.info("Nenhum médico cadastrado ainda.")

# --- ADMISSÕES ---
elif aba == "Admissões":
    st.header("Admissões de Pacientes")
    novo_admissao_id = st.text_input("ID da admissão", key="novo_admissao_id")
    leito = st.text_input("Leito", key="admissao_leito")
    paciente = st.text_input("Paciente", key="admissao_paciente")
    medico = st.text_input("Médico Responsável", key="admissao_medico")
    data_admissao = st.date_input("Data da Admissão")
    if st.button("Cadastrar Admissão"):
        if not (novo_admissao_id and leito and paciente and medico):
            st.warning("Preencha todos os campos obrigatórios.")
        else:
            salvar_admissao(novo_admissao_id, {
                "leito": leito,
                "paciente": paciente,
                "medico": medico,
                "data_admissao": str(data_admissao)
            })
            st.success("Admissão registrada!")

    admissoes_lista = obter_admissoes()
    if admissoes_lista:
        st.subheader("Admissões registradas:")
        df_admissoes = pd.DataFrame(admissoes_lista)
        st.dataframe(df_admissoes)
    else:
        st.info("Nenhuma admissão registrada.")

# --- HISTÓRICOS ---
elif aba == "Históricos":
    st.header("Histórico de Admissões")
    hist_id = st.text_input("ID do histórico", key="novo_hist_id")
    admissao_relacionada = st.text_input("ID da admissão relacionada", key="hist_admissao_rel")
    descricao = st.text_area("Descrição do evento", key="hist_desc")
    data_evento = st.date_input("Data do evento", key="hist_data")
    if st.button("Registrar Evento"):
        if not (hist_id and admissao_relacionada and descricao):
            st.warning("Preencha todos os campos obrigatórios.")
        else:
            salvar_historico_admissao(hist_id, {
                "admissao_relacionada": admissao_relacionada,
                "descricao": descricao,
                "data_evento": str(data_evento)
            })
            st.success("Evento registrado no histórico!")

    historico_lista = obter_historico_admissoes()
    if historico_lista:
        st.subheader("Histórico de admissões:")
        df_hist = pd.DataFrame(historico_lista)
        st.dataframe(df_hist)
    else:
        st.info("Nenhum evento no histórico.")

# --- RELATÓRIOS ---
elif aba == "Relatórios":
    st.header("Relatórios Rápidos")
    st.subheader("Estatísticas Gerais")
    total_leitos = len(obter_leitos())
    total_medicos = len(obter_medicos())
    total_admissoes = len(obter_admissoes())
    total_hist = len(obter_historico_admissoes())
    st.write(f"**Total de leitos:** {total_leitos}")
    st.write(f"**Total de médicos:** {total_medicos}")
    st.write(f"**Total de admissões:** {total_admissoes}")
    st.write(f"**Total de eventos históricos:** {total_hist}")

    st.subheader("Análise Avançada (Exemplo)")
    admissoes_lista = obter_admissoes()
    if admissoes_lista:
        df_adm = pd.DataFrame(admissoes_lista)
        if 'data_admissao' in df_adm.columns:
            df_adm['mes'] = pd.to_datetime(df_adm['data_admissao']).dt.to_period('M')
            rel_mes = df_adm['mes'].value_counts().sort_index()
            st.bar_chart(rel_mes)

st.caption("Desenvolvido com Streamlit + Firebase. Multiusuário em tempo real.")
