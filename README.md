# Projeto Furia - Sistema de Gerenciamento de Fãs

Este projeto oferece um sistema completo para gerenciamento de fãs da equipe de e-sports FURIA, permitindo cadastro de fãs, validação de documentos, gerenciamento de redes sociais e análise de engajamento.

## Sumário

- [Projeto Furia - Sistema de Gerenciamento de Fãs](#projeto-furia---sistema-de-gerenciamento-de-fãs)
  - [Sumário](#sumário)
  - [Visão Geral](#visão-geral)
  - [Estrutura do Projeto](#estrutura-do-projeto)
- [Funcionalidades](#funcionalidades)
- [Instalação e Configuração](#instalação-e-configuração)
- [Executando o Projeto](#executando-o-projeto)
  - [Backend (FastAPI)](#backend-fastapi)
  - [FrontEnd (Streamlit)](#frontend-streamlit)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)

---

## Visão Geral

O Projeto Furia é um sistema que possibilita:

1. Cadastro de fãs, com informações pessoais, interesses e atividades.
2. Upload e validação de documentos.
3. Vinculação e validação de perfis de redes sociais (Instagram, Twitter, Steam, GamersClub).
4. Visualização e análise de engajamento dos fãs em um painel administrativo.

Esta aplicação foi desenvolvida utilizando Python, FastAPI (para o backend) e Streamlit (para o frontend).

---

## Estrutura do Projeto

```bash
ProjetoFuria/
├── app/
│   ├── database.py          # Configuração da conexão com o banco de dados
│   ├── main.py              # Ponto de entrada da API FastAPI
│   ├── middleware/
│   │   └── upload_validator.py   # Middleware para validação de uploads
│   ├── models.py            # Modelos de dados (SQLAlchemy e Pydantic)
│   ├── routes/
│   │   ├── cadastro.py      # Rotas de cadastro de fãs
│   │   ├── dashboard.py     # Rotas para exibição e estatísticas de fãs
│   │   ├── redes.py         # Rotas para gerenciamento de redes sociais
│   │   └── upload.py        # Rotas para upload de documentos
│   └── services/
│       └── ai_validator.py  # Lógica de validação de conteúdo usando IA
├── frontend.py              # Arquivo Streamlit para o dashboard
├── requirements.txt         # Lista de dependências do projeto
└── README.md                # Documentação do projeto (este arquivo)
```

# Funcionalidades

1. **Cadastro de Fãs**
    - Registro de dados pessoais (nome, CPF, endereço, etc.).
    - Definição de interesses, eventos e histórico de compras.
2. **Validação de Documentos**
    - Upload de documentos (imagens ou PDFs).
    - Validação (manual ou automática) do conteúdo dos documentos.
3. **Gerenciamento de Redes Sociais**
    - Inclusão de perfis (Instagram, Twitter, Steam, GamersClub).
    - Validação com IA para verificar relevância ao perfil de e-sports.
4. **Dashboard de Gerenciamento**
    - Visualização e filtro de todos os fãs cadastrados.
    - Estatísticas de engajamento, top interesses, eventos e compras populares.
    - Interface intuitiva em Streamlit com botões e barra de pesquisa.

# Instalação e Configuração
1. **Clonar o repositório (ou baixar o código-fonte)**
   ```bash
   git clone https://github.com/SeuUsuario/ProjetoFuria.git
   cd ProjetoFuria
   ```
2. **Criar e ativar um ambiente virtual
    ```bash
    python -m venv env
    source env/bin/activate
    # No Windows:
    # .\env\Scripts\activate
   ```
3. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```
> Certifique-se de que todas as dependências sejam instaladas com sucesso!

# Executando o Projeto
## Backend (FastAPI)
Na raiz do projeto, execute:
```bash
uvicorn app.main:app --reload
```
isso iniciará o backend na porta padrão (8000). A documentação interativa do FastAPI estrá disponivel em:
```plaintext
http://localhost:8000/docs
```
- Ou se preferir:
```plaintext
http://localhost:8000/redoc
```
## FrontEnd (Streamlit)
Você pode rodar o dashboard localmente executando:
```bash
streamlit run frontend.py
```
Por padrão, o Streamlit estará disponível em `http://localhost:8501`.

# Tecnologias Utilizadas
- **Python 3.9+**
- **FastAPI**
- **SQLAlchemy**
- **Pydantic**
- **Uvicorn**
- **Streamlit**
- **Requests**
- **BeautifulSoup4** (para extração de conteúdo)
- **spaCy** (para validação avançada de conteúdo com IA)