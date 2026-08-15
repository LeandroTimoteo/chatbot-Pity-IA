Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
cd "c:\Users\leand\OneDrive\Ambiente de Trabalho\Projetos 2025\chatbot-Pity-IA"
Write-Host "Iniciando Pity-IA Web (FastAPI)..." -ForegroundColor Green
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:8503"
.\venv\Scripts\python.exe -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8503 --reload

