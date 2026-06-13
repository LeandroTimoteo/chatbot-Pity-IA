<div align="center">

# 🤖 Pity-IA Studio

### Bilingual AI Assistant with Premium Interface

[![Open App](https://img.shields.io/badge/🚀_Open_App-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://chatbot-pity-ia-nbnhnjscbk8htyftxdzxm5.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.56+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-Web_API-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI_API-6366F1?style=flat-square&logo=openai&logoColor=white)](https://openrouter.ai)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Hardened-0EA5E9?style=flat-square&logo=shield&logoColor=white)](#-security)

<br>

<a href="https://chatbot-pity-ia-nbnhnjscbk8htyftxdzxm5.streamlit.app/" target="_blank">
  <img src="https://github.com/LeandroTimoteo/chatbot-Pity-IA/blob/main/images/Copilot_20250921_194729.png?raw=true" width="720" alt="Pity-IA Studio — Chatbot Interface Preview" />
</a>

<br>

**[🚀 Open Pity-IA Studio](https://chatbot-pity-ia-nbnhnjscbk8htyftxdzxm5.streamlit.app/)** · **[📋 Report Bug](https://github.com/LeandroTimoteo/chatbot-Pity-IA/issues)** · **[💡 Suggest Feature](https://github.com/LeandroTimoteo/chatbot-Pity-IA/issues)**

</div>

---

## ✨ Features

| Feature | Description |
|---------|-----------|
| 🇧🇷🇺🇸 **Bilingual** | Automatic responses in Portuguese and English with real-time translation |
| 🎤 **Voice Input** | Record audio directly in the browser — automatic transcription via Google Speech |
| 🔊 **Voice Output** | Listen to synthesized audio responses (TTS) with smart voice selection |
| 🎨 **Premium Design** | Glassmorphism interface with gradients, animations, and responsive mode |
| 🔒 **Security** | XSS protection, isolated sessions, rate limiting, and input validation |
| 💾 **History** | Conversation context per session with smart message limits |
| ⚡ **Multi-model** | Automatic fallback between AI models via OpenRouter |

---

## 🚀 Live Demo

<div align="center">

### 👉 [**Access Pity-IA Studio now**](https://chatbot-pity-ia-nbnhnjscbk8htyftxdzxm5.streamlit.app/) 👈

*Hosted on Streamlit Cloud · No installation required*

</div>

---

## 🛠️ Local Installation

### Prerequisites

- Python 3.10+
- [OpenRouter](https://openrouter.ai) API Key (free plan available)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/LeandroTimoteo/chatbot-Pity-IA.git
cd chatbot-Pity-IA

# 2. Create and activate the virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
#    Create a .env file in the project root:
echo OPENROUTER_API_KEY=your_key_here > .env
echo OPENROUTER_MODEL=nvidia/nemotron-3-nano-30b-a3b:free >> .env
```

### Run

```bash
# Streamlit (recommended)
streamlit run modules/app.py --server.port 8502

# FastAPI (alternative)
python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8503 --reload
```

Access: **http://localhost:8502** (Streamlit) or **http://localhost:8503** (FastAPI)

---

## ☁️ Deployment on Streamlit Cloud

1. Fork or push the repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click on **"New app"** and select the repository
4. Set the app path: `modules/app.py`
5. In **Secrets**, add:
   ```toml
   OPENROUTER_API_KEY = "your_key_here"
   ```
6. Click on **Deploy!**

---

## 🔒 Security

Pity-IA Studio implements multiple security layers:

| Protection | Details |
|----------|----------|
| **XSS Prevention** | All user input is escaped with `html.escape()` before rendering |
| **Isolated Sessions** | Each user has their own conversation history via `st.session_state` |
| **Rate Limiting** | Maximum of 30 messages per minute per session/IP |
| **Input Validation** | Prompts limited to 4,000 characters with sanitization |
| **XSRF Protection** | Enabled via Streamlit configuration |
| **Security Headers** | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` (FastAPI) |
| **Strict CORS** | Only authorized origins can access the API |
| **Secrets Management** | API keys managed via `st.secrets` / environment variables |

---

## 📁 Project Structure

```text
chatbot-Pity-IA/
├── modules/
│   ├── app.py              # 🎨 Main Streamlit App (UI + security)
│   ├── online.py           # 🧠 Integration with OpenRouter API
│   ├── speak.py            # 🔊 Speech synthesis (gTTS)
│   ├── transcribe.py       # 🎤 Audio transcription (SpeechRecognition)
│   └── gemini_response.py  # 🔮 Gemini module (alternative)
├── web/
│   ├── index.html          # 🌐 FastAPI Frontend
│   └── static/
│       ├── app.css         # 🎨 Premium styles
│       └── app.js          # ⚡ Frontend logic
├── fastapi_app.py          # 🚀 REST API with FastAPI
├── .streamlit/
│   ├── config.toml         # ⚙️ Local configuration
│   └── cloud.toml          # ☁️ Cloud configuration
├── requirements.txt        # 📦 Python dependencies
├── .gitignore              # 🚫 Git ignored files
├── LICENSE                 # 📄 MIT License
└── README.md               # 📖 This file
```

---

## 🧰 Tech Stack

<div align="center">

| Layer | Technology | Usage |
|--------|-----------|-----|
| **Frontend** | Streamlit | Main chatbot interface |
| **Alt. Frontend** | HTML/CSS/JS | FastAPI interface with glassmorphism |
| **Backend** | FastAPI | Alternative REST API |
| **AI** | OpenRouter API | Access to models (Nemotron, etc.) |
| **TTS** | gTTS | Speech synthesis in multiple languages |
| **STT** | SpeechRecognition | Audio transcription |
| **Deployment** | Streamlit Cloud | Free hosting |

</div>

---

## 📝 Usage Examples

```text
💬 "Create a 30-day Python study plan"
💬 "Explain what a REST API is in simple terms"
💬 "Summarize this text in 5 lines"
💬 "Create a marketing strategy for a small business"
💬 "Explain the difference between SQL and NoSQL"
```

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. **Fork** the project
2. Create your **Feature Branch** (`git checkout -b feature/MyFeature`)
3. Commit your changes (`git commit -m 'feat: add MyFeature'`)
4. Push to the branch (`git push origin feature/MyFeature`)
5. Open a **Pull Request**

---

## 👤 Author

<div align="center">

**Leandro Timoteo Silva**

Software Engineer

[![GitHub](https://img.shields.io/badge/GitHub-@LeandroTimoteo-181717?style=flat-square&logo=github)](https://github.com/LeandroTimoteo)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Leandro_Timóteo-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/leandro-timóteo-ads)
[![Email](https://img.shields.io/badge/Email-leandrinhots6@gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:leandrinhots6@gmail.com)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-+55_83_98783--0223-25D366?style=flat-square&logo=whatsapp&logoColor=white)](https://wa.me/5583987830223)

</div>

---

## 📄 License

This project is licensed under the **MIT** License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**[Leandro Timóteo Software Engineering](https://github.com/LeandroTimoteo)**

⭐ If this project helped you, consider giving it a star on GitHub!

</div>
