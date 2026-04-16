# Pity-IA Voice Chatbot (PT/EN)

<p align="center">
  <a href="https://github.com/LeandroTimoteo/chatbot-Pity-IA" target="_blank">
    <img src="https://github.com/LeandroTimoteo/chatbot-Pity-IA/blob/main/images/Copilot_20250921_194729.png?raw=true" width="700" alt="Pity-IA Chatbot preview" />
  </a>
</p>

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-green?logo=openai)
![License](https://img.shields.io/badge/License-MIT-yellow)

Pity-IA is a bilingual (Portuguese/English) voice-enabled chatbot built with Streamlit.  
It integrates with OpenRouter models to provide real-time AI responses through a modern UI.

## Features
- Text and voice input
- AI-generated responses via OpenRouter
- Audio response playback
- PT/EN response language switching
- PT/EN full UI layout switching
- Modern responsive interface

## Installation
```bash
git clone https://github.com/LeandroTimoteo/chatbot-Pity-IA.git
cd chatbot-Pity-IA
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=nvidia/nemotron-3-nano-30b-a3b:free
```

## Run
```bash
streamlit run modules/app.py --server.port 8502
```

Open in browser:
`http://127.0.0.1:8502`

## Streamlit Cloud (Clean Deploy Checklist)
1. Commit and push the latest code to `main`.
2. In Streamlit Cloud, open your app settings and confirm:
   - Python version is compatible with your environment.
   - Secrets include `OPENROUTER_API_KEY` (and optional `OPENROUTER_MODEL`).
3. Click `Clear cache`.
4. Click `Reboot app`.
5. Hard refresh the browser (`Ctrl+F5`).
6. If console still shows `Unrecognized feature: ...`, treat it as a browser/platform warning from iframe permissions policy, not as a Python app runtime error.

## Project Structure
```text
chatbot-Pity-IA/
├── modules/
│   ├── app.py
│   ├── online.py
│   ├── speak.py
│   └── transcribe.py
├── images/
├── videos/
├── requirements.txt
└── README.md
```

## Tech Stack
- Python
- Streamlit
- OpenRouter API
- gTTS
- Streamlit `st.audio_input`

## Demo
**[Pity-IA Demo] [![Open App](https://img.shields.io/badge/🚀%20Open%20App-Streamlit-brightgreen?style=for-the-badge)](https://chatbot-pity-ia-nbnhnjscbk8htyftxdzxm5.streamlit.app/)


## Contact
**Leandro Timoteo Silva**
- Email: [leandrinhots6@gmail.com](mailto:leandrinhots6@gmail.com)
- LinkedIn: [linkedin.com/in/leandro-timóteo-ads](https://www.linkedin.com/in/leandro-timóteo-ads)
- WhatsApp: [+55 83 98783-0223](https://wa.me/5583987830223)
- GitHub: [@LeandroTimoteo](https://github.com/LeandroTimoteo)

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

