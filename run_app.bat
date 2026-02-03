@echo off
cd /d "c:\Users\leand\OneDrive\Ambiente de Trabalho\Projetos 2025\chatbot-Pity-IA"
echo Iniciando ChatBot Pity-IA...
timeout /t 2 /nobreak
start http://localhost:8501
streamlit run modules/app.py
