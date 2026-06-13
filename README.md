<div align="center">

# 🤖 Pity-IA Studio

### Assistente de IA Bilíngue com Interface Premium

[![Open App](https://img.shields.io/badge/🚀_Abrir_App-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://chatbot-pity-ia-nbnhnjscbk8htyftxdzxm5.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.56+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-Web_API-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI_API-6366F1?style=flat-square&logo=openai&logoColor=white)](https://openrouter.ai)
[![License](https://img.shields.io/badge/Licença-MIT-22C55E?style=flat-square)](LICENSE)
[![Security](https://img.shields.io/badge/Segurança-Hardened-0EA5E9?style=flat-square&logo=shield&logoColor=white)](#-segurança)

<br>

<a href="https://chatbot-pity-ia-nbnhnjscbk8htyftxdzxm5.streamlit.app/" target="_blank">
  <img src="https://github.com/LeandroTimoteo/chatbot-Pity-IA/blob/main/images/Copilot_20250921_194729.png?raw=true" width="720" alt="Pity-IA Studio — Preview da interface do chatbot" />
</a>

<br>

**[🚀 Abrir Pity-IA Studio](https://chatbot-pity-ia-nbnhnjscbk8htyftxdzxm5.streamlit.app/)** · **[📋 Reportar Bug](https://github.com/LeandroTimoteo/chatbot-Pity-IA/issues)** · **[💡 Sugerir Feature](https://github.com/LeandroTimoteo/chatbot-Pity-IA/issues)**

</div>

---

## ✨ Funcionalidades

| Feature | Descrição |
|---------|-----------|
| 🇧🇷🇺🇸 **Bilíngue** | Respostas automáticas em Português e Inglês com tradução em tempo real |
| 🎤 **Entrada por Voz** | Grave áudio direto no navegador — transcrição automática via Google Speech |
| 🔊 **Saída por Voz** | Ouça respostas em áudio sintetizado (TTS) com seleção inteligente de voz |
| 🎨 **Design Premium** | Interface glassmorphism com gradientes, animações e modo responsivo |
| 🔒 **Segurança** | Proteção XSS, sessões isoladas, rate limiting, validação de input |
| 💾 **Histórico** | Contexto de conversa por sessão com limite inteligente de mensagens |
| ⚡ **Multi-modelo** | Fallback automático entre modelos de IA via OpenRouter |

---

## 🚀 Demo ao Vivo

<div align="center">

### 👉 [**Acesse o Pity-IA Studio agora**](https://chatbot-pity-ia-nbnhnjscbk8htyftxdzxm5.streamlit.app/) 👈

*Hospedado no Streamlit Cloud · Sem instalação necessária*

</div>

---

## 🛠️ Instalação Local

### Pré-requisitos

- Python 3.10+
- Chave de API do [OpenRouter](https://openrouter.ai) (plano gratuito disponível)

### Setup

```bash
# 1. Clone o repositório
git clone https://github.com/LeandroTimoteo/chatbot-Pity-IA.git
cd chatbot-Pity-IA

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
#    Crie um arquivo .env na raiz do projeto:
echo OPENROUTER_API_KEY=sua_chave_aqui > .env
echo OPENROUTER_MODEL=nvidia/nemotron-3-nano-30b-a3b:free >> .env
```

### Executar

```bash
# Streamlit (recomendado)
streamlit run modules/app.py --server.port 8502

# FastAPI (alternativo)
python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8503 --reload
```

Acesse: **http://localhost:8502** (Streamlit) ou **http://localhost:8503** (FastAPI)

---

## ☁️ Deploy no Streamlit Cloud

1. Faça fork ou push do repositório para o GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Clique em **"New app"** e selecione o repositório
4. Defina o caminho do app: `modules/app.py`
5. Em **Secrets**, adicione:
   ```toml
   OPENROUTER_API_KEY = "sua_chave_aqui"
   ```
6. Clique em **Deploy!**

---

## 🔒 Segurança

O Pity-IA Studio implementa múltiplas camadas de segurança:

| Proteção | Detalhes |
|----------|----------|
| **XSS Prevention** | Todo input do usuário é escapado com `html.escape()` antes da renderização |
| **Sessões Isoladas** | Cada usuário tem seu próprio histórico de conversa via `st.session_state` |
| **Rate Limiting** | Máximo de 30 mensagens por minuto por sessão/IP |
| **Input Validation** | Prompts limitados a 4.000 caracteres com sanitização |
| **XSRF Protection** | Habilitado via configuração do Streamlit |
| **Security Headers** | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` (FastAPI) |
| **CORS Restrito** | Apenas origens autorizadas podem acessar a API |
| **Secrets Management** | Chaves de API gerenciadas via `st.secrets` / variáveis de ambiente |

---

## 📁 Estrutura do Projeto

```
chatbot-Pity-IA/
├── modules/
│   ├── app.py              # 🎨 App principal Streamlit (UI + segurança)
│   ├── online.py           # 🧠 Integração com OpenRouter API
│   ├── speak.py            # 🔊 Síntese de fala (gTTS)
│   ├── transcribe.py       # 🎤 Transcrição de áudio (SpeechRecognition)
│   └── gemini_response.py  # 🔮 Módulo Gemini (alternativo)
├── web/
│   ├── index.html          # 🌐 Frontend FastAPI
│   └── static/
│       ├── app.css         # 🎨 Estilos premium
│       └── app.js          # ⚡ Lógica do frontend
├── fastapi_app.py          # 🚀 API REST com FastAPI
├── .streamlit/
│   ├── config.toml         # ⚙️ Configuração local
│   └── cloud.toml          # ☁️ Configuração do Cloud
├── requirements.txt        # 📦 Dependências Python
├── .gitignore              # 🚫 Arquivos ignorados pelo Git
├── LICENSE                 # 📄 Licença MIT
└── README.md               # 📖 Este arquivo
```

---

## 🧰 Tech Stack

<div align="center">

| Camada | Tecnologia | Uso |
|--------|-----------|-----|
| **Frontend** | Streamlit | Interface principal do chatbot |
| **Frontend Alt.** | HTML/CSS/JS | Interface FastAPI com glassmorphism |
| **Backend** | FastAPI | API REST alternativa |
| **IA** | OpenRouter API | Acesso a modelos (Nemotron, etc.) |
| **TTS** | gTTS | Síntese de fala em múltiplos idiomas |
| **STT** | SpeechRecognition | Transcrição de áudio |
| **Deploy** | Streamlit Cloud | Hospedagem gratuita |

</div>

---

## 📝 Exemplos de Uso

```
💬 "Crie um plano de estudos para Python em 30 dias"
💬 "Explique o que é uma API REST de forma simples"
💬 "Resuma este texto em 5 linhas"
💬 "Create a marketing strategy for a small business"
💬 "Explain the difference between SQL and NoSQL"
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um **Fork** do projeto
2. Crie sua **Feature Branch** (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: adicionar MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um **Pull Request**

---

## 👤 Autor

<div align="center">

**Leandro Timoteo Silva**

Software Engineer

[![GitHub](https://img.shields.io/badge/GitHub-@LeandroTimoteo-181717?style=flat-square&logo=github)](https://github.com/LeandroTimoteo)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Leandro_Timóteo-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/leandro-timóteo-ads)
[![Email](https://img.shields.io/badge/Email-leandrinhots6@gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:leandrinhots6@gmail.com)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-+55_83_98783--0223-25D366?style=flat-square&logo=whatsapp&logoColor=white)](https://wa.me/5583987830223)

</div>

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

**Desenvolvido com ❤️ por [Leandro Timoteo](https://github.com/LeandroTimoteo)**

⭐ Se este projeto te ajudou, considere dar uma estrela no GitHub!

</div>
