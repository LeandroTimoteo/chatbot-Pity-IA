# 🤖 Pity-IA Chatbot

Um assistente de IA inteligente bilíngue (Português e Inglês) com suporte a voz, construído com Streamlit e OpenRouter.

## ✨ Funcionalidades

- 🇧🇷 **Português** e 🇺🇸 **Inglês** - Respostas automáticas em ambos os idiomas
- 🎤 **Entrada por Voz** - Grave áudio e o app transcreve automaticamente
- 🔊 **Saída por Voz** - Ouça as respostas em áudio sintetizado
- 🎨 **Design Moderno** - Landing page atrativa com gradientes elegantes
- 💾 **Histórico de Chat** - Mantém contexto nas conversas
- ⚡ **Rápido e Responsivo** - Powered by GPT-3.5 Turbo

## 🚀 Como Usar

### Localmente

1. **Clone o repositório:**
```bash
git clone https://github.com/LeandroTimoteo/chatbot-Pity-IA.git
cd chatbot-Pity-IA
```

2. **Configure as variáveis de ambiente:**
```bash
# Crie um arquivo env/.env
OPENROUTER_API_KEY=sua_chave_api_aqui
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Execute o app:**
```bash
# Windows
.\run_app.ps1

# Linux/Mac
python -m streamlit run modules/app.py
```

5. **Acesse em seu navegador:**
```
http://localhost:8501
```

### No Streamlit Cloud

1. Vá para [https://share.streamlit.io](https://share.streamlit.io)
2. Clique em "New app"
3. Selecione seu repositório GitHub: `LeandroTimoteo/chatbot-Pity-IA`
4. Defina o caminho do app: `modules/app.py`
5. Adicione a variável de ambiente `OPENROUTER_API_KEY` nos "Secrets"
6. Deploy!

## 📋 Requisitos

- Python 3.8+
- Chave de API do OpenRouter (gratuita em https://openrouter.ai)

## 🔐 Variáveis de Ambiente

```
OPENROUTER_API_KEY=sua_chave_api_openrouter
```

## 📁 Estrutura do Projeto

```
chatbot-Pity-IA/
├── modules/
│   ├── app.py                 # App principal Streamlit
│   ├── online.py              # Sistema de IA bilíngue
│   ├── transcribe.py          # Transcrição de áudio
│   ├── speak.py               # Síntese de fala
│   └── ...outros módulos
├── env/
│   └── .env                   # Variáveis de ambiente
├── .streamlit/
│   ├── config.toml            # Configuração local
│   └── cloud.toml             # Configuração Streamlit Cloud
├── requirements.txt           # Dependências Python
├── run_app.bat               # Script Windows
├── run_app.ps1               # Script PowerShell
└── README.md                 # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

- **Streamlit** - Framework web Python
- **OpenRouter API** - Acesso a modelos de IA (GPT-3.5 Turbo)
- **Google TTS** - Síntese de fala
- **Audio Recorder Streamlit** - Gravação de áudio
- **Python-dotenv** - Gerenciamento de variáveis de ambiente

## 📝 Exemplos de Uso

1. **Digite sua pergunta** ou **grave um áudio**
2. **Escolha o idioma** (Português ou Inglês)
3. **Receba respostas** em texto e áudio
4. **Vire a página** para ver respostas em ambos os idiomas

## ⚠️ Notas Importantes

- A chave de API não deve ser commitada no GitHub
- Use a feature de "Secrets" do Streamlit Cloud para variáveis sensíveis
- O app funciona melhor com navegadores modernos que suportam Web Audio API

## 🤝 Contribuições

Sinta-se livre para fazer fork e enviar pull requests!

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

## 👤 Autor

**Leandro Timoteo**
- GitHub: [@LeandroTimoteo](https://github.com/LeandroTimoteo)
- Streamlit Cloud: [leandrotimoteo](https://share.streamlit.io/user/leandrotimoteo)

---

**Desenvolvido com ❤️ usando Streamlit**
