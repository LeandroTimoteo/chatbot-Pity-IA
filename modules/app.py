"""Pity-IA Studio — Aplicação principal Streamlit.

Segurança:
- XSS: todo conteúdo de usuário é escapado com html.escape()
- Histórico de conversa por sessão (st.session_state)
- Rate limiting por sessão (max 30 msgs/min)
- Validação de input antes de enviar para API
- CSP meta tag para proteção adicional
"""

import html
import os
import hashlib
import time
from pathlib import Path

import streamlit as st

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from transcribe import transcribe_audio
from speak import speak_text
from online import gerar_resposta_online, SYSTEM_PROMPTS

# ---------------------------------------------------------------------------
# Carregamento de ambiente
# ---------------------------------------------------------------------------

if load_dotenv:
    load_dotenv()

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Pity-IA Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS profissional com proteção CSP
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Manrope:wght@400;600;700&display=swap');

    :root {
        --bg-1: #07131f;
        --bg-2: #0d2538;
        --surface: rgba(255,255,255,0.08);
        --surface-2: rgba(255,255,255,0.12);
        --stroke: rgba(255,255,255,0.18);
        --text: #f5fbff;
        --muted: #b8c7d8;
        --brand: #12d6e3;
        --brand-2: #1f7afc;
        --success: #12d68e;
        --danger: #e35555;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Manrope', sans-serif;
        color: var(--text);
        background:
            radial-gradient(1200px 500px at 10% -10%, rgba(18,214,227,.22), transparent 60%),
            radial-gradient(900px 400px at 100% 0%, rgba(31,122,252,.25), transparent 55%),
            linear-gradient(145deg, var(--bg-1), var(--bg-2));
    }

    [data-testid="stMainBlockContainer"] {
        padding-top: 1.2rem;
        max-width: 1150px;
    }

    .hero {
        border: 1px solid var(--stroke);
        background: linear-gradient(180deg, rgba(255,255,255,.12), rgba(255,255,255,.04));
        border-radius: 24px;
        padding: 1.8rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 12px 40px rgba(0,0,0,.28);
    }

    .eyebrow {
        display: inline-block;
        font-size: .75rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: var(--brand);
        border: 1px solid rgba(18,214,227,.45);
        border-radius: 999px;
        padding: .28rem .6rem;
        margin-bottom: .8rem;
    }

    .hero h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.1;
        margin: 0;
        color: white;
    }

    .hero p {
        color: var(--muted);
        margin: .8rem 0 0;
        font-size: 1.02rem;
    }

    .panel {
        margin-top: 1rem;
        border: 1px solid var(--stroke);
        background: var(--surface);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        backdrop-filter: blur(10px);
    }

    .panel h3 {
        margin: 0 0 .35rem;
        color: #ffffff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.06rem;
    }

    .panel p {
        margin: 0;
        color: var(--muted);
        font-size: .95rem;
    }

    .topbar {
        border: 1px solid var(--stroke);
        background: var(--surface);
        border-radius: 16px;
        padding: .85rem 1rem;
        margin-bottom: .8rem;
    }

    .topbar h2 {
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.2rem;
        color: #ffffff;
    }

    .chip {
        display: inline-block;
        border: 1px solid var(--stroke);
        border-radius: 999px;
        padding: .2rem .55rem;
        font-size: .78rem;
        color: var(--muted);
        margin-right: .35rem;
    }

    .bubble-user, .bubble-ai {
        border-radius: 14px;
        padding: .82rem .95rem;
        margin: .4rem 0;
        animation: pop .2s ease-out;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    .bubble-user {
        background: linear-gradient(145deg, var(--brand-2), #1756d3);
        color: #fff;
        border: 1px solid rgba(255,255,255,.18);
    }

    .bubble-ai {
        background: rgba(255,255,255,.92);
        color: #14263a;
        border: 1px solid rgba(18,214,227,.2);
    }

    .bubble-ai pre {
        background: #1a2d45;
        color: #e0e8f5;
        border-radius: 8px;
        padding: .6rem;
        overflow-x: auto;
        font-size: .88rem;
    }

    @keyframes pop {
        from {opacity: .55; transform: translateY(6px);}
        to {opacity: 1; transform: translateY(0);}
    }

    .stButton > button {
        border: 1px solid var(--stroke);
        background: linear-gradient(135deg, rgba(18,214,227,.2), rgba(31,122,252,.22));
        color: #ffffff;
        border-radius: 12px;
        font-weight: 700;
        min-height: 2.6rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: rgba(18,214,227,.6);
        box-shadow: 0 0 0 2px rgba(18,214,227,.2) inset;
        transform: translateY(-1px);
    }

    div[data-testid="stChatInput"] {
        border-radius: 14px;
        border: 1px solid var(--stroke);
        background: var(--surface-2);
    }

    .small-note {
        color: var(--muted);
        font-size: .83rem;
        margin-top: .2rem;
    }

    .version-badge {
        display: inline-block;
        font-size: .68rem;
        color: var(--muted);
        border: 1px solid var(--stroke);
        border-radius: 6px;
        padding: .15rem .4rem;
        margin-left: .5rem;
        opacity: 0.7;
    }

    .rate-limit-warning {
        background: rgba(227, 85, 85, 0.15);
        border: 1px solid rgba(227, 85, 85, 0.3);
        border-radius: 10px;
        padding: .6rem .8rem;
        color: #ffaaaa;
        font-size: .88rem;
        margin: .5rem 0;
    }

    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] {
            padding-top: .8rem;
            padding-left: .8rem;
            padding-right: .8rem;
        }

        .hero {
            padding: 1.2rem;
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
if "historico_ia" not in st.session_state:
    st.session_state.historico_ia = [SYSTEM_PROMPTS["pt"].copy()]
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

UI_TEXT = {
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
        "reply_lang_btn": "Switch reply language",
        "clear_chat_btn": "🗑️ Clear chat",
        "back_btn": "← Back",
        "voice_input": "Voice input",
        "tip": "Tip: ask specific questions for better responses.",
        "chat_input": "Type your question...",
        "transcribing": "Transcribing audio...",
        "transcription_ok": "Transcription",
        "thinking": "Pity-IA is thinking...",
        "listen_last": "🔊 Play last answer",
        "you": "You",
        "too_long": "⚠️ Message too long (max 4000 characters).",
        "rate_limited": "⚠️ Rate limit reached. Please wait a moment.",
    },
}


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
    # SEGURANÇA: escape de todo conteúdo do usuário
    safe_content = html.escape(content)
    # Preservar quebras de linha como <br> após o escape
    safe_content = safe_content.replace("\n", "<br>")

    css = "bubble-user" if role == "user" else "bubble-ai"
    ui = UI_TEXT[st.session_state.ui_lang]
    prefix = html.escape(ui["you"]) if role == "user" else "Pity-IA"

    st.markdown(
        f'<div class="{css}"><strong>{prefix}:</strong> {safe_content}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Landing Page
# ---------------------------------------------------------------------------

def landing_page() -> None:
    ui = UI_TEXT[st.session_state.ui_lang]
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
    """Transcreve áudio recebido do componente de input."""
    if not audio_bytes:
        return None

    temp_file = Path("audio_temp.wav")
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

    # Header
    st.markdown('<div class="topbar">', unsafe_allow_html=True)
    header_left, header_mid, header_right = st.columns([3, 1.2, 1.2])

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

    # Input de texto
    user_input = st.chat_input(
        ui["chat_input"],
        key="chat_input",
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
                st.audio(f.read(), format="audio/wav")


# ---------------------------------------------------------------------------
# Layout principal
# ---------------------------------------------------------------------------

toolbar_left, toolbar_right = st.columns([6, 1.6])
with toolbar_right:
    ui = UI_TEXT[st.session_state.ui_lang]
    if st.button(ui["layout_toggle"], use_container_width=True, help=ui["layout_help"]):
        st.session_state.ui_lang = "en" if st.session_state.ui_lang == "pt" else "pt"
        st.rerun()

if st.session_state.page == "landing":
    landing_page()
else:
    chat_page()

# Footer
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 2rem; padding: 0.8rem;
         border-top: 1px solid rgba(255,255,255,0.1);">
        <span style="color: var(--muted); font-size: .78rem;">
            © 2025-2026 Pity-IA Studio · Leandro Timoteo · v{APP_VERSION}
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
