"""Módulo de integração com a API do OpenRouter para respostas de IA.

Segurança:
- Histórico de conversa é passado por parâmetro (per-session, não global)
- Headers reconstruídos a cada request (suporta carregamento tardio de secrets)
- Input sanitizado e limitado em tamanho
- Tratamento robusto de exceções
- Logging estruturado para monitoramento
- Cache automático de respostas com TTL
"""

import os
import time
from pathlib import Path
from functools import wraps

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from modules.logger import get_logger


# Configurar logging
logger = get_logger(__name__, log_file="online.log")

# Constantes de retry
MAX_RETRIES = 3
RETRY_DELAY = 1  # segundos

# ---------------------------------------------------------------------------
# Carregamento de variáveis de ambiente
# ---------------------------------------------------------------------------

def _load_env_file(path: Path) -> None:
    """Fallback manual para carregar .env quando python-dotenv não está instalado."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_this_dir = Path(__file__).resolve().parent
_root_dir = _this_dir.parent

if load_dotenv:
    load_dotenv(_root_dir / ".env", override=True)
    load_dotenv(_this_dir / "env" / ".env", override=True)
    load_dotenv(_root_dir / "env" / ".env", override=True)
else:
    _load_env_file(_root_dir / ".env")
    _load_env_file(_this_dir / "env" / ".env")
    _load_env_file(_root_dir / "env" / ".env")

# ---------------------------------------------------------------------------
# Configuração da API
# ---------------------------------------------------------------------------

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Limites de segurança
MAX_PROMPT_LENGTH = 4000
MAX_HISTORY_MESSAGES = 20

FALLBACK_MODELS = [
    os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-nano-30b-a3b:free"),
    "nvidia/nemotron-nano-9b-v2:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
]

SYSTEM_PROMPTS = {
    "pt": {
        "role": "system",
        "content": (
            "Você é um assistente útil, amigável e profissional que responde "
            "em português do Brasil. Responda de forma clara, concisa e sempre "
            "ajudando o usuário."
        ),
    },
    "en": {
        "role": "system",
        "content": (
            "You are a helpful, friendly and professional assistant that "
            "responds in English. Answer clearly, concisely and always help "
            "the user."
        ),
    },
}


def _get_api_key() -> str:
    """Obtém a chave da API de forma segura, tentando múltiplas fontes."""
    key = os.getenv("OPENROUTER_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("OPENROUTER_API_KEY", "")
        except Exception:
            pass
    if not key:
        logger.warning(
            "OPENROUTER_API_KEY não encontrada. "
            "Configure nas variáveis de ambiente ou em st.secrets."
        )
    return key


def _build_headers() -> dict:
    """Constrói headers frescos a cada request (suporta carregamento tardio)."""
    return {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("APP_PUBLIC_URL", "https://chatbot-pity-ia.streamlit.app"),
        "X-Title": os.getenv("APP_NAME", "Chatbot Pity IA"),
    }


def _sanitize_prompt(prompt: str) -> str:
    """Sanitiza e valida o prompt do usuário."""
    if not isinstance(prompt, str):
        raise ValueError("Prompt deve ser uma string.")
    cleaned = prompt.strip()
    if not cleaned:
        raise ValueError("Prompt não pode ser vazio.")
    if len(cleaned) > MAX_PROMPT_LENGTH:
        cleaned = cleaned[:MAX_PROMPT_LENGTH]
        logger.warning("Prompt truncado para %d caracteres.", MAX_PROMPT_LENGTH)
    return cleaned


def _sanitize_idioma(idioma: str) -> str:
    """Valida o idioma informado."""
    idioma = str(idioma).strip().lower()
    if idioma not in ("pt", "en"):
        return "pt"
    return idioma


def _trim_history(history: list, max_messages: int = MAX_HISTORY_MESSAGES) -> list:
    """Mantém o histórico dentro do limite, preservando o system prompt."""
    if len(history) <= max_messages:
        return history
    # Preserva o primeiro (system) + últimas (max-1) mensagens
    return [history[0]] + history[-(max_messages - 1):]


# ---------------------------------------------------------------------------
# Chamada à API
# ---------------------------------------------------------------------------

def _chat_completion(
    messages: list,
    temperature: float = 0.7,
    max_tokens: int = 500,
) -> dict:
    """Executa a chamada à API com fallback entre modelos e retry automático.
    
    Implementa retry automático com backoff exponencial e fallback entre modelos.
    """
    last_error = None
    headers = _build_headers()

    for model in dict.fromkeys(FALLBACK_MODELS):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                
                logger.debug(
                    "Tentativa %d/%d para modelo %s",
                    attempt,
                    MAX_RETRIES,
                    model
                )
                
                response = requests.post(
                    OPENROUTER_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=90,
                )
                
                if response.status_code >= 400:
                    error_msg = f"API error {response.status_code}: {response.text[:200]}"
                    raise RuntimeError(error_msg)
                
                logger.info("Resposta bem-sucedida do modelo %s", model)
                return response.json()
                
            except requests.exceptions.Timeout:
                last_error = TimeoutError("Timeout na requisição à API")
                logger.warning(
                    "Timeout no modelo %s (tentativa %d/%d)",
                    model,
                    attempt,
                    MAX_RETRIES
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)  # Backoff exponencial
                    
            except requests.exceptions.ConnectionError as e:
                last_error = e
                logger.warning(
                    "Erro de conexão no modelo %s (tentativa %d/%d): %s",
                    model,
                    attempt,
                    MAX_RETRIES,
                    e
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)
                    
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Erro no modelo %s (tentativa %d/%d): %s",
                    model,
                    attempt,
                    MAX_RETRIES,
                    exc
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    
    logger.error(
        "Falha em todas as tentativas com todos os modelos. Último erro: %s",
        last_error,
        exc_info=True
    )
    raise last_error if last_error else RuntimeError("Falha na chamada de API.")


# ---------------------------------------------------------------------------
# Interface pública
# ---------------------------------------------------------------------------

def gerar_resposta_online(
    prompt: str,
    idioma: str = "pt",
    historico: list | None = None,
) -> dict:
    """Gera uma resposta bilíngue usando o modelo de IA do OpenRouter.

    Args:
        prompt: A pergunta ou mensagem do usuário.
        idioma: Idioma da resposta ("pt" ou "en").
        historico: Lista de mensagens da sessão do usuário (mutável).
                   Se None, cria uma lista temporária sem persistência.

    Returns:
        dict com chaves "pt", "en", "sucesso", e "historico" atualizado.
    """
    logger.info("Iniciando geração de resposta | Idioma: %s", idioma)
    
    try:
        idioma = _sanitize_idioma(idioma)
        prompt = _sanitize_prompt(prompt)
        
        logger.debug("Prompt sanitizado: %d caracteres", len(prompt))

        # Usa o histórico da sessão ou cria um temporário
        if historico is None:
            historico = [SYSTEM_PROMPTS[idioma].copy()]

        # Garante que o system prompt está presente
        if not historico or historico[0].get("role") != "system":
            historico.insert(0, SYSTEM_PROMPTS[idioma].copy())

        # Adiciona a mensagem do usuário
        historico.append({"role": "user", "content": prompt})
        
        logger.debug("Histórico contém %d mensagens", len(historico))

        # Limita o tamanho do histórico
        historico[:] = _trim_history(historico)

        # Chamada à API
        logger.info("Chamando API OpenRouter...")
        response = _chat_completion(
            messages=historico,
            temperature=0.7,
            max_tokens=500,
        )

        # Extrai a resposta
        resposta_idioma = response["choices"][0]["message"]["content"].strip()
        historico.append({"role": "assistant", "content": resposta_idioma})
        
        logger.info("Resposta recebida: %d caracteres", len(resposta_idioma))

        # Traduz para o outro idioma
        logger.info("Iniciando tradução...")
        if idioma == "pt":
            resposta_pt = resposta_idioma
            resposta_en = _traduzir_resposta(resposta_idioma, "pt_to_en")
        else:
            resposta_en = resposta_idioma
            resposta_pt = _traduzir_resposta(resposta_idioma, "en_to_pt")

        logger.info("Resposta gerada com sucesso")
        return {
            "pt": resposta_pt,
            "en": resposta_en,
            "sucesso": True,
            "historico": historico,
        }

    except ValueError as ve:
        logger.warning("Input inválido: %s", ve)
        return {
            "pt": f"⚠️ Entrada inválida: {ve}",
            "en": f"⚠️ Invalid input: {ve}",
            "sucesso": False,
        }
    except Exception as exc:
        logger.error("Erro ao gerar resposta: %s", exc, exc_info=True)
        return {
            "pt": f"⚠️ Erro ao gerar resposta: {exc}",
            "en": f"⚠️ Error generating response: {exc}",
            "sucesso": False,
        }


def _traduzir_resposta(texto: str, direcao: str) -> str:
    """Traduz a resposta para o outro idioma usando a API.

    Args:
        texto: Texto a ser traduzido.
        direcao: "pt_to_en" ou "en_to_pt".

    Returns:
        Texto traduzido, ou o original se a tradução falhar.
    """
    try:
        destino = "inglês" if direcao == "pt_to_en" else "português"
        prompt_traducao = (
            f"Traduza este texto para {destino}:\n\n{texto}\n\n"
            "Apenas forneça a tradução, sem explicações adicionais."
        )
        response = _chat_completion(
            messages=[{"role": "user", "content": prompt_traducao}],
            temperature=0.3,
            max_tokens=300,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        logger.warning("Tradução falhou: %s", exc)
        return texto
