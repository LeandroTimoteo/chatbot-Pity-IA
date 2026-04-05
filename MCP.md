# MCP (Master Context / Model Context Protocol) - Pity-IA

## 1. Visão Geral do Projeto
**Nome:** Pity-IA Voice Chatbot (PT/EN)
**Descrição:** Chatbot habilitado para voz com suporte bilíngue (Português e Inglês). Construído com Streamlit, integrando com a API do OpenRouter para gerar respostas de Inteligência Artificial e utilizando bibliotecas de áudio para transcrição e síntese de voz.

## 2. Requisitos de Sistema e Dependências
As seguintes bibliotecas e pacotes Python são necessários para rodar o projeto (pode ser instalado via `pip install -r requirements.txt`):
- **streamlit** (>= 1.36.0): Framework para interface de usuário web.
- **openai** (>= 1.0.0): Biblioteca para se comunicar com APIs compatíveis com os padrões OpenAI (via OpenRouter).
- **gtts** (>= 2.4.0): Google Text-to-Speech para converter as respostas de texto da IA em áudio.
- **SpeechRecognition** (>= 3.10.4): Usada para transcrever o áudio gravado do microfone para texto.
- **python-dotenv** (>= 1.0.0): Para carregar e ler variáveis de ambiente (como `OPENROUTER_API_KEY`).

## 3. Variáveis de Ambiente Necessárias
As configurações devem estar em um arquivo `.env` na raiz do projeto contendo:
```env
OPENROUTER_API_KEY=sua_chave_aqui
OPENROUTER_MODEL=nvidia/nemotron-3-nano-30b-a3b:free  # ou o modelo de sua escolha
```

## 4. Estrutura do Projeto
- `modules/app.py`: Arquivo principal da aplicação Streamlit.
- `modules/online.py`: Lógica de requisições de IA e chat online.
- `modules/speak.py`: Lógica relacionada à síntese de voz.
- `modules/transcribe.py`: Lógica responsável pela transcrição.
- `requirements.txt`: Lista oficial de dependências.
- `README.md`: Documentação geral.

## 5. Comando de Inicialização e Regras
Para o ambiente de desenvolvimento, o aplicativo deve rodar a partir do script `modules/app.py` na porta designada `8502`.
Comando oficial para servidor local:
```bash
streamlit run modules/app.py --server.port 8502
```
URL do Navegador: `http://localhost:8502`
