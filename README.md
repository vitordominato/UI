# Sistema de Gestão de Leitos# Sistema Hospitalar

Um sistema de gestão hospitalar desenvolvido com Streamlit para gerenciar unidades, leitos, médicos e pacientes.

## Funcionalidades

- Gerenciamento de Unidades Hospitalares
- Controle de Leitos (disponíveis, ocupados, manutenção)
- Cadastro e gerenciamento de Médicos
- Gestão de Pacientes e Fichas Clínicas
- Dashboard com estatísticas
- Interface amigável e responsiva
- Indicadores assistenciais
- Interface adaptada para dispositivos móveis

## Requisitos

- Python 3.8+
- PostgreSQL
- Git

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/vitordominato/UI.git
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
- Copie `.env.example` para `.env`
- Configure as variáveis conforme necessário

5. Inicie o banco de dados:
```bash
alembic upgrade head
```

6. Inicie o servidor:
```bash
uvicorn app.main:app --reload
```

## Estrutura do Projeto

```
hospital_app/
├── app/
│   ├── api/          # Rotas da API
│   ├── core/         # Configurações e utilitários
│   ├── db/          # Modelos e migrações
│   ├── services/    # Serviços de negócio
│   └── ui/          # Interface Streamlit
├── alembic/         # Migrações do banco de dados
├── tests/           # Testes
├── requirements.txt
├── .env.example
└── README.md
```
