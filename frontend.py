import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import os
import streamlit as st

# Configuração da API
backend_option = st.sidebar.selectbox(
    "Ambiente:",
    ("Local", "Produção")
)

BACKEND_URL = "https://projetofuria.onrender.com" if backend_option == "Produção" else "http://localhost:8000"
response = requests.get(f"{BACKEND_URL}/predict", params={"x": 1})

# Configuração da página
st.set_page_config(
    page_title="Dashboard Furia",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funções para consumir a API
def get_fans(interesse=None, evento=None, compra=None, engajamento=None, page=1, page_size=100, nome=None):
    """Obtém a lista de fãs com filtros opcionais"""
    params = {
        "page": page,
        "page_size": page_size
    }

    if interesse:
        params["interesse"] = interesse
    if evento:
        params["evento"] = evento
    if compra:
        params["compra"] = compra
    if engajamento:
        params["engajamento"] = engajamento

    try:
        response = requests.get(f"{API_URL}/dashboard/fans", params=params)
        response.raise_for_status()
        data = response.json()

        # Filtrar por nome se fornecido
        if nome and data["fans"]:
            data["fans"] = [fan for fan in data["fans"] if nome.lower() in fan["nome"].lower()]
            data["total"] = len(data["fans"])

        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados dos fãs: {str(e)}")
        return {"fans": [], "total": 0, "page": 1, "total_pages": 1}

def get_stats():
    """Obtém estatísticas gerais do dashboard"""
    try:
        response = requests.get(f"{API_URL}/dashboard/stats")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter estatísticas: {str(e)}")
        return {
            "total_fans": 0,
            "top_interesses": [],
            "top_eventos": [],
            "top_compras": []
        }

def get_fan_redes(fan_id):
    """Obtém as redes sociais de um fã específico"""
    try:
        response = requests.get(f"{API_URL}/redes/{fan_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter redes sociais: {str(e)}")
        return []

def cadastrar_fan(fan_data):
    """Cadastra um novo fã"""
    try:
        response = requests.post(f"{API_URL}/cadastro", json=fan_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao cadastrar fã: {str(e)}")
        return None

def adicionar_redes(fan_id, redes_data):
    """Adiciona redes sociais a um fã"""
    try:
        response = requests.post(
            f"{API_URL}/redes?fan_id={fan_id}",
            json=redes_data
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao adicionar redes sociais: {str(e)}")
        return None

def validar_redes(fan_id):
    """Valida as redes sociais de um fã"""
    try:
        response = requests.post(f"{API_URL}/redes/validar/{fan_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao validar redes sociais: {str(e)}")
        return None

def upload_documento(fan_id, file):
    """Faz upload de um documento para um fã"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_URL}/upload/{fan_id}", files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao fazer upload do documento: {str(e)}")
        return None

# Sidebar para navegação
st.sidebar.title("Projeto Furia")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/FURIA_Esports_logo.svg/1200px-FURIA_Esports_logo.svg.png", width=150)

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Cadastro de Fãs", "Gerenciar Redes Sociais", "Upload de Documentos"]
)

# Inicializar variáveis de sessão se não existirem
if 'last_fan_id' not in st.session_state:
    st.session_state.last_fan_id = 1

# Página principal - Dashboard
if menu == "Dashboard":
    st.title("Dashboard de Fãs - FURIA eSports")

    # Obter estatísticas
    stats = get_stats()

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Fãs", stats.get("total_fans", 0))

    # Obter dados para as outras métricas
    fans_data = get_fans(page_size=1000)

    with col2:
        # Calcular fãs com alto engajamento
        alto_engajamento = sum(1 for fan in fans_data.get("fans", []) if fan.get("engajamento") == "Alto")
        st.metric("Fãs com Alto Engajamento", alto_engajamento)

    with col3:
        # Calcular total de redes validadas
        total_redes_validadas = sum(fan.get("redes_validadas", 0) for fan in fans_data.get("fans", []))
        st.metric("Redes Sociais Validadas", total_redes_validadas)

    with col4:
        # Interesse mais popular
        interesse_popular = stats.get("top_interesses", [["N/A", 0]])[0][0] if stats.get("top_interesses") else "N/A"
        st.metric("Interesse Mais Popular", interesse_popular)

    # Filtros
    st.subheader("Filtros")

    # Barra de pesquisa
    search_query = st.text_input("🔍 Pesquisar por nome de fã")

    # Extrair todos os dados únicos para os filtros
    all_fans = fans_data.get("fans", [])

    # Coletar todos os valores únicos
    all_interesses = set()
    all_eventos = set()
    all_compras = set()

    for fan in all_fans:
        all_interesses.update(fan.get("interesses", []))
        all_eventos.update(fan.get("eventos", []))
        all_compras.update(fan.get("compras", []))

    # Criar colunas para os filtros com botões
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.write("**Filtrar por Interesse:**")
        interesse_filter = None
        interesse_buttons = ["Todos"] + sorted(list(all_interesses))
        for interesse in interesse_buttons:
            if st.button(interesse, key=f"int_{interesse}"):
                interesse_filter = None if interesse == "Todos" else interesse
                st.session_state.interesse_filter = interesse_filter

        # Mostrar filtro atual
        st.write(f"**Filtro atual:** {st.session_state.get('interesse_filter', 'Todos')}")

    with col2:
        st.write("**Filtrar por Evento:**")
        evento_filter = None
        evento_buttons = ["Todos"] + sorted(list(all_eventos))
        for evento in evento_buttons[:5]:  # Limitar para não sobrecarregar a UI
            if st.button(evento, key=f"evt_{evento}"):
                evento_filter = None if evento == "Todos" else evento
                st.session_state.evento_filter = evento_filter

        # Mostrar filtro atual
        st.write(f"**Filtro atual:** {st.session_state.get('evento_filter', 'Todos')}")

    with col3:
        st.write("**Filtrar por Compra:**")
        compra_filter = None
        compra_buttons = ["Todos"] + sorted(list(all_compras))
        for compra in compra_buttons[:5]:  # Limitar para não sobrecarregar a UI
            if st.button(compra, key=f"cmp_{compra}"):
                compra_filter = None if compra == "Todos" else compra
                st.session_state.compra_filter = compra_filter

        # Mostrar filtro atual
        st.write(f"**Filtro atual:** {st.session_state.get('compra_filter', 'Todos')}")

    with col4:
        st.write("**Filtrar por Engajamento:**")
        engajamento_filter = None
        for eng in ["Todos", "Alto", "Médio", "Baixo"]:
            if st.button(eng, key=f"eng_{eng}"):
                engajamento_filter = None if eng == "Todos" else eng
                st.session_state.engajamento_filter = engajamento_filter

        # Mostrar filtro atual
        st.write(f"**Filtro atual:** {st.session_state.get('engajamento_filter', 'Todos')}")

    # Botão para limpar todos os filtros
    if st.button("Limpar Todos os Filtros"):
        st.session_state.interesse_filter = None
        st.session_state.evento_filter = None
        st.session_state.compra_filter = None
        st.session_state.engajamento_filter = None
        st.experimental_rerun()

    # Obter dados filtrados
    filtered_fans = get_fans(
        interesse=st.session_state.get('interesse_filter'),
        evento=st.session_state.get('evento_filter'),
        compra=st.session_state.get('compra_filter'),
        engajamento=st.session_state.get('engajamento_filter'),
        nome=search_query
    )

    # Tabela de fãs
    fans_list = filtered_fans.get("fans", [])
    if fans_list:
        st.subheader(f"Fãs ({len(fans_list)})")

        # Converter para DataFrame para melhor visualização
        fans_df = pd.DataFrame([
            {
                "ID": fan.get("id"),
                "Nome": fan.get("nome"),
                "Interesses": ", ".join(fan.get("interesses", [])),
                "Eventos": len(fan.get("eventos", [])),
                "Compras": len(fan.get("compras", [])),
                "Redes Validadas": fan.get("redes_validadas", 0),
                "Engajamento": fan.get("engajamento", "Baixo")
            }
            for fan in fans_list
        ])

        # Adicionar estilo condicional
        def highlight_engajamento(val):
            if val == "Alto":
                return 'background-color: #a8f0a8'
            elif val == "Médio":
                return 'background-color: #f0f0a8'
            else:
                return 'background-color: #f0a8a8'

        # Exibir tabela estilizada
        st.dataframe(
            fans_df.style.applymap(
                highlight_engajamento,
                subset=["Engajamento"]
            ),
            height=400
        )

        # Visualizações
        st.subheader("Visualizações")

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de engajamento
            engajamento_counts = {
                "Alto": sum(1 for fan in fans_list if fan.get("engajamento") == "Alto"),
                "Médio": sum(1 for fan in fans_list if fan.get("engajamento") == "Médio"),
                "Baixo": sum(1 for fan in fans_list if fan.get("engajamento") == "Baixo")
            }

            fig = px.pie(
                names=list(engajamento_counts.keys()),
                values=list(engajamento_counts.values()),
                title="Distribuição de Engajamento",
                color=list(engajamento_counts.keys()),
                color_discrete_map={
                    "Alto": "#4CAF50",
                    "Médio": "#FFC107",
                    "Baixo": "#F44336"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Top interesses
            interesse_counts = {}
            for fan in fans_list:
                for interesse in fan.get("interesses", []):
                    interesse_counts[interesse] = interesse_counts.get(interesse, 0) + 1

            top_interesses = sorted(interesse_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            if top_interesses:
                fig = px.bar(
                    x=[item[0] for item in top_interesses],
                    y=[item[1] for item in top_interesses],
                    title="Top 5 Interesses",
                    labels={"x": "Interesse", "y": "Quantidade de Fãs"}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Não há dados suficientes para mostrar interesses")
    else:
        st.info("Nenhum fã encontrado com os filtros selecionados")

# Página de Cadastro de Fãs
elif menu == "Cadastro de Fãs":
    st.title("Cadastro de Fãs")

    with st.form("cadastro_form"):
        st.subheader("Informações Pessoais")
        nome = st.text_input("Nome Completo", max_chars=50)
        cpf = st.text_input("CPF (formato: 123.456.789-00)", max_chars=14)
        endereco = st.text_input("Endereço", max_chars=255)

        st.subheader("Preferências")
        atividades = st.multiselect(
            "Atividades",
            ["Streaming", "Cosplay", "Competições", "Colecionador", "Criação de Conteúdo"]
        )

        interesses = st.multiselect(
            "Interesses",
            ["CS:GO", "Valorant", "League of Legends", "Dota 2", "Rainbow Six", "Fortnite", "Overwatch"]
        )

        eventos = st.multiselect(
            "Eventos",
            ["CBLOL 2023", "Major CS:GO", "TI Dota", "Valorant Champions", "Brasil Game Show"]
        )

        compras = st.multiselect(
            "Compras",
            ["Camiseta FURIA", "Mousepad", "Boné", "Caneca", "Máscara", "Agasalho"]
        )

        submitted = st.form_submit_button("Cadastrar")

        if submitted:
            if not nome or not cpf or not endereco:
                st.error("Por favor, preencha todos os campos obrigatórios.")
            elif not interesses:
                st.error("Por favor, selecione pelo menos um interesse.")
            else:
                fan_data = {
                    "nome": nome,
                    "cpf": cpf,
                    "endereco": endereco,
                    "atividades": atividades,
                    "interesses": interesses,
                    "eventos": eventos,
                    "compras": compras
                }

                result = cadastrar_fan(fan_data)
                if result:
                    st.success(f"Fã cadastrado com sucesso! ID: {result.get('id')}")
                    st.session_state.last_fan_id = result.get('id')
                    st.info("Agora você pode adicionar redes sociais ou fazer upload de documentos.")

# Página de Gerenciamento de Redes Sociais
elif menu == "Gerenciar Redes Sociais":
    st.title("Gerenciar Redes Sociais")

    # Selecionar fã
    fan_id = st.number_input("ID do Fã", min_value=1, step=1, value=st.session_state.get('last_fan_id', 1))

    # Obter redes atuais
    redes_atuais = get_fan_redes(fan_id)

    if redes_atuais:
        st.subheader("Redes Sociais Atuais")

        redes_df = pd.DataFrame([
            {
                "ID": rede.get("id"),
                "Tipo": rede.get("tipo", "").capitalize(),
                "Link": rede.get("link"),
                "Validado": "✅" if rede.get("validado") else "❌"
            }
            for rede in redes_atuais
        ])

        st.dataframe(redes_df)

        if st.button("Validar Redes Sociais"):
            with st.spinner("Validando redes sociais..."):
                result = validar_redes(fan_id)
                if result:
                    st.success("Redes sociais validadas com sucesso!")
                    st.json(result)

    st.subheader("Adicionar/Atualizar Redes Sociais")

    with st.form("redes_form"):
        instagram = st.text_input("Instagram", placeholder="https://instagram.com/seuperfil")
        twitter = st.text_input("Twitter", placeholder="https://twitter.com/seuperfil")
        steam = st.text_input("Steam", placeholder="https://steamcommunity.com/id/seuperfil")
        gamersclub = st.text_input("Gamers Club", placeholder="https://gamersclub.com.br/player/seuperfil")

        submitted = st.form_submit_button("Salvar Redes Sociais")

        if submitted:
            redes_data = {
                "instagram": instagram,
                "twitter": twitter,
                "steam": steam,
                "gamersclub": gamersclub
            }

            # Remover campos vazios
            redes_data = {k: v for k, v in redes_data.items() if v}

            if not redes_data:
                st.error("Por favor, adicione pelo menos uma rede social.")
            else:
                result = adicionar_redes(fan_id, redes_data)
                if result:
                    st.success("Redes sociais atualizadas com sucesso!")
                    st.experimental_rerun()

# Página de Upload de Documentos
elif menu == "Upload de Documentos":
    st.title("Upload de Documentos")

    # Selecionar fã
    fan_id = st.number_input("ID do Fã", min_value=1, step=1, value=st.session_state.get('last_fan_id', 1))

    uploaded_file = st.file_uploader("Escolha um documento", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file is not None:
        # Exibir preview
        if uploaded_file.type.startswith('image'):
            st.image(uploaded_file, caption="Preview do documento", width=300)
        else:
            st.info(f"Arquivo PDF: {uploaded_file.name}")

        if st.button("Enviar Documento"):
            with st.spinner("Enviando documento..."):
                result = upload_documento(fan_id, uploaded_file)

                if result:
                    st.success("Documento enviado com sucesso!")

                    # Exibir resultado da validação
                    if result.get("validado"):
                        st.success("✅ Documento validado com sucesso!")
                    else:
                        st.error("❌ Documento não validado.")

                    st.json(result)

# Rodapé
st.sidebar.markdown("---")
st.sidebar.info("Projeto Furia - Dashboard de Fãs")
