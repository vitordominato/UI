import streamlit as st
import pandas as pd
import os
from datetime import date
from pathlib import Path

st.set_page_config(page_title="Gestão de Leitos", layout="wide")

# CSS customizado para botões coloridos
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #f0f0f0;
        color: #222;
    }
    div.stButton > button:has(span:contains('Realizado')) {
        background-color: #22c55e !important;
        color: white !important;
    }
    div.stButton > button:has(span:contains('Cancelado')) {
        background-color: #ef4444 !important;
        color: white !important;
    }
    div.stButton > button:has(span:contains('Desfazer')) {
        background-color: #facc15 !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

from datetime import datetime, date

# Função centralizada para exibir e editar a Ficha Clínica

def ficha_clinica_form(info_leito, leito, df_leitos, caminho_leitos, key_prefix="ficha"):
    risco = info_leito['risco_assistencial'].values[0] if 'risco_assistencial' in df_leitos.columns and not info_leito.empty else ""
    operadora = info_leito['operadora'].values[0] if 'operadora' in df_leitos.columns and not info_leito.empty else ""
    pendencia_rotina = info_leito['pendencia_rotina'].values[0] if 'pendencia_rotina' in df_leitos.columns and not info_leito.empty else ""
    descricao_pendencia = info_leito['descricao_pendencia'].values[0] if 'descricao_pendencia' in df_leitos.columns and not info_leito.empty else ""
    pendencia_resolvida = info_leito['pendencia_resolvida'].values[0] if 'pendencia_resolvida' in df_leitos.columns and not info_leito.empty else "Não"
    paliativo = info_leito['cuidados_paliativos'].values[0] if 'cuidados_paliativos' in df_leitos.columns and not info_leito.empty else ""
    autorizacao = info_leito['autorizacao_pendente'].values[0] if 'autorizacao_pendente' in df_leitos.columns and not info_leito.empty else ""
    desospitalizacao = info_leito['desospitalizacao'].values[0] if 'desospitalizacao' in df_leitos.columns and not info_leito.empty else ""
    alta_amanha = info_leito['alta_amanha'].values[0] if 'alta_amanha' in df_leitos.columns and not info_leito.empty else ""
    intercorrencia = info_leito['intercorrencia_24h'].values[0] if 'intercorrencia_24h' in df_leitos.columns and not info_leito.empty else ""
    desc_intercorrencia = info_leito['desc_intercorrencia'].values[0] if 'desc_intercorrencia' in df_leitos.columns and not info_leito.empty else ""
    reavaliacao = info_leito['reavaliacao_medica'].values[0] if 'reavaliacao_medica' in df_leitos.columns and not info_leito.empty else ""
    obs_gerais = info_leito['observacoes_gerais'].values[0] if 'observacoes_gerais' in df_leitos.columns and not info_leito.empty else ""
    resposta_aut = info_leito['resposta_aut'].values[0] if 'resposta_aut' in df_leitos.columns and not info_leito.empty else ""
    detalhe_aut = info_leito['detalhe_aut'].values[0] if 'detalhe_aut' in df_leitos.columns and not info_leito.empty else ""

    col_campos = st.columns(5)
    with col_campos[0]:
        st.markdown("Operadora")
        nova_operadora = st.selectbox("", ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"], index=["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"].index(operadora) if operadora in ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"] else 0, key=f"{key_prefix}_operadora_{leito}")
    with col_campos[1]:
        st.markdown("Risco assistencial")
        novo_risco = st.selectbox("", ["", "Baixo", "Moderado", "Alto"], index=["", "Baixo", "Moderado", "Alto"].index(risco) if risco in ["", "Baixo", "Moderado", "Alto"] else 0, key=f"{key_prefix}_risco_{leito}")
    with col_campos[2]:
        st.markdown("Cuidados paliativos?")
        novo_paliativo = st.selectbox("", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(paliativo) if paliativo in ["", "Sim", "Não"] else 0, key=f"{key_prefix}_paliativo_{leito}")
    with col_campos[3]:
        st.markdown("Desospitalização?")
        nova_desospitalizacao = st.selectbox("", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(desospitalizacao) if desospitalizacao in ["", "Sim", "Não"] else 0, key=f"{key_prefix}_desospitalizacao_{leito}")
    with col_campos[4]:
        st.markdown("Alta prevista para amanhã?")
        nova_alta_amanha = st.selectbox("", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(alta_amanha) if alta_amanha in ["", "Sim", "Não"] else 0, key=f"{key_prefix}_alta_amanha_{leito}")

    col_autorizacao = st.columns([2, 2, 6])
    with col_autorizacao[0]:
        st.markdown("Autorização")
        nova_autorizacao = st.selectbox(
            "", ["", "Não", "Procedimento", "Medicação"],
            index=["", "Não", "Procedimento", "Medicação"].index(autorizacao) if autorizacao in ["", "Não", "Procedimento", "Medicação"] else 0,
            key=f"{key_prefix}_autorizacao_{leito}"
        )
    with col_autorizacao[1]:
        st.markdown("Resposta")
        nova_resposta_aut = st.selectbox(
            "", ["", "Autorizado", "Em análise"],
            index=["", "Autorizado", "Em análise"].index(resposta_aut) if resposta_aut in ["", "Autorizado", "Em análise"] else 0,
            key=f"{key_prefix}_resposta_aut_{leito}"
        )
    with col_autorizacao[2]:
        st.markdown("Detalhe")
        novo_detalhe_aut = st.text_input(
            "", value=detalhe_aut, key=f"{key_prefix}_detalhe_aut_{leito}"
        )

    # Pendência do dia (em linha)
    col_pendencia = st.columns([2, 6])
    with col_pendencia[0]:
        nova_pendencia_rotina = st.selectbox(
            "Pendência do dia",
            ["nenhuma", "rotina tarde", "plantão noturno"],
            index=["nenhuma", "rotina tarde", "plantão noturno"].index(pendencia_rotina) if pendencia_rotina in ["nenhuma", "rotina tarde", "plantão noturno"] else 0,
            key=f"{key_prefix}_pendencia_rotina_{leito}"
        )
    with col_pendencia[1]:
        nova_descricao_pendencia = st.text_input(
            "Descrição",
            value=descricao_pendencia,
            key=f"{key_prefix}_descricao_pendencia_{leito}"
        )
    # Sinalização visual da pendência
    if nova_pendencia_rotina != "nenhuma":
        cor = "green" if pendencia_resolvida == "Sim" else "red"
        texto = "Resolvida" if pendencia_resolvida == "Sim" else "Pendente"
        st.markdown(f"<span style='color:{cor}; font-weight:bold'>Status da Pendência: {texto}</span>", unsafe_allow_html=True)

    nova_intercorrencia = st.selectbox("Intercorrência nas últimas 24h?", ["", "Não", "Verde", "Laranja", "Amarela", "Azul", "Outras"], index=["", "Não", "Verde", "Laranja", "Amarela", "Azul", "Outras"].index(intercorrencia) if intercorrencia in ["", "Não", "Verde", "Laranja", "Amarela", "Azul", "Outras"] else 0, key=f"{key_prefix}_intercorrencia_{leito}")
    nova_desc_intercorrencia = st.text_area("Descrição da intercorrência", value=desc_intercorrencia, key=f"{key_prefix}_desc_intercorrencia_{leito}")
    novas_obs_gerais = st.text_area("Observações gerais", value=obs_gerais, key=f"{key_prefix}_obs_gerais_{leito}")

    alterou_ficha = (
        novo_risco != risco or
        nova_operadora != operadora or
        novo_paliativo != paliativo or
        nova_autorizacao != autorizacao or
        nova_resposta_aut != resposta_aut or
        novo_detalhe_aut != detalhe_aut or
        nova_desospitalizacao != desospitalizacao or
        nova_alta_amanha != alta_amanha or
        nova_intercorrencia != intercorrencia or
        nova_desc_intercorrencia != desc_intercorrencia or
        novas_obs_gerais != obs_gerais or
        nova_pendencia_rotina != pendencia_rotina or
        nova_descricao_pendencia != descricao_pendencia
    )
    if alterou_ficha:
        df_leitos.loc[df_leitos['leito'] == leito, 'risco_assistencial'] = novo_risco
        df_leitos.loc[df_leitos['leito'] == leito, 'operadora'] = nova_operadora
        df_leitos.loc[df_leitos['leito'] == leito, 'cuidados_paliativos'] = novo_paliativo
        df_leitos.loc[df_leitos['leito'] == leito, 'autorizacao_pendente'] = nova_autorizacao
        df_leitos.loc[df_leitos['leito'] == leito, 'resposta_aut'] = nova_resposta_aut
        df_leitos.loc[df_leitos['leito'] == leito, 'detalhe_aut'] = novo_detalhe_aut
        df_leitos.loc[df_leitos['leito'] == leito, 'desospitalizacao'] = nova_desospitalizacao
        df_leitos.loc[df_leitos['leito'] == leito, 'alta_amanha'] = nova_alta_amanha
        df_leitos.loc[df_leitos['leito'] == leito, 'intercorrencia_24h'] = nova_intercorrencia
        df_leitos.loc[df_leitos['leito'] == leito, 'desc_intercorrencia'] = nova_desc_intercorrencia
        df_leitos.loc[df_leitos['leito'] == leito, 'observacoes_gerais'] = novas_obs_gerais
        df_leitos.loc[df_leitos['leito'] == leito, 'pendencia_rotina'] = nova_pendencia_rotina
        df_leitos.loc[df_leitos['leito'] == leito, 'descricao_pendencia'] = nova_descricao_pendencia
        # Mantém o status da pendência se já existe, senão inicializa como 'Não'
        if 'pendencia_resolvida' not in df_leitos.columns or pd.isna(df_leitos.loc[df_leitos['leito'] == leito, 'pendencia_resolvida']).all():
            df_leitos.loc[df_leitos['leito'] == leito, 'pendencia_resolvida'] = 'Não'
        df_leitos.to_csv(caminho_leitos, index=False)
        st.success("Ficha clínica salva!")

    col1, col2, col3 = st.columns(3)
    if col1.button("🟩 Alta", key=f"{key_prefix}_alta_{leito}"):
        # Salva paciente em altas_hoje.csv antes de zerar
        ALTAS_HOJE_PATH = os.path.join('data', 'altas_hoje.csv')
        if not os.path.exists(ALTAS_HOJE_PATH):
            pd.DataFrame(columns=["leito","nome","medico","equipe","data_alta"]).to_csv(ALTAS_HOJE_PATH, index=False)
        altas_hoje = pd.read_csv(ALTAS_HOJE_PATH, dtype=str).fillna("")
        info_alta = df_leitos[df_leitos['leito'] == leito][['leito','nome','medico','equipe']].copy()
        info_alta['data_alta'] = date.today().strftime('%Y-%m-%d')
        altas_hoje = pd.concat([altas_hoje, info_alta], ignore_index=True)
        altas_hoje.to_csv(ALTAS_HOJE_PATH, index=False)
        # Zera informações do paciente
        for campo in ['nome','medico','equipe','especialidade','risco_assistencial','operadora','pendencia_rotina','descricao_pendencia','cuidados_paliativos','autorizacao_pendente','desospitalizacao','alta_amanha','intercorrencia_24h','desc_intercorrencia','reavaliacao_medica','observacoes_gerais']:
            df_leitos.loc[df_leitos['leito'] == leito, campo] = ""
        df_leitos.to_csv(caminho_leitos, index=False)
        st.success("Leito liberado por alta!")
    if col2.button("🟧 Transferência", key=f"{key_prefix}_transfer_{leito}"):
        # Zera informações do paciente
        for campo in ['nome','medico','equipe','especialidade','risco_assistencial','operadora','pendencia_rotina','descricao_pendencia','cuidados_paliativos','autorizacao_pendente','desospitalizacao','alta_amanha','intercorrencia_24h','desc_intercorrencia','reavaliacao_medica','observacoes_gerais']:
            df_leitos.loc[df_leitos['leito'] == leito, campo] = ""
        df_leitos.to_csv(caminho_leitos, index=False)
        st.success("Leito liberado por transferência!")
    if col3.button("⛔ Óbito", key=f"{key_prefix}_obito_{leito}"):
        # Zera informações do paciente
        for campo in ['nome','medico','equipe','especialidade','risco_assistencial','operadora','pendencia_rotina','descricao_pendencia','cuidados_paliativos','autorizacao_pendente','desospitalizacao','alta_amanha','intercorrencia_24h','desc_intercorrencia','reavaliacao_medica','observacoes_gerais']:
            df_leitos.loc[df_leitos['leito'] == leito, campo] = ""
        df_leitos.to_csv(caminho_leitos, index=False)
        st.success("Leito liberado por óbito!")

# Funções auxiliares e caminhos para admissões/admitidos
ADMISSOES_PATH = os.path.join('data', 'admissoes.csv')
ADMITIDOS_PATH = os.path.join('data', 'admitidos.csv')
if not os.path.exists(ADMISSOES_PATH):
    pd.DataFrame(columns=["nome_paciente","origem","observacoes"]).to_csv(ADMISSOES_PATH, index=False)
if not os.path.exists(ADMITIDOS_PATH):
    pd.DataFrame(columns=["nome_paciente","origem","observacoes","data_admissao"]).to_csv(ADMITIDOS_PATH, index=False)
def carregar_admissoes():
    return pd.read_csv(ADMISSOES_PATH, dtype=str).fillna("")
def carregar_admitidos():
    return pd.read_csv(ADMITIDOS_PATH, dtype=str).fillna("")
def salvar_admissoes(df):
    df.to_csv(ADMISSOES_PATH, index=False)
def salvar_admitidos(df):
    df.to_csv(ADMITIDOS_PATH, index=False)

# Diretórios e arquivos
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CAMINHO_LEITOS = str(DATA_DIR / "leitos.csv")
CAMINHO_MEDICOS = str(DATA_DIR / "medicos.csv")

# Colunas dos DataFrames
colunas_leitos = [
    "leito", "nome", "medico", "especialidade", "risco", "operadora",
    "pendencia_rotina", "exame", "reavaliacao", "descricao_pendencia", "paliativo", "cirurgia", "medicacao",
    "desospitalizacao", "alta_amanha", "intercorrencia", "cor_intercorrencia", "observacao"
]
colunas_medicos = ["Nome do Médico", "CRM", "Especialidade", "Equipe"]

# Layout responsivo: menu hambúrguer e filtros rápidos
# Estrutura dos andares por unidade
CONFIG_ANDARES = {
    "Unidade I": {
        "4º andar": (401, 432),
        "5º andar": (501, 535),
        "6º andar": (601, 637),
    },
    "Unidade III": {
        "4º andar (Unidade III)": (401, 404),
        "5º andar (Pediatria)": (501, 510),
        "6º andar (Pediatria)": (601, 610),
        "7º andar": (701, 710),
        "8º andar (Obstetrícia)": (801, 810),
        "9º andar (Obstetrícia)": (901, 910),
    },
    "Unidade IV": {
        "6º andar (TMO)": (601, 626),
        "7º andar (Cardiologia)": (701, 728),
        "8º andar (Unidade IV)": (801, 828),
        "9º andar (Unidade IV)": (901, 928),
    }
}

# Carregar dados dos médicos e montar lista ANTES do sidebar
if os.path.exists(CAMINHO_MEDICOS):
    df_medicos = pd.read_csv(CAMINHO_MEDICOS, dtype=str).fillna("")
else:
    df_medicos = pd.DataFrame(columns=colunas_medicos)
medicos_lista = df_medicos['Nome do Médico'].dropna().unique().tolist()

with st.sidebar:
    st.title("🏥 Gestão de Leitos")
    st.markdown("---")
    st.subheader("Filtros rápidos")
    unidade = st.selectbox("Unidade", list(CONFIG_ANDARES.keys()), key="unidade_filtro")
    andares_disponiveis = list(CONFIG_ANDARES[unidade].keys())
    andar = st.selectbox("Andar", andares_disponiveis, key="andar_filtro")
    # Dropdown de médicos cadastrados para filtro
    if len(medicos_lista) > 0:
        medico_filtro = st.selectbox("Filtrar por médico", ["(Todos)"] + medicos_lista, key="medico_filtro_select")
    else:
        medico_filtro = "(Todos)"
    st.markdown("---")


# Criação de tabs
abas = ["Leitos", "Visão do Plantonista", "Pendência tarde", "Admissão", "Médicos", "Gestão"]
tabs = st.tabs(abas)

# Painel de Leitos (tela principal)
with tabs[0]:
    st.header("Painel de Leitos")

    # Carregar dados reais dos leitos e médicos
    if os.path.exists(CAMINHO_LEITOS):
        df_leitos = pd.read_csv(CAMINHO_LEITOS, dtype=str).fillna("")
    else:
        df_leitos = pd.DataFrame(columns=colunas_leitos)

    # Garante colunas de autorização para evitar KeyError
    if 'resposta_aut' not in df_leitos.columns:
        df_leitos['resposta_aut'] = ''
    if 'detalhe_aut' not in df_leitos.columns:
        df_leitos['detalhe_aut'] = ''

    if len(df_leitos) == 0:
        st.info("Nenhum leito cadastrado.")
    elif medico_filtro != "(Todos)":
        # Filtra todos os pacientes do médico, agrupados por unidade e andar
        setores = {}
        for unidade_nome, andares in CONFIG_ANDARES.items():
            for andar_nome, (inicio, fim) in andares.items():
                # Gera o range de leitos com sufixo correto
                if unidade_nome == "Unidade III":
                    leitos_setor = [f"{i}-3" for i in range(inicio, fim + 1)]
                elif unidade_nome == "Unidade IV":
                    leitos_setor = [f"{i}-4" for i in range(inicio, fim + 1)]
                else:
                    leitos_setor = [str(i) for i in range(inicio, fim + 1)]
                for leito in leitos_setor:
                    info_leito = df_leitos[df_leitos['leito'] == leito]
                    if not info_leito.empty:
                        nome_medico = info_leito['medico'].values[0]
                        nome_paciente = info_leito['nome'].values[0]
                        equipe = info_leito['equipe'].values[0] if ('equipe' in df_leitos.columns) else ""
                        if nome_medico == medico_filtro and nome_paciente:
                            chave_setor = f"{unidade_nome} - {andar_nome}"
                            if chave_setor not in setores:
                                setores[chave_setor] = []
                            setores[chave_setor].append({
                                'leito': leito,
                                'paciente': nome_paciente,
                                'equipe': equipe
                            })
        if not setores:
            st.info("Nenhum paciente encontrado para este médico.")
        else:
            for setor, pacientes in setores.items():
                st.markdown(f"### {setor}")
                for p in pacientes:
                    leito = p['leito']
                    info_leito = df_leitos[df_leitos['leito'] == leito]
                    nome_paciente = p['paciente']
                    equipe = p['equipe']
                    # Exibe informações básicas
                    st.write(f"Leito: {leito} | Paciente: {nome_paciente} | Equipe: {equipe}")
                    descricao_pendencia = info_leito['descricao_pendencia'].values[0] if 'descricao_pendencia' in df_leitos.columns and not info_leito.empty else ""
                    with st.expander("Ficha Clínica", expanded=False):
                        ficha_clinica_form(info_leito, leito, df_leitos, CAMINHO_LEITOS, key_prefix="medico")
                    st.markdown("---")
    else:
        # Exibe todos os leitos normalmente
        inicio, fim = CONFIG_ANDARES[unidade][andar]
        if unidade == "Unidade III":
            leitos_range = [f"{i}-3" for i in range(inicio, fim + 1)]
        elif unidade == "Unidade IV":
            leitos_range = [f"{i}-4" for i in range(inicio, fim + 1)]
        else:
            leitos_range = [str(i) for i in range(inicio, fim + 1)]

        for leito in leitos_range:
            info_leito = df_leitos[df_leitos['leito'] == leito]
            nome_paciente = info_leito['nome'].values[0] if not info_leito.empty else ""
            nome_medico = info_leito['medico'].values[0] if not info_leito.empty else ""
            equipe = info_leito['equipe'].values[0] if ('equipe' in df_leitos.columns and not info_leito.empty) else ""

            with st.container():
                cols = st.columns([1, 3, 3, 2])
                cols[0].markdown(f"**Leito {leito}**")
                # Campos editáveis SEMPRE visíveis
                novo_nome = cols[1].text_input("Nome do paciente", value=nome_paciente, key=f"edit_nome_{leito}")
                novo_medico = cols[2].selectbox("Médico", medicos_lista, index=medicos_lista.index(nome_medico) if nome_medico in medicos_lista else 0, key=f"edit_medico_{leito}")
                novo_equipe = cols[3].selectbox("Equipe", ["Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente", "Hematologia", "Oncologia"], index=["Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente", "Hematologia", "Oncologia"].index(equipe) if equipe in ["Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente", "Hematologia", "Oncologia"] else 0, key=f"edit_equipe_{leito}")
                # Salvamento automático
                alterou = (
                    novo_nome != nome_paciente or
                    novo_medico != nome_medico or
                    novo_equipe != equipe
                )
                if alterou:
                    # Se o leito não existe, cria uma nova linha
                    if info_leito.empty:
                        nova_linha = {col: '' for col in df_leitos.columns}
                        nova_linha['leito'] = leito
                        df_leitos = pd.concat([df_leitos, pd.DataFrame([nova_linha])], ignore_index=True)
                    df_leitos.loc[df_leitos['leito'] == leito, 'nome'] = novo_nome
                    df_leitos.loc[df_leitos['leito'] == leito, 'medico'] = novo_medico
                    df_leitos.loc[df_leitos['leito'] == leito, 'equipe'] = novo_equipe
                    df_leitos.to_csv(CAMINHO_LEITOS, index=False)
                    st.success("Salvo!")
                # Ficha Clínica como expander (seta para baixo)
                descricao_pendencia = info_leito['descricao_pendencia'].values[0] if 'descricao_pendencia' in df_leitos.columns and not info_leito.empty else ""
                with st.expander("Ficha Clínica", expanded=False):
                    ficha_clinica_form(info_leito, leito, df_leitos, CAMINHO_LEITOS, key_prefix="painel")
                st.markdown("---")

if os.path.exists(CAMINHO_MEDICOS):
    df_medicos = pd.read_csv(CAMINHO_MEDICOS, dtype=str).fillna("")
else:
    df_medicos = pd.DataFrame(columns=colunas_medicos)

# Lista de médicos (apenas nomes)
medicos_lista = df_medicos['Nome do Médico'].dropna().unique().tolist()

# Exibição dinâmica dos leitos do andar selecionado
inicio, fim = CONFIG_ANDARES[unidade][andar]
if unidade == "Unidade III":
    leitos_range = [f"{i}-3" for i in range(inicio, fim + 1)]
elif unidade == "Unidade IV":
    leitos_range = [f"{i}-4" for i in range(inicio, fim + 1)]
else:
    leitos_range = [str(i) for i in range(inicio, fim + 1)]

# Lista fixa de equipes (ordem alfabética)
equipes_lista = [
    "CABERJ",
    "Cardiologia",
    "Cirurgia Geral",
    "Urologia"
]

with tabs[1]:
    st.header("Resumo do Plantão")
    # Lista Pacientes em Cuidados Paliativos
    with st.expander("Pacientes em Cuidados Paliativos", expanded=True):
        if os.path.exists(CAMINHO_LEITOS):
            df_leitos_paliativos = pd.read_csv(CAMINHO_LEITOS, dtype=str).fillna("")
            paliativos = df_leitos_paliativos[df_leitos_paliativos['cuidados_paliativos'].str.lower() == 'sim']
            if not paliativos.empty:
                for idx, row in paliativos.iterrows():
                    cols = st.columns([1, 3, 3, 3])
                    cols[0].markdown(f"<b>Leito:</b> {row['leito']}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row['nome']}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico responsável:</b> {row['medico']}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row['equipe']}", unsafe_allow_html=True)
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhum paciente em cuidados paliativos no momento.")
        else:
            st.caption("Nenhum dado de leitos disponível.")
    # Lista Pendência Noite
    with st.expander("Pendência noite", expanded=True):
        if os.path.exists(CAMINHO_LEITOS):
            df_leitos_pendencia = pd.read_csv(CAMINHO_LEITOS, dtype=str).fillna("")
            pendencias_noite = df_leitos_pendencia[(df_leitos_pendencia['pendencia_rotina'] == 'plantão noturno') & (df_leitos_pendencia['pendencia_resolvida'] != 'Sim')]
            if not pendencias_noite.empty:
                for idx, row in pendencias_noite.iterrows():
                    cols = st.columns([1, 2, 2, 2, 2, 3, 1])
                    cols[0].markdown(f"<b>Leito:</b> {row['leito']}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row['nome']}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico:</b> {row['medico']}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row['equipe']}", unsafe_allow_html=True)
                    cols[4].markdown(f"<b>Tipo:</b> {row['pendencia_rotina']}", unsafe_allow_html=True)
                    cols[5].markdown(f"<b>Descrição:</b> {row['descricao_pendencia']}", unsafe_allow_html=True)
                    if cols[6].button("Realizado", key=f"realizado_noite_{row['leito']}"):
                        df_leitos_pendencia.loc[df_leitos_pendencia['leito'] == row['leito'], 'pendencia_resolvida'] = 'Sim'
                        df_leitos_pendencia.to_csv(CAMINHO_LEITOS, index=False)
                        st.success(f"Pendência do leito {row['leito']} marcada como realizada.")
                        st.experimental_rerun()
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhuma pendência de plantão noturno aberta.")
        else:
            st.caption("Nenhum dado de leitos disponível.")
    # Código Amarelo segue abaixo
    with st.expander("Código Amarelo nas últimas 24h", expanded=True):
        if os.path.exists(CAMINHO_LEITOS):
            df_leitos_codigo = pd.read_csv(CAMINHO_LEITOS, dtype=str).fillna("")
            hoje = date.today().strftime('%Y-%m-%d')
            if 'data_intercorrencia' in df_leitos_codigo.columns:
                amarelos = df_leitos_codigo[(df_leitos_codigo['intercorrencia_24h'].str.lower() == 'amarela') & (df_leitos_codigo['data_intercorrencia'] == hoje)]
            else:
                amarelos = df_leitos_codigo[df_leitos_codigo['intercorrencia_24h'].str.lower() == 'amarela']
            if not amarelos.empty:
                for idx, row in amarelos.iterrows():
                    cols = st.columns([1, 2, 2, 3])
                    cols[0].markdown(f"<b>Leito:</b> {row['leito']}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row['nome']}", unsafe_allow_html=True)
                    equipe = row['equipe'] if 'equipe' in row else ''
                    cols[2].markdown(f"<b>Equipe:</b> {equipe}", unsafe_allow_html=True)
                    descricao = row['desc_intercorrencia'] if 'desc_intercorrencia' in row else ''
                    cols[3].markdown(f"<b>Descrição:</b> {descricao}", unsafe_allow_html=True)
                    st.markdown('<hr style=\"margin-top: 0.5rem; margin-bottom: 0.5rem;\">', unsafe_allow_html=True)
            else:
                st.caption("Nenhum paciente com intercorrência amarela nas últimas 24h.")
        else:
            st.caption("Nenhum dado de leitos disponível.")

with tabs[2]:
    st.header("Pendência tarde")
    if os.path.exists(CAMINHO_LEITOS):
        df_leitos_pendencia = pd.read_csv(CAMINHO_LEITOS, dtype=str).fillna("")
        pendencias_tarde = df_leitos_pendencia[(df_leitos_pendencia['pendencia_rotina'] == 'rotina tarde') & (df_leitos_pendencia['pendencia_resolvida'] != 'Sim')]
        if not pendencias_tarde.empty:
            for idx, row in pendencias_tarde.iterrows():
                cols = st.columns([1, 2, 2, 2, 2, 3, 1])
                cols[0].markdown(f"<b>Leito:</b> {row['leito']}", unsafe_allow_html=True)
                cols[1].markdown(f"<b>Paciente:</b> {row['nome']}", unsafe_allow_html=True)
                cols[2].markdown(f"<b>Médico:</b> {row['medico']}", unsafe_allow_html=True)
                cols[3].markdown(f"<b>Equipe:</b> {row['equipe']}", unsafe_allow_html=True)
                cols[4].markdown(f"<b>Tipo:</b> {row['pendencia_rotina']}", unsafe_allow_html=True)
                cols[5].markdown(f"<b>Descrição:</b> {row['descricao_pendencia']}", unsafe_allow_html=True)
                if cols[6].button("Realizado", key=f"realizado_tarde_{row['leito']}"):
                    df_leitos_pendencia.loc[df_leitos_pendencia['leito'] == row['leito'], 'pendencia_resolvida'] = 'Sim'
                    df_leitos_pendencia.to_csv(CAMINHO_LEITOS, index=False)
                    st.success(f"Pendência do leito {row['leito']} marcada como realizada.")
                    st.experimental_rerun()
                st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
        else:
            st.caption("Nenhuma pendência de rotina tarde aberta.")
    else:
        st.caption("Nenhum dado de leitos disponível.")

with tabs[3]:
    st.header("Admissão de Paciente")
    with st.expander("Nova Admissão", expanded=True):
        nome_paciente = st.text_input("Nome do paciente", key="admissao_nome_admissao")
        origem = st.selectbox("Origem", ["Emergência", "CTI", "Outros"], key="admissao_origem_admissao")
        obs = st.text_area("Observações", key="admissao_obs_admissao")
        if st.button("Salvar Admissão", key="admissao_salvar_admissao"):
            df_adm = carregar_admissoes()
            nova = {"nome_paciente": nome_paciente, "origem": origem, "observacoes": obs}
            df_adm = pd.concat([df_adm, pd.DataFrame([nova])], ignore_index=True)
            salvar_admissoes(df_adm)
            st.success("Paciente adicionado à lista de admissões!")
        if st.button("Cancelar", key="admissao_cancelar_admissao"):
            st.session_state['modal_admissao'] = False

    st.subheader("Admissões Pendentes")
    df_adm = carregar_admissoes()
    for idx, row in df_adm.reset_index().iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([3,2,4,4,2,2])
        c1.write(row['nome_paciente'])
        c2.write(row['origem'])
        c3.write(row['observacoes'])
        realizado_key = f"realizado_{row['nome_paciente']}_{row['origem']}_{idx}"
        cancel_key = f"cancelado_{row['nome_paciente']}_{row['origem']}_{idx}"
        if c5.button("Realizado", key=realizado_key, type="secondary"):
            st.markdown("""
                <style>
                div[data-testid='stButton'] button[kind='secondary'] {background-color: #22c55e !important; color: white !important;}
                </style>
            """, unsafe_allow_html=True)
            # Migrar para admitidos
            df_admitidos = carregar_admitidos()
            data_hoje = date.today().strftime('%Y-%m-%d')
            novo = {"nome_paciente": row['nome_paciente'], "origem": row['origem'], "observacoes": row['observacoes'], "data_admissao": data_hoje}
            df_admitidos = pd.concat([df_admitidos, pd.DataFrame([novo])], ignore_index=True)
            salvar_admitidos(df_admitidos)
            # Remover da lista de admissões
            df_adm = df_adm.drop(row['index']).reset_index(drop=True)
            salvar_admissoes(df_adm)
            st.experimental_rerun()
        if c6.button("Cancelado", key=cancel_key, type="secondary"):
            st.markdown("""
                <style>
                div[data-testid='stButton'] button[kind='secondary'] {background-color: #ef4444 !important; color: white !important;}
                </style>
            """, unsafe_allow_html=True)
            # Remove a linha da lista de admissões
            df_adm = df_adm.drop(row['index']).reset_index(drop=True)
            salvar_admissoes(df_adm)
            st.experimental_rerun()

    st.subheader("Admitidos")
    df_admitidos = carregar_admitidos()
    for idx, row in df_admitidos.iterrows():
        c1, c2, c3, c4, c5 = st.columns([3,2,4,3,2])
        c1.write(row['nome_paciente'])
        c2.write(row['origem'])
        c3.write(row['observacoes'])
        c4.write(row['data_admissao'])
        desfazer_key = f"desfazer_{row['nome_paciente']}_{row['origem']}_{idx}"
        if c5.button("Desfazer", key=desfazer_key, type="secondary"):
            st.markdown("""
                <style>
                div[data-testid='stButton'] button[kind='secondary'] {background-color: #facc15 !important; color: black !important;}
                </style>
            """, unsafe_allow_html=True)
            # Remover dos admitidos e retornar para admissões pendentes
            df_admitidos_novo = df_admitidos.drop(idx).reset_index(drop=True)
            salvar_admitidos(df_admitidos_novo)
            df_adm = carregar_admissoes()
            nova = {"nome_paciente": row['nome_paciente'], "origem": row['origem'], "observacoes": row['observacoes']}
            df_adm = pd.concat([df_adm, pd.DataFrame([nova])], ignore_index=True)
            salvar_admissoes(df_adm)
            st.experimental_rerun()

with tabs[4]:
    st.header("Cadastro de Médicos")
    novo_medico = st.text_input("Nome do médico", key="medicos_nome_medico")
    if st.button("Salvar", key="medicos_salvar_medico"):
        if novo_medico.strip():
            df_medicos = pd.read_csv(CAMINHO_MEDICOS, dtype=str).fillna("") if os.path.exists(CAMINHO_MEDICOS) else pd.DataFrame(columns=["Nome do Médico"])
            if novo_medico.strip() not in df_medicos['Nome do Médico'].values:
                df_medicos = pd.concat([df_medicos, pd.DataFrame({"Nome do Médico": [novo_medico.strip()]})], ignore_index=True)
                df_medicos.to_csv(CAMINHO_MEDICOS, index=False)
                st.success("Médico cadastrado com sucesso!")
            else:
                st.info("Este médico já está cadastrado.")
        else:
            st.warning("Digite o nome do médico antes de salvar.")
    # Lista dos médicos já cadastrados
    st.subheader("Médicos cadastrados")
    if os.path.exists(CAMINHO_MEDICOS):
        df_medicos = pd.read_csv(CAMINHO_MEDICOS, dtype=str).fillna("")
        for idx, nome in enumerate(df_medicos['Nome do Médico']):
            col_nome, col_excluir = st.columns([6,1])
            col_nome.write(f"- {nome}")
            if col_excluir.button("Excluir", key=f"excluir_medico_{idx}"):
                df_medicos_novo = df_medicos[df_medicos['Nome do Médico'] != nome].reset_index(drop=True)
                df_medicos_novo.to_csv(CAMINHO_MEDICOS, index=False)
                st.experimental_rerun()
    else:
        st.info("Nenhum médico cadastrado ainda.")

with tabs[5]:
    st.header("Gestão")
    if os.path.exists(CAMINHO_LEITOS):
        df_gestao = pd.read_csv(CAMINHO_LEITOS, dtype=str).fillna("")
        # Lista 1: Pacientes AMIL
        with st.expander("Pacientes AMIL", expanded=True):
            amil = df_gestao[df_gestao['operadora'].str.upper() == 'AMIL']
            if not amil.empty:
                for idx, row in amil.iterrows():
                    cols = st.columns([1, 3, 2, 2, 2, 2])
                    cols[0].markdown(f"<b>Leito:</b> {row.get('leito','')}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row.get('nome','')}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico:</b> {row.get('medico','')}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row.get('equipe','') if 'equipe' in row else ''}", unsafe_allow_html=True)
                    cols[4].markdown(f"<b>Operadora:</b> {row.get('operadora','')}", unsafe_allow_html=True)
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhum paciente AMIL encontrado.")
        # Lista 2: Desospitalização
        with st.expander("Desospitalização", expanded=True):
            desosp = df_gestao[df_gestao['desospitalizacao'].str.lower() == 'sim']
            if not desosp.empty:
                for idx, row in desosp.iterrows():
                    cols = st.columns([1, 3, 2, 2, 2, 2])
                    cols[0].markdown(f"<b>Leito:</b> {row.get('leito','')}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row.get('nome','')}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico:</b> {row.get('medico','')}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row.get('equipe','') if 'equipe' in row else ''}", unsafe_allow_html=True)
                    cols[4].markdown(f"<b>Desospitalização:</b> {row.get('desospitalizacao','')}", unsafe_allow_html=True)
                    cols[5].markdown(f"<b>Operadora:</b> {row.get('operadora','')}", unsafe_allow_html=True)
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhum paciente em desospitalização.")
        # Lista 3: Autorização
        with st.expander("Autorização", expanded=True):
            autorizacao = df_gestao[df_gestao['autorizacao_pendente'].isin(['Procedimento','Medicação'])]
            if not autorizacao.empty:
                for idx, row in autorizacao.iterrows():
                    cols = st.columns([1, 3, 2, 2, 2, 2, 3])
                    cols[0].markdown(f"<b>Leito:</b> {row.get('leito','')}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row.get('nome','')}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico:</b> {row.get('medico','')}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row.get('equipe','') if 'equipe' in row else ''}", unsafe_allow_html=True)
                    cols[4].markdown(f"<b>Autorização:</b> {row.get('autorizacao_pendente','')}", unsafe_allow_html=True)
                    cols[5].markdown(f"<b>Operadora:</b> {row.get('operadora','')}", unsafe_allow_html=True)
                    cols[6].markdown(f"<b>Detalhe:</b> {row.get('detalhe_aut','') if 'detalhe_aut' in row else ''}", unsafe_allow_html=True)
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhuma autorização pendente.")
        # Lista 4: Alta prevista para amanhã
        with st.expander("Alta prevista para amanhã", expanded=True):
            alta = df_gestao[df_gestao['alta_amanha'].str.lower() == 'sim']
            if not alta.empty:
                for idx, row in alta.iterrows():
                    cols = st.columns([1, 3, 2, 2, 2, 2])
                    cols[0].markdown(f"<b>Leito:</b> {row.get('leito','')}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row.get('nome','')}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico:</b> {row.get('medico','')}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row.get('equipe','') if 'equipe' in row else ''}", unsafe_allow_html=True)
                    cols[4].markdown(f"<b>Alta prevista para amanhã:</b> {row.get('alta_amanha','')}", unsafe_allow_html=True)
                    cols[5].markdown(f"<b>Operadora:</b> {row.get('operadora','')}", unsafe_allow_html=True)
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhum paciente com alta prevista para amanhã.")
        # Lista 5: Altas Hoje
        ALTAS_HOJE_PATH = os.path.join('data', 'altas_hoje.csv')
        with st.expander("Altas Hoje", expanded=True):
            if os.path.exists(ALTAS_HOJE_PATH):
                altas_hoje = pd.read_csv(ALTAS_HOJE_PATH, dtype=str).fillna("")
                hoje = date.today().strftime('%Y-%m-%d')
                altas_hoje = altas_hoje[altas_hoje['data_alta'] == hoje]
                if not altas_hoje.empty:
                    for idx, row in altas_hoje.iterrows():
                        cols = st.columns([1, 3, 2, 2])
                        cols[0].markdown(f"<b>Leito:</b> {row.get('leito','')}", unsafe_allow_html=True)
                        cols[1].markdown(f"<b>Paciente:</b> {row.get('nome','')}", unsafe_allow_html=True)
                        cols[2].markdown(f"<b>Médico:</b> {row.get('medico','')}", unsafe_allow_html=True)
                        cols[3].markdown(f"<b>Equipe:</b> {row.get('equipe','')}", unsafe_allow_html=True)
                        st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
                else:
                    st.caption("Nenhuma alta registrada hoje.")
            else:
                st.caption("Nenhuma alta registrada hoje.")
    else:
        st.info("Nenhum dado de leitos disponível.")



# Rodapé
st.markdown("---")
st.caption("Sistema desenvolvido para uso hospitalar, mobile-first, multiusuário e com sincronização em tempo real.")
