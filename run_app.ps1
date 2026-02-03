Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
cd "c:\Users\leand\OneDrive\Ambiente de Trabalho\Projetos 2025\chatbot-Pity-IA"
Write-Host "Iniciando ChatBot Pity-IA..." -ForegroundColor Green
Start-Sleep -Seconds 2
Start-Process "http://localhost:8501"
streamlit run modules/app.py
