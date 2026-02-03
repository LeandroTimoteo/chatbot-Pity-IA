import os
from dotenv import load_dotenv
from openai import OpenAI

# 🔐 Carrega variáveis do arquivo .env localizado na pasta 'env'
load_dotenv(dotenv_path=os.path.join("env", ".env"))

# 🔑 Obtém a chave da API
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("❌ Chave de API não encontrada. Verifique o arquivo env/.env e a variável OPENROUTER_API_KEY.")

# 🔗 Inicializa o cliente da OpenRouter
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

# 🧠 Histórico de conversa para manter o contexto
conversa_pt = [
    {"role": "system", "content": "Você é um assistente útil, amigável e profissional que responde em português do Brasil. Responda de forma clara, concisa e sempre ajudando o usuário."}
]

conversa_en = [
    {"role": "system", "content": "You are a helpful, friendly and professional assistant that responds in English. Answer clearly, concisely and always help the user."}
]

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
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # ✅ modelo confiável
            messages=conversa_atual,
            temperature=0.7,
            max_tokens=500
        )

        # Extrai a resposta
        resposta_idioma = response.choices[0].message.content.strip()
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
        
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_traducao}],
            temperature=0.3,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
    except:
        return texto  # Retorna texto original se tradução falhar










