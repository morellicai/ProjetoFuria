# ProjetoFuria

**ProjetoFuria** é uma solução completa para cadastro, validação e análise de fãs, com foco em experiências para comunidades de e-sports. O sistema permite coletar dados pessoais, interesses, atividades, eventos, compras, além de validar documentos e perfis de redes sociais usando inteligência artificial. O projeto é dividido em backend (API FastAPI) e frontend (Streamlit), proporcionando uma experiência moderna e interativa.

---

## 🚀 Visão Geral

O objetivo do ProjetoFuria é criar uma plataforma robusta para:

- Coletar dados detalhados de fãs (nome, endereço, CPF, interesses, atividades, eventos, compras do último ano)
- Permitir upload e validação de documentos (ex: RG) usando OCR
- Vincular e validar perfis de redes sociais e e-sports
- Exibir um dashboard com resumo dos dados coletados
- Facilitar a integração entre frontend e backend de forma simples e escalável

---

## 🏗️ Arquitetura

```
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

- **Backend:** API RESTful construída com FastAPI, responsável por processar dados, validar documentos e gerenciar integrações.
- **Frontend:** Interface web interativa desenvolvida em Streamlit, facilitando o cadastro e visualização dos dados.

---

## ✨ Funcionalidades

- **Cadastro completo de fãs:** nome, endereço, CPF, interesses, atividades, eventos e compras.
- **Upload de documentos:** envio de imagem do RG ou similar.
- **Validação de identidade via IA:** OCR para extrair e comparar nome do documento com o informado.
- **Vinculação de redes sociais:** campos para links de perfis e páginas, incluindo e-sports.
- **Validação de links:** simulação de checagem de relevância dos perfis informados.
- **Dashboard interativo:** resumo visual dos dados coletados e validados.
- **Documentação clara e exemplos de uso.**

---

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/morellicai/ProjetoFuria.git
cd ProjetoFuria
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## 🖥️ Como rodar localmente

### Backend (FastAPI)

No diretório raiz, execute:

```bash
uvicorn app.main:app --reload
```

- Acesse a API em: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Documentação automática: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Frontend (Streamlit)

Em outro terminal, execute:

```bash
streamlit run frontend.py
```

- Acesse a interface web em: [http://localhost:8501](http://localhost:8501)

---

## 📝 Exemplo de Uso

1. Abra o frontend no navegador.
2. Preencha os campos de cadastro com seus dados.
3. Faça upload de uma imagem do seu RG.
4. Informe os links de suas redes sociais e perfis de e-sports.
5. Visualize o dashboard com o resumo dos dados e status das validações.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** FastAPI, Uvicorn, Pydantic, pytesseract (OCR)
- **Frontend:** Streamlit
- **Outros:** Pandas, Pillow, requests
