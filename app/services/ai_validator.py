import spacy
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Callable, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carregar o modelo do spaCy
try:
    nlp = spacy.load("pt_core_news_sm")
    logger.info("Modelo pt_core_news_sm carregado com sucesso")
except:
    try:
        nlp = spacy.load("en_core_web_sm")
        logger.info("Modelo en_core_web_sm carregado como fallback")
    except Exception as e:
        logger.error(f"Erro ao carregar modelos spaCy: {str(e)}")
        raise

# Configuração do Selenium
def criar_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        logger.error(f"Erro ao criar driver Selenium: {str(e)}")
        return None

# Extratores específicos para cada rede social usando Selenium
def extrair_instagram_selenium(driver, url):
    try:
        driver.get(url)
        # Aguardar carregamento da página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        # Dar tempo para carregar conteúdo dinâmico
        time.sleep(3)

        # Extrair bio
        bio_elements = driver.find_elements(By.XPATH, "//header//div[contains(@class, 'bio')]")
        # Extrair posts (legendas)
        post_elements = driver.find_elements(By.XPATH, "//article//div[contains(@class, 'caption')]")

        textos = []
        for elem in bio_elements:
            textos.append(elem.text)
        for elem in post_elements:
            textos.append(elem.text)

        # Se não encontrou nada específico, pegar todo o texto da página
        if not textos:
            textos.append(driver.find_element(By.TAG_NAME, "body").text)

        return " ".join(textos)
    except Exception as e:
        logger.error(f"Erro ao extrair Instagram: {str(e)}")
        return driver.page_source  # Retorna o HTML para análise com BeautifulSoup como fallback

def extrair_twitter_selenium(driver, url):
    try:
        driver.get(url)
        # Aguardar carregamento da página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        # Dar tempo para carregar conteúdo dinâmico
        time.sleep(3)

        # Extrair bio
        bio_elements = driver.find_elements(By.XPATH, "//div[@data-testid='UserDescription']")
        # Extrair tweets
        tweet_elements = driver.find_elements(By.XPATH, "//article//div[@data-testid='tweetText']")

        textos = []
        for elem in bio_elements:
            textos.append(elem.text)
        for elem in tweet_elements:
            textos.append(elem.text)

        # Se não encontrou nada específico, pegar todo o texto da página
        if not textos:
            textos.append(driver.find_element(By.TAG_NAME, "body").text)

        return " ".join(textos)
    except Exception as e:
        logger.error(f"Erro ao extrair Twitter: {str(e)}")
        return driver.page_source  # Retorna o HTML para análise com BeautifulSoup como fallback

def extrair_steam_selenium(driver, url):
    try:
        driver.get(url)
        # Aguardar carregamento da página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "profile_page"))
        )

        # Extrair bio
        bio_elements = driver.find_elements(By.CLASS_NAME, "profile_summary")
        # Extrair jogos
        game_elements = driver.find_elements(By.CLASS_NAME, "game_name")

        textos = []
        for elem in bio_elements:
            textos.append(elem.text)
        for elem in game_elements:
            textos.append(elem.text)

        # Se não encontrou nada específico, pegar todo o texto da página
        if not textos:
            textos.append(driver.find_element(By.TAG_NAME, "body").text)

        return " ".join(textos)
    except Exception as e:
        logger.error(f"Erro ao extrair Steam: {str(e)}")
        return driver.page_source  # Retorna o HTML para análise com BeautifulSoup como fallback

def extrair_gamersclub_selenium(driver, url):
    try:
        driver.get(url)
        # Aguardar carregamento da página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "player-info"))
        )

        # Extrair estatísticas
        stats_elements = driver.find_elements(By.CLASS_NAME, "player-stats")
        # Extrair jogos
        game_elements = driver.find_elements(By.CLASS_NAME, "game-item")

        textos = []
        for elem in stats_elements:
            textos.append(elem.text)
        for elem in game_elements:
            textos.append(elem.text)

        # Se não encontrou nada específico, pegar todo o texto da página
        if not textos:
            textos.append(driver.find_element(By.TAG_NAME, "body").text)

        return " ".join(textos)
    except Exception as e:
        logger.error(f"Erro ao extrair Gamers Club: {str(e)}")
        return driver.page_source  # Retorna o HTML para análise com BeautifulSoup como fallback

# Extratores com BeautifulSoup como fallback
def extrair_instagram(soup: BeautifulSoup) -> str:
    bio = soup.select_one('header section div')
    posts = soup.select('article div > span')
    textos = []
    if bio:
        textos.append(bio.get_text())
    for post in posts:
        textos.append(post.get_text())
    return " ".join(textos)

def extrair_twitter(soup: BeautifulSoup) -> str:
    tweets = soup.select('article')
    bio = soup.select_one('div[data-testid="UserDescription"]')
    textos = []
    if bio:
        textos.append(bio.get_text())
    for tweet in tweets:
        textos.append(tweet.get_text())
    return " ".join(textos)

def extrair_steam(soup: BeautifulSoup) -> str:
    bio = soup.select_one('.profile_summary')
    games = soup.select('.game_name')
    textos = []
    if bio:
        textos.append(bio.get_text())
    for game in games:
        textos.append(game.get_text())
    return " ".join(textos)

def extrair_gamersclub(soup: BeautifulSoup) -> str:
    stats = soup.select('.player-stats')
    games = soup.select('.game-item')
    textos = []
    for stat in stats:
        textos.append(stat.get_text())
    for game in games:
        textos.append(game.get_text())
    return " ".join(textos)

EXTRATORES: Dict[str, Callable[[BeautifulSoup], str]] = {
    "instagram": extrair_instagram,
    "twitter": extrair_twitter,
    "steam": extrair_steam,
    "gamersclub": extrair_gamersclub
}

SELENIUM_EXTRATORES: Dict[str, Callable[[webdriver.Chrome, str], str]] = {
    "instagram": extrair_instagram_selenium,
    "twitter": extrair_twitter_selenium,
    "steam": extrair_steam_selenium,
    "gamersclub": extrair_gamersclub_selenium
}

def extrair_conteudo_do_perfil(link: str, tipo_rede: str) -> str:
    logger.info(f"Iniciando extração de conteúdo para {tipo_rede}: {link}")

    # Primeiro, tentar com Selenium
    try:
        driver = criar_driver()
        if driver:
            logger.info(f"Usando Selenium para extrair conteúdo de {tipo_rede}")
            extrator_selenium = SELENIUM_EXTRATORES.get(tipo_rede)
            if extrator_selenium:
                conteudo = extrator_selenium(driver, link)
                driver.quit()
                if conteudo:
                    logger.info(f"Extração com Selenium bem-sucedida para {tipo_rede}")
                    return conteudo
            driver.quit()
    except Exception as e:
        logger.error(f"Erro ao usar Selenium: {str(e)}")
        if 'driver' in locals() and driver:
            driver.quit()

    # Fallback para BeautifulSoup
    logger.info(f"Usando BeautifulSoup como fallback para {tipo_rede}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(link, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Status code não-200 recebido: {response.status_code}")
            return ""

        soup = BeautifulSoup(response.text, 'html.parser')

        for script in soup(["script", "style"]):
            script.extract()

        extrator = EXTRATORES.get(tipo_rede)
        if extrator:
            conteudo = extrator(soup)
            if conteudo:
                logger.info(f"Extração com BeautifulSoup bem-sucedida para {tipo_rede}")
                return conteudo

        # Extração genérica como último recurso
        logger.info("Usando extração genérica de texto")
        return soup.get_text(separator=' ', strip=True)[:5000]

    except Exception as e:
        logger.error(f"Erro ao extrair conteúdo com BeautifulSoup: {str(e)}")
        return ""

def validar_conteudo_com_ia(conteudo: str, interesses: list) -> dict:
    if not conteudo:
        return {
            "relevante": False,
            "confianca": 0.0,
            "motivo": "Não foi possível extrair conteúdo do perfil"
        }

    logger.info(f"Validando conteúdo com IA (tamanho: {len(conteudo)} caracteres)")
    doc = nlp(conteudo.lower())

    palavras_chave_esports = [
        "game", "gaming", "esport", "esports", "tournament", "torneio",
        "competição", "competicao", "player", "jogador", "team", "equipe",
        "match", "partida", "furia", "cs:go", "csgo", "counter-strike",
        "league of legends", "lol", "dota", "valorant", "overwatch",
        "fps", "moba", "battle royale", "streamer", "streaming"
    ]

    interesses_lower = [interesse.lower() for interesse in interesses]

    palavras_encontradas = []
    interesses_encontrados = []

    for token in doc:
        if token.text in palavras_chave_esports:
            palavras_encontradas.append(token.text)
        if token.text in interesses_lower:
            interesses_encontrados.append(token.text)

    palavras_encontradas = list(set(palavras_encontradas))
    interesses_encontrados = list(set(interesses_encontrados))

    logger.info(f"Palavras-chave encontradas: {palavras_encontradas}")
    logger.info(f"Interesses encontrados: {interesses_encontrados}")

    pontuacao_palavras = len(palavras_encontradas) * 0.5
    pontuacao_interesses = len(interesses_encontrados) * 1.0
    pontuacao_total = pontuacao_palavras + pontuacao_interesses

    confianca = min(pontuacao_total / 5.0, 1.0)

    relevante = confianca >= 0.3

    if relevante:
        motivo = f"Perfil contém termos de e-sports ({', '.join(palavras_encontradas)})"
        if interesses_encontrados:
            motivo += f" e interesses do usuário ({', '.join(interesses_encontrados)})"
    else:
        motivo = "Perfil não contém conteúdo relevante de e-sports ou relacionado aos interesses do usuário"

    logger.info(f"Resultado da validação: relevante={relevante}, confiança={confianca}")

    return {
        "relevante": relevante,
        "confianca": round(confianca, 2),
        "motivo": motivo,
        "palavras_encontradas": palavras_encontradas,
        "interesses_encontrados": interesses_encontrados
    }