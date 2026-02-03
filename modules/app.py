import streamlit as st
import io
import wave
import os
from dotenv import load_dotenv
import time

# 🔐 Carrega variáveis do .env
load_dotenv()

# 🎙️ Módulos locais
from audio_recorder_streamlit import audio_recorder
from transcribe import transcribe_audio
from speak import speak_text
from online import gerar_resposta_online

# 🔧 Configuração da página
st.set_page_config(
    page_title="🤖 ChatBot Pity-IA | IA Inteligente",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🚫 Suprimir warnings do console (Mais agressivo)
st.markdown("""
    <script>
    // Suprimir todos os warnings que não são críticos
    (function() {
        // Desabilitar logging de Permissions-Policy
        document.addEventListener('securitypolicyviolation', function(e) {
            e.preventDefault();
        }, true);
        
        // Interceptar todos os tipos de log
        const originalWarn = console.warn;
        const originalError = console.error;
        const originalLog = console.log;
        const originalInfo = console.info;
        const originalDebug = console.debug;
        
        const patternsToSuppress = [
            'Unrecognized feature',
            'sandbox',
            'Permissions-Policy',
            'allow-scripts',
            'allow-same-origin',
            'escape its sandboxing',
            'ScriptProcessorNode',
            'Deprecation',
            'AudioRecorder',
            'Sample rate',
            'iframe',
            'media',
            'Failed to load',
            'wav',
            '404'
        ];
        
        function shouldSuppress(message) {
            if (typeof message !== 'string') {
                message = String(message);
            }
            return patternsToSuppress.some(pattern => 
                message.toLowerCase().includes(pattern.toLowerCase())
            );
        }
        
        console.warn = function(...args) {
            if (!args.some(arg => shouldSuppress(arg))) {
                originalWarn.apply(console, args);
            }
        };
        
        console.error = function(...args) {
            if (!args.some(arg => shouldSuppress(arg))) {
                originalError.apply(console, args);
            }
        };
        
        console.log = function(...args) {
            if (!args.some(arg => shouldSuppress(arg))) {
                originalLog.apply(console, args);
            }
        };
        
        console.info = function(...args) {
            if (!args.some(arg => shouldSuppress(arg))) {
                originalInfo.apply(console, args);
            }
        };
        
        console.debug = function(...args) {
            if (!args.some(arg => shouldSuppress(arg))) {
                originalDebug.apply(console, args);
            }
        };
        
        // Suprimir erros de recurso não encontrado
        window.addEventListener('error', function(e) {
            if (shouldSuppress(e.message) || shouldSuppress(e.filename || '')) {
                e.preventDefault();
            }
        }, true);
    })();
    </script>
""", unsafe_allow_html=True)

# 🎨 Estilo visual avançado
st.markdown("""
    <style>
    * {
        margin: 0;
        padding: 0;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    [data-testid="stMainBlockContainer"] {
        padding: 2rem;
    }
    
    .main-header {
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        animation: fadeInDown 0.8s ease-out;
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.95;
        margin-bottom: 1rem;
    }
    
    .feature-box {
        background: rgba(255,255,255,0.95);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    .chat-message {
        border-radius: 15px;
        padding: 1.2rem;
        margin: 1rem 0;
        animation: slideIn 0.4s ease-out;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 5px;
    }
    
    .assistant-message {
        background: rgba(255,255,255,0.95);
        color: #333;
        margin-right: 20%;
        border-bottom-left-radius: 5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .button-group {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .language-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        margin: 0.5rem;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .stButton > button {
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
    }
    
    .landing-section {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        color: white;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .landing-section h2 {
        font-size: 2rem;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .landing-section p {
        font-size: 1.1rem;
        line-height: 1.8;
        margin-bottom: 1rem;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: rgba(255,255,255,0.15);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-10px);
    }
    
    .feature-card h3 {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white !important;
        padding: 1rem 2rem !important;
        border-radius: 30px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        display: inline-block;
        margin: 1rem 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .cta-button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 10px 30px rgba(245, 87, 108, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 📱 Inicializa session state
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "idioma" not in st.session_state:
    st.session_state.idioma = "pt"

# 🏠 LANDING PAGE
if st.session_state.page == "landing":
    # Header principal
    st.markdown("""
        <div class="main-header">
            <h1>🤖 Pity-IA</h1>
            <p>Seu Assistente de IA Inteligente e Bilíngue</p>
            <div style="margin: 1.5rem 0;">
                <span class="language-badge">🇧🇷 Português</span>
                <span class="language-badge">🇺🇸 Inglês</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Seção de benefícios
    st.markdown("""
        <div class="landing-section">
            <h2>🌟 Por que escolher Pity-IA?</h2>
            <p>Conheça as vantagens de um assistente de IA de última geração</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Grid de features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h3>🎯 Preciso</h3>
                <p>Respostas precisas e relevantes adaptadas às suas necessidades</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h3>🌍 Bilíngue</h3>
                <p>Suporte completo em Português e Inglês</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card">
                <h3>⚡ Rápido</h3>
                <p>Respostas instantâneas com tecnologia de IA avançada</p>
            </div>
        """, unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
            <div class="feature-card">
                <h3>🎤 Voz</h3>
                <p>Suporte a entrada e saída de áudio natural</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
            <div class="feature-card">
                <h3>💾 Histórico</h3>
                <p>Mantém contexto nas suas conversas</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
            <div class="feature-card">
                <h3>🚀 Pronto</h3>
                <p>Comece a usar agora sem complicações</p>
            </div>
        """, unsafe_allow_html=True)
    
    # CTA buttons
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn1:
        if st.button("🚀 Começar em Português", use_container_width=True, key="btn_pt"):
            st.session_state.idioma = "pt"
            st.session_state.page = "chat"
            st.rerun()
    
    with col_btn2:
        if st.button("🚀 Start in English", use_container_width=True, key="btn_en"):
            st.session_state.idioma = "en"
            st.session_state.page = "chat"
            st.rerun()
    
    with col_btn3:
        if st.button("❓ Ver Mais", use_container_width=True, key="btn_more"):
            st.info("📌 Este é um assistente de IA bilíngue alimentado por tecnologia de ponta. Use para fazer perguntas, obter respostas informadas e conversar naturalmente!")

# 💬 PÁGINA DO CHAT
elif st.session_state.page == "chat":
    # Header
    col_header1, col_header2, col_header3 = st.columns([3, 1, 1])
    
    with col_header1:
        st.markdown(f"### 🤖 ChatBot Pity-IA | Idioma: {'🇧🇷 Português' if st.session_state.idioma == 'pt' else '🇺🇸 English'}")
    
    with col_header2:
        if st.button("🔄 Trocar Idioma"):
            st.session_state.idioma = "en" if st.session_state.idioma == "pt" else "pt"
            st.rerun()
    
    with col_header3:
        if st.button("🧹 Limpar"):
            st.session_state.messages = []
            st.rerun()
    
    # Botão voltar
    if st.button("⬅️ Voltar"):
        st.session_state.page = "landing"
        st.rerun()
    
    st.divider()
    
    # Display messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>👤 Você:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message"><strong>🤖 Pity-IA:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Input
    col_audio, col_text = st.columns([1, 3])
    
    with col_audio:
        st.write("🎤 Áudio:")
        audio_bytes = audio_recorder()
    
    user_input = st.chat_input("Digite sua pergunta ou fale através do microfone...", key="chat_input")
    
    # Processar áudio
    if audio_bytes and not user_input:
        try:
            with st.spinner("🎧 Processando áudio..."):
                with open("audio_temp.wav", "wb") as f:
                    f.write(audio_bytes)
                user_input = transcribe_audio("audio_temp.wav")
                if user_input:
                    st.success(f"📝 Transcrição: {user_input}")
                    # Limpar arquivo após uso
                    try:
                        os.remove("audio_temp.wav")
                    except:
                        pass
        except Exception as e:
            st.error(f"❌ Erro na transcrição: {e}")
    
    # Processar chat
    if user_input and user_input.strip():
        # Adicionar mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Gerar resposta
        with st.spinner("🤖 Pity-IA está pensando..."):
            resultado = gerar_resposta_online(user_input, st.session_state.idioma)
            
            if resultado["sucesso"]:
                resposta = resultado[st.session_state.idioma]
                st.session_state.messages.append({"role": "assistant", "content": resposta})
                
                # Tentar gerar áudio (sem autoplay para evitar erro 404)
                try:
                    lang_audio = "pt" if st.session_state.idioma == "pt" else "en"
                    audio_path = speak_text(resposta, lang_audio)
                    if audio_path and os.path.exists(audio_path):
                        # Armazenar o path do áudio na session para usar depois
                        st.session_state.last_audio_path = audio_path
                except Exception as audio_error:
                    # Se falhar, apenas continua sem áudio
                    st.session_state.last_audio_path = None
            else:
                st.error(resultado[st.session_state.idioma])
        
        st.rerun()
    
    # Reproduzir áudio se existir
    if hasattr(st.session_state, 'last_audio_path') and st.session_state.last_audio_path:
        if os.path.exists(st.session_state.last_audio_path):
            st.divider()
            col_audio1, col_audio2 = st.columns([1, 3])
            with col_audio1:
                if st.button("🔊 Ouvir Resposta"):
                    try:
                        with open(st.session_state.last_audio_path, "rb") as audio_file:
                            st.audio(audio_file.read(), format="audio/wav")
                    except:
                        pass




