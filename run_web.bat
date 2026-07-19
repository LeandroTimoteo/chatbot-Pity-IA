@echo off
cd /d "c:\Users\leand\OneDrive\Ambiente de Trabalho\Projetos 2025\chatbot-Pity-IA"
echo Iniciando Pity-IA Web (FastAPI)...
timeout /t 2 /nobreak
start http://127.0.0.1:8503
.\venv\Scripts\python.exe -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8503 --reload

