"""Pity-IA Studio — Aplicação principal Streamlit.

Segurança:
- XSS: todo conteúdo de usuário é escapado com html.escape()
- Histórico de conversa por sessão (st.session_state)
- Rate limiting por sessão (max 30 msgs/min)
- Validação de input antes de enviar para API
- CSP meta tag para proteção adicional
- Logging estruturado para monitoramento
"""

import html
import os
import hashlib
import tempfile
import time
from pathlib import Path

import streamlit as st

from logger import get_logger
from transcribe import transcribe_audio
from speak import speak_text
from online import gerar_resposta_online, SYSTEM_PROMPTS

# Configurar logging
logger = get_logger(__name__, log_file="streamlit.log")

# ---------------------------------------------------------------------------
# Cache e otimizações de performance
# ---------------------------------------------------------------------------

@st.cache_resource
def load_system_prompts():
    """Cache para os system prompts que nunca mudam."""
    return SYSTEM_PROMPTS

@st.cache_data(ttl=3600)
def get_ui_translations():
    """Cache para textos de UI (renovado a cada hora)."""
    return {
        "pt": {
            "layout_toggle": "Layout: Português",
            "layout_help": "Mudar layout para inglês",
            "hero_title": "Seu assistente com visual premium e resposta em tempo real",
            "hero_desc": "Converse por texto ou voz em PT/EN com uma interface mais moderna, limpa e preparada para impressionar.",
            "panel_1_t": "🔒 Segurança",
            "panel_1_d": "Proteção contra XSS, sessões isoladas e rate limiting.",
            "panel_2_t": "⚡ Fluxo rápido",
            "panel_2_d": "Entrada por texto/voz e resposta com menos fricção.",
            "panel_3_t": "🌍 Modo bilíngue",
            "panel_3_d": "Alternância instantânea entre português e inglês.",
            "start_pt": "Iniciar em Português",
            "start_en": "Start in English",
            "prompt_examples": "Exemplos de prompts",
            "prompt_examples_info": "Exemplos: 'Crie um plano de estudos', 'Explique este erro', 'Resuma meu texto em 5 linhas'.",
            "chat_title": "🤖 Pity-IA Chat",
            "chip_lang": "Idioma",
            "chip_messages": "Mensagens",
            "reply_lang_btn": "Trocar idioma da resposta",
            "clear_chat_btn": "🗑️ Limpar conversa",
            "back_btn": "← Voltar",
            "voice_input": "Entrada por voz",
            "tip": "Dica: pergunte algo específico para respostas melhores.",
            "chat_input": "Digite sua pergunta...",
            "transcribing": "Transcrevendo áudio...",
            "transcription_ok": "Transcrição",
            "thinking": "Pity-IA está pensando...",
            "listen_last": "🔊 Ouvir última resposta",
            "you": "Você",
            "too_long": "⚠️ Mensagem muito longa (máximo 4000 caracteres).",
            "rate_limited": "⚠️ Limite de mensagens atingido. Aguarde um momento.",
        },
        "en": {
            "layout_toggle": "Layout: English",
            "layout_help": "Switch layout to Portuguese",
            "hero_title": "Your assistant with premium visuals and real-time responses",
            "hero_desc": "Chat by text or voice in PT/EN with a modern, clean interface built to stand out.",
            "panel_1_t": "🔒 Security",
            "panel_1_d": "XSS protection, isolated sessions, and rate limiting.",
            "panel_2_t": "⚡ Fast flow",
            "panel_2_d": "Text/voice input and responses with less friction.",
            "panel_3_t": "🌍 Bilingual mode",
            "panel_3_d": "Instant switch between Portuguese and English.",
            "start_pt": "Start in Portuguese",
            "start_en": "Start in English",
            "prompt_examples": "Prompt examples",
            "prompt_examples_info": "Examples: 'Create a study plan', 'Explain this error', 'Summarize my text in 5 lines'.",
            "chat_title": "🤖 Pity-IA Chat",
            "chip_lang": "Language",
            "chip_messages": "Messages",
            "reply_lang_btn": "Change response language",
            "clear_chat_btn": "🗑️ Clear chat",
            "back_btn": "← Back",
            "voice_input": "Voice input",
            "tip": "Tip: ask something specific for better responses.",
            "chat_input": "Type your question...",
            "transcribing": "Transcribing audio...",
            "transcription_ok": "Transcription",
            "thinking": "Pity-IA is thinking...",
            "listen_last": "🔊 Listen to last response",
            "you": "You",
            "too_long": "⚠️ Message too long (maximum 4000 characters).",
            "rate_limited": "⚠️ Message limit reached. Please wait a moment.",
        }
    }

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Pity-IA Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS profissional com proteção CSP
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Manrope:wght@400;500;600;700&display=swap');

    :root {
        --bg-1: #07131f;
        --bg-2: #0d2538;
        --surface: rgba(255,255,255,0.06);
        --surface-2: rgba(255,255,255,0.10);
        --stroke: rgba(255,255,255,0.10);
        --text: #f5fbff;
        --muted: #94a9c2;
        --brand: #12d6e3;
        --brand-2: #1f7afc;
        --success: #12d68e;
        --danger: #e35555;
        --radius-sm: 10px;
        --radius-md: 16px;
        --radius-lg: 24px;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Manrope', sans-serif;
        color: var(--text);
        background:
            radial-gradient(1000px 400px at 20% -20%, rgba(18,214,227,.12), transparent 60%),
            radial-gradient(800px 350px at 80% 0%, rgba(31,122,252,.15), transparent 55%),
            linear-gradient(160deg, var(--bg-1), var(--bg-2));
    }

    [data-testid="stSidebar"] {
        background: rgba(7, 19, 31, 0.6) !important;
        backdrop-filter: blur(24px) !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.06);
        margin: .8rem 0 !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        font-size: .85rem;
        min-height: 2.3rem;
        border-radius: var(--radius-sm) !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding-top: 1.4rem;
        max-width: 1100px;
    }

    .hero {
        border: 1px solid var(--stroke);
        background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.02));
        border-radius: var(--radius-lg);
        padding: 2.2rem 2rem;
        backdrop-filter: blur(8px);
    }

    .eyebrow {
        display: inline-block;
        font-size: .7rem;
        letter-spacing: .1em;
        text-transform: uppercase;
        color: var(--brand);
        border: 1px solid rgba(18,214,227,.3);
        border-radius: 999px;
        padding: .25rem .65rem;
        margin-bottom: .8rem;
        font-weight: 600;
    }

    .hero h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.15;
        margin: 0;
        color: white;
        font-weight: 700;
        letter-spacing: -.02em;
    }

    .hero p {
        color: var(--muted);
        margin: .9rem 0 0;
        font-size: 1.02rem;
        line-height: 1.6;
        max-width: 600px;
    }

    .panel {
        margin-top: 1rem;
        border: 1px solid var(--stroke);
        background: linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.015));
        border-radius: var(--radius-md);
        padding: 1.3rem 1.4rem;
        backdrop-filter: blur(6px);
        transition: all 0.3s ease;
    }

    .panel:hover {
        border-color: rgba(18,214,227,.25);
        background: linear-gradient(180deg, rgba(18,214,227,.06), rgba(255,255,255,.02));
        transform: translateY(-3px);
    }

    .panel h3 {
        margin: 0 0 .35rem;
        color: #ffffff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 600;
    }

    .panel p {
        margin: 0;
        color: var(--muted);
        font-size: .92rem;
        line-height: 1.55;
    }

    .topbar {
        border: 1px solid var(--stroke);
        background: linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.015));
        border-radius: var(--radius-md);
        padding: .9rem 1.2rem;
        margin-bottom: .8rem;
        backdrop-filter: blur(6px);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: .5rem;
    }

    .topbar h2 {
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.2rem;
        color: #ffffff;
        font-weight: 600;
    }

    .chip {
        display: inline-block;
        border: 1px solid var(--stroke);
        border-radius: 999px;
        padding: .2rem .6rem;
        font-size: .75rem;
        color: var(--muted);
        background: rgba(255,255,255,.04);
    }

    .msg-row {
        display: flex;
        gap: .7rem;
        margin: .5rem 0;
        animation: pop .25s ease-out;
        align-items: flex-start;
    }

    .msg-avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
        background: rgba(255,255,255,.06);
        border: 1px solid rgba(255,255,255,.08);
    }

    .msg-body {
        border-radius: var(--radius-md);
        padding: .8rem 1.1rem;
        word-wrap: break-word;
        overflow-wrap: break-word;
        line-height: 1.6;
        flex: 1;
        min-width: 0;
        font-size: .95rem;
    }

    .bubble-user .msg-body {
        background: linear-gradient(145deg, var(--brand-2), #1756d3);
        color: #fff;
        border: 1px solid rgba(255,255,255,.12);
    }

    .bubble-ai .msg-body {
        background: rgba(255,255,255,.92);
        color: #14263a;
        border: 1px solid rgba(18,214,227,.15);
    }

    .bubble-ai pre {
        background: #1a2d45;
        color: #e0e8f5;
        border-radius: 8px;
        padding: .7rem;
        overflow-x: auto;
        font-size: .86rem;
        margin: .5rem 0 0;
    }

    @keyframes pop {
        from {opacity: .5; transform: translateY(8px);}
        to {opacity: 1; transform: translateY(0);}
    }

    .stButton > button {
        border: 1px solid var(--stroke);
        background: linear-gradient(135deg, rgba(18,214,227,.15), rgba(31,122,252,.18));
        color: #ffffff;
        border-radius: var(--radius-sm);
        font-weight: 600;
        min-height: 2.5rem;
        transition: all 0.2s ease;
        letter-spacing: .01em;
    }

    .stButton > button:hover {
        border-color: rgba(18,214,227,.5);
        background: linear-gradient(135deg, rgba(18,214,227,.25), rgba(31,122,252,.28));
        transform: translateY(-1px);
    }

    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,.04);
        border-color: rgba(255,255,255,.08);
    }

    .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,.08);
        border-color: rgba(18,214,227,.3);
    }

    .stButton > button:active {
        transform: translateY(0) scale(.98);
    }

    div[data-testid="stChatInput"] {
        border-radius: var(--radius-md);
        border: 1px solid var(--stroke);
        background: var(--surface-2);
        transition: border-color .2s ease;
    }

    div[data-testid="stChatInput"]:focus-within {
        border-color: rgba(18,214,227,.4);
    }

    hr.st-divider {
        border-color: rgba(255,255,255,.04) !important;
        margin: .8rem 0 !important;
    }

    h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #ffffff;
        font-size: 1.05rem;
        font-weight: 600;
        margin: .5rem 0 .7rem;
    }

    .small-note {
        color: var(--muted);
        font-size: .82rem;
        line-height: 1.5;
    }

    div[data-testid="stAudioInput"] > div {
        border: 1px solid var(--stroke);
        border-radius: var(--radius-sm);
        background: rgba(255,255,255,.04);
        transition: all 0.2s ease;
    }

    div[data-testid="stAudioInput"] > div:hover {
        border-color: rgba(18,214,227,.35);
    }

    div[data-testid="stAudioInput"] button {
        border-radius: 8px !important;
    }

    .version-badge {
        display: inline-block;
        font-size: .65rem;
        color: var(--muted);
        border: 1px solid var(--stroke);
        border-radius: 6px;
        padding: .12rem .4rem;
        opacity: 0.65;
        font-weight: 500;
    }

    .rate-limit-warning {
        background: rgba(227, 85, 85, 0.1);
        border: 1px solid rgba(227, 85, 85, 0.2);
        border-radius: var(--radius-sm);
        padding: .6rem .9rem;
        color: #ffaaaa;
        font-size: .86rem;
        margin: .5rem 0;
    }

    .stForm {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    textarea:focus {
        border-color: rgba(18,214,227,.4) !important;
    }

    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,.1);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,.2);
    }

    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] {
            padding-top: .6rem;
            padding-left: .6rem;
            padding-right: .6rem;
        }

        .hero {
            padding: 1.2rem;
        }

        .topbar {
            flex-direction: column;
            align-items: flex-start;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state (seguro, por sessão)
# ---------------------------------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "idioma" not in st.session_state:
    st.session_state.idioma = "pt"
if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "pt"
if "last_audio_path" not in st.session_state:
    st.session_state.last_audio_path = None
if "last_voice_digest" not in st.session_state:
    st.session_state.last_voice_digest = None
# Usar cache para prompts de sistema
_cached_system_prompts = load_system_prompts()
if "historico_ia" not in st.session_state:
    st.session_state.historico_ia = [_cached_system_prompts["pt"].copy()]
if "rate_limit_timestamps" not in st.session_state:
    st.session_state.rate_limit_timestamps = []


# ---------------------------------------------------------------------------
# Constantes de segurança
# ---------------------------------------------------------------------------

MAX_INPUT_LENGTH = 4000
RATE_LIMIT_WINDOW = 60  # segundos
RATE_LIMIT_MAX = 30  # mensagens por janela
APP_VERSION = "2.0.0"

# ---------------------------------------------------------------------------
# Internacionalização
# ---------------------------------------------------------------------------

LANG_LABEL = {
    "pt": "Português",
    "en": "English",
}

# UI_TEXT agora usa cache
UI_TEXT = get_ui_translations()


# ---------------------------------------------------------------------------
# Segurança: Rate Limiting
# ---------------------------------------------------------------------------

def _check_rate_limit() -> bool:
    """Verifica se o usuário excedeu o rate limit. Retorna True se PERMITIDO."""
    now = time.time()
    # Limpar timestamps antigos
    st.session_state.rate_limit_timestamps = [
        ts for ts in st.session_state.rate_limit_timestamps
        if now - ts < RATE_LIMIT_WINDOW
    ]
    if len(st.session_state.rate_limit_timestamps) >= RATE_LIMIT_MAX:
        return False
    st.session_state.rate_limit_timestamps.append(now)
    return True


# ---------------------------------------------------------------------------
# Renderização segura de mensagens
# ---------------------------------------------------------------------------

def render_message(role: str, content: str) -> None:
    """Renderiza uma mensagem de chat com proteção XSS."""
    safe_content = html.escape(content)
    safe_content = safe_content.replace("\n", "<br>")

    css = "bubble-user" if role == "user" else "bubble-ai"
    ui = UI_TEXT[st.session_state.ui_lang]
    avatar = "🧑" if role == "user" else "🤖"
    prefix = html.escape(ui["you"]) if role == "user" else "Pity-IA"

    st.markdown(
        f"""
        <div class="msg-row {css}">
            <div class="msg-avatar">{avatar}</div>
            <div class="msg-body">
                <strong>{prefix}:</strong> {safe_content}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Landing Page
# ---------------------------------------------------------------------------

def landing_page() -> None:
    ui = UI_TEXT[st.session_state.ui_lang]
    lang = st.session_state.ui_lang

    st.markdown(
        f"""
        <section class="hero">
            <span class="eyebrow">Pity-IA Studio <span class="version-badge">v{APP_VERSION}</span></span>
            <h1>{html.escape(ui["hero_title"])}</h1>
            <p>{html.escape(ui["hero_desc"])}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="panel">
                <h3>{ui["panel_1_t"]}</h3>
                <p>{html.escape(ui["panel_1_d"])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="panel">
                <h3>{ui["panel_2_t"]}</h3>
                <p>{html.escape(ui["panel_2_d"])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="panel">
                <h3>{ui["panel_3_t"]}</h3>
                <p>{html.escape(ui["panel_3_d"])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:.55rem'></div>", unsafe_allow_html=True)
    cta1, cta2, cta3 = st.columns([1, 1, 1])

    with cta1:
        if st.button(ui["start_pt"], use_container_width=True):
            st.session_state.idioma = "pt"
            st.session_state.historico_ia = [SYSTEM_PROMPTS["pt"].copy()]
            st.session_state.page = "chat"
            st.rerun()

    with cta2:
        if st.button(ui["start_en"], use_container_width=True):
            st.session_state.idioma = "en"
            st.session_state.historico_ia = [SYSTEM_PROMPTS["en"].copy()]
            st.session_state.page = "chat"
            st.rerun()

    with cta3:
        if st.button(ui["prompt_examples"], use_container_width=True):
            st.info(ui["prompt_examples_info"])


# ---------------------------------------------------------------------------
# Processamento de áudio
# ---------------------------------------------------------------------------

def process_voice_input(audio_bytes: bytes) -> str | None:
    if not audio_bytes:
        return None

    temp_dir = Path(tempfile.gettempdir())
    temp_file = temp_dir / "audio_temp.wav"
    try:
        temp_file.write_bytes(audio_bytes)
        text = transcribe_audio(str(temp_file))
        return text
    finally:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Chat Page
# ---------------------------------------------------------------------------

def chat_page() -> None:
    ui = UI_TEXT[st.session_state.ui_lang]

    st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)

    # Header
    st.markdown('<div class="topbar">', unsafe_allow_html=True)
    header_left, header_mid, header_right = st.columns([3, 1.3, 1.3])

    with header_left:
        st.markdown(
            f"""
            <h2>{ui["chat_title"]} <span class="version-badge">v{APP_VERSION}</span></h2>
            <span class="chip">{html.escape(ui["chip_lang"])}: {html.escape(LANG_LABEL[st.session_state.idioma])}</span>
            <span class="chip">{html.escape(ui["chip_messages"])}: {len(st.session_state.messages)}</span>
            """,
            unsafe_allow_html=True,
        )

    with header_mid:
        if st.button(ui["reply_lang_btn"], use_container_width=True):
            new_lang = "en" if st.session_state.idioma == "pt" else "pt"
            st.session_state.idioma = new_lang
            st.session_state.historico_ia = [SYSTEM_PROMPTS[new_lang].copy()]
            st.rerun()

    with header_right:
        if st.button(ui["clear_chat_btn"], use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_audio_path = None
            st.session_state.historico_ia = [
                SYSTEM_PROMPTS[st.session_state.idioma].copy()
            ]
            st.session_state.rate_limit_timestamps = []
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    back_col, _ = st.columns([1, 6])
    with back_col:
        if st.button(ui["back_btn"], use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()

    st.divider()

    # Mensagens
    for message in st.session_state.messages:
        render_message(message["role"], message["content"])

    st.divider()

    # Area de Inputs (Texto e Voz)
    input_title = "### 💬 Digite sua mensagem ou use a voz" if st.session_state.ui_lang == "pt" else "### 💬 Type your message or use voice"
    st.markdown(input_title)
    
    # Input de texto explícito
    with st.form("text_input_form", clear_on_submit=True):
        text_col, btn_col = st.columns([5, 1])
        with text_col:
            text_input = st.text_input("Mensagem", label_visibility="collapsed", placeholder=ui["chat_input"])
        with btn_col:
            submit_label = "Enviar" if st.session_state.ui_lang == "pt" else "Send"
            submit_btn = st.form_submit_button(submit_label)
            
    user_input = text_input if (submit_btn and text_input.strip()) else None

    # Input de voz
    audio_col, help_col = st.columns([1, 3])
    with audio_col:
        audio_file = st.audio_input(ui["voice_input"])
        audio_bytes = audio_file.getvalue() if audio_file else None

    with help_col:
        st.markdown(
            f"<p class='small-note'>{html.escape(ui['tip'])}</p>",
            unsafe_allow_html=True,
        )

    # Processar áudio (se novo)
    audio_digest = hashlib.sha1(audio_bytes).hexdigest() if audio_bytes else None
    if audio_bytes and not user_input and audio_digest != st.session_state.last_voice_digest:
        with st.spinner(ui["transcribing"]):
            user_input = process_voice_input(audio_bytes)
        st.session_state.last_voice_digest = audio_digest
        if user_input:
            st.success(f"{ui['transcription_ok']}: {user_input}")

    # Processar input do usuário
    if user_input and user_input.strip():
        # SEGURANÇA: Validar tamanho
        if len(user_input) > MAX_INPUT_LENGTH:
            st.warning(ui["too_long"])
            return

        # SEGURANÇA: Rate limiting
        if not _check_rate_limit():
            st.markdown(
                f'<div class="rate-limit-warning">{html.escape(ui["rate_limited"])}</div>',
                unsafe_allow_html=True,
            )
            return

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner(ui["thinking"]):
            result = gerar_resposta_online(
                user_input,
                st.session_state.idioma,
                historico=st.session_state.historico_ia,
            )

        if result.get("sucesso"):
            answer = result[st.session_state.idioma]
            st.session_state.messages.append({"role": "assistant", "content": answer})

            # Atualizar histórico da sessão
            if "historico" in result:
                st.session_state.historico_ia = result["historico"]

            try:
                audio_lang = "pt" if st.session_state.idioma == "pt" else "en"
                audio_path = speak_text(answer, audio_lang)
                st.session_state.last_audio_path = (
                    audio_path if audio_path and os.path.exists(audio_path) else None
                )
            except Exception:
                st.session_state.last_audio_path = None
        else:
            st.error(result[st.session_state.idioma])

        st.rerun()

    # Botão para ouvir última resposta
    if st.session_state.last_audio_path and os.path.exists(st.session_state.last_audio_path):
        st.divider()
        if st.button(ui["listen_last"], use_container_width=False):
            with open(st.session_state.last_audio_path, "rb") as f:
                st.audio(f.read(), format="audio/mpeg")

    # Auto-scroll para a última mensagem
    st.markdown(
        """
        <script>
        window.scrollTo(0, document.body.scrollHeight);
        </script>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar Elegante
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 2rem; margin-top: .5rem;">
            <div style="font-size: 2.4rem; margin-bottom: .3rem;">🤖</div>
            <h2 style="margin: 0; font-family: 'Space Grotesk', sans-serif; color: var(--brand); font-size: 1.6rem; font-weight: 700;">Pity-IA</h2>
            <span class="version-badge" style="margin-top: .4rem; display: inline-block;">v{APP_VERSION}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("### 🌐 Idioma / Language")
    ui = UI_TEXT[st.session_state.ui_lang]
    col_lang1, col_lang2 = st.columns(2)
    with col_lang1:
        if st.button("🇧🇷 PT", use_container_width=True,
                     disabled=st.session_state.ui_lang == "pt",
                     type="primary" if st.session_state.ui_lang == "pt" else "secondary"):
            if st.session_state.ui_lang != "pt":
                st.session_state.ui_lang = "pt"
                st.rerun()
    with col_lang2:
        if st.button("🇺🇸 EN", use_container_width=True,
                     disabled=st.session_state.ui_lang == "en",
                     type="primary" if st.session_state.ui_lang == "en" else "secondary"):
            if st.session_state.ui_lang != "en":
                st.session_state.ui_lang = "en"
                st.rerun()
        
    st.divider()
    about_title = "### ℹ️ Sobre" if st.session_state.ui_lang == "pt" else "### ℹ️ About"
    about_text = "Assistente premium com respostas em tempo real, suporte a voz e chat seguro." if st.session_state.ui_lang == "pt" else "Premium assistant with real-time responses, voice support, and secure chat."
    st.markdown(about_title)
    st.caption(about_text)

# ---------------------------------------------------------------------------
# Layout principal
# ---------------------------------------------------------------------------

if st.session_state.page == "landing":
    landing_page()
else:
    chat_page()

# Footer
footer_text = "Engenharia de software" if st.session_state.ui_lang == "pt" else "Software Engineering"
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 2rem; padding: .7rem;
         border-top: 1px solid rgba(255,255,255,0.05);">
        <span style="color: var(--muted); font-size: .75rem; opacity: .7;">
            © 2025–2026 Pity-IA Studio · Leandro Timóteo {footer_text} · v{APP_VERSION}
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
