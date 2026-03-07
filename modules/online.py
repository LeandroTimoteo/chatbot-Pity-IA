import os
from pathlib import Path
import requests

try:
    from dotenv import load_dotenv
except ImportError:  # fallback quando python-dotenv nao estiver instalado
    load_dotenv = None


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()

# 🔐 Carrega variáveis do .env com fallback para diferentes locais
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

# 🔑 Obtém a chave da API
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("❌ Chave de API não encontrada. Defina OPENROUTER_API_KEY no .env.")

OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-nano-30b-a3b:free")
FALLBACK_MODELS = [
    OPENROUTER_MODEL,
    "nvidia/nemotron-nano-9b-v2:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
]

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": os.getenv("APP_PUBLIC_URL", "http://localhost"),
    "X-Title": os.getenv("APP_NAME", "Chatbot Pity IA"),
}

# 🧠 Histórico de conversa para manter o contexto
conversa_pt = [
    {"role": "system", "content": "Você é um assistente útil, amigável e profissional que responde em português do Brasil. Responda de forma clara, concisa e sempre ajudando o usuário."}
]

conversa_en = [
    {"role": "system", "content": "You are a helpful, friendly and professional assistant that responds in English. Answer clearly, concisely and always help the user."}
]


def _chat_completion(messages, temperature=0.7, max_tokens=500):
    last_error = None
    for model in dict.fromkeys(FALLBACK_MODELS):
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            response = requests.post(
                OPENROUTER_API_URL,
                headers=OPENROUTER_HEADERS,
                json=payload,
                timeout=90,
            )
            if response.status_code >= 400:
                raise RuntimeError(
                    f"Error code: {response.status_code} - {response.text}"
                )
            return response.json()
        except Exception as exc:
            last_error = exc
            continue
    raise last_error if last_error else RuntimeError("Falha na chamada de API.")

def gerar_resposta_online(prompt: str, idioma: str = "pt") -> dict:
    """
    Gera uma resposta bilíngue usando o modelo de IA do OpenRouter.

    Args:
        prompt (str): A pergunta ou mensagem do usuário.
        idioma (str): Idioma da resposta ("pt" para português, "en" para inglês)

    Returns:
        dict: Um dicionário com respostas em português e inglês.
    """
    try:
        # Seleciona o histórico baseado no idioma
        conversa_atual = conversa_pt if idioma == "pt" else conversa_en
        
        # Adiciona a entrada do usuário ao histórico
        conversa_atual.append({"role": "user", "content": prompt})

        # 🔁 Limita o histórico a 20 mensagens (mantém o system + últimas 19)
        if len(conversa_atual) > 20:
            conversa_atual[:] = [conversa_atual[0]] + conversa_atual[-19:]

        # Chamada à API para obter resposta
        response = _chat_completion(
            messages=conversa_atual,
            temperature=0.7,
            max_tokens=500,
        )

        # Extrai a resposta
        resposta_idioma = response["choices"][0]["message"]["content"].strip()
        conversa_atual.append({"role": "assistant", "content": resposta_idioma})
        
        # Se resposta em português, traduz para inglês e vice-versa
        if idioma == "pt":
            resposta_pt = resposta_idioma
            resposta_en = traduzir_resposta(resposta_idioma, "pt_to_en")
        else:
            resposta_en = resposta_idioma
            resposta_pt = traduzir_resposta(resposta_idioma, "en_to_pt")
        
        return {
            "pt": resposta_pt,
            "en": resposta_en,
            "sucesso": True
        }

    except Exception as e:
        return {
            "pt": f"⚠️ Erro ao gerar resposta: {str(e)}",
            "en": f"⚠️ Error generating response: {str(e)}",
            "sucesso": False
        }

def traduzir_resposta(texto: str, direcao: str) -> str:
    """
    Traduz a resposta para o outro idioma usando a API.
    
    Args:
        texto (str): Texto a ser traduzido
        direcao (str): Direção da tradução ("pt_to_en" ou "en_to_pt")
    
    Returns:
        str: Texto traduzido
    """
    try:
        prompt_traducao = f"Traduza este texto para {'inglês' if direcao == 'pt_to_en' else 'português'}:\n\n{texto}\n\nApenas forneça a tradução, sem explicações adicionais."
        
        response = _chat_completion(
            messages=[{"role": "user", "content": prompt_traducao}],
            temperature=0.3,
            max_tokens=300,
        )
        
        return response["choices"][0]["message"]["content"].strip()
    except:
        return texto  # Retorna texto original se tradução falhar




