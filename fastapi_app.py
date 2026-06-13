"""Pity-IA FastAPI Web Application.

Segurança:
- CORS restrito
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Rate limiting simples por IP
- Validação e sanitização de input
- Sem exposição de dados internos na resposta
"""

import html
import time
from collections import defaultdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from starlette.middleware.base import BaseHTTPMiddleware

from modules.online import gerar_resposta_online

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
INDEX_FILE = WEB_DIR / "index.html"

MAX_PROMPT_LENGTH = 4000
RATE_LIMIT_WINDOW = 60  # segundos
RATE_LIMIT_MAX = 30  # requests por janela

# ---------------------------------------------------------------------------
# Rate Limiting por IP
# ---------------------------------------------------------------------------

_rate_limit_store: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting simples por IP."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()

            # Limpar timestamps antigos
            _rate_limit_store[client_ip] = [
                ts for ts in _rate_limit_store[client_ip]
                if now - ts < RATE_LIMIT_WINDOW
            ]

            if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_MAX:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again later."},
                )

            _rate_limit_store[client_ip].append(now)

        return await call_next(request)


# ---------------------------------------------------------------------------
# Security Headers Middleware
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adiciona headers de segurança em todas as respostas."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(self), geolocation=()"
        )
        return response


# ---------------------------------------------------------------------------
# App FastAPI
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Pity-IA API",
    version="2.0.0",
    docs_url=None,  # Desabilitar Swagger em produção
    redoc_url=None,  # Desabilitar ReDoc em produção
)

# CORS restrito
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chatbot-pity-ia.streamlit.app",
        "http://localhost:8501",
        "http://localhost:8502",
        "http://localhost:8503",
        "http://127.0.0.1:8503",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Middlewares de segurança
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------------------------------------------------------------------------
# Modelos de dados
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Request model para o endpoint de chat com validação."""

    prompt: str
    idioma: str = "pt"

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Prompt não pode ser vazio.")
        if len(v) > MAX_PROMPT_LENGTH:
            raise ValueError(
                f"Prompt excede o limite de {MAX_PROMPT_LENGTH} caracteres."
            )
        return v

    @field_validator("idioma")
    @classmethod
    def validate_idioma(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in ("pt", "en"):
            return "pt"
        return v


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.get("/")
def home() -> FileResponse:
    """Serve a página principal."""
    return FileResponse(INDEX_FILE)


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": "2.0.0"}


@app.post("/api/chat")
def chat(payload: ChatRequest) -> dict:
    """Endpoint de chat com a IA.

    Retorna resposta no idioma selecionado, sem expor dados internos.
    """
    resposta = gerar_resposta_online(payload.prompt, payload.idioma)

    if not isinstance(resposta, dict):
        raise HTTPException(status_code=500, detail="Erro interno.")

    sucesso = bool(resposta.get("sucesso"))
    texto = resposta.get(payload.idioma, "")

    return {
        "ok": sucesso,
        "idioma": payload.idioma,
        "texto": texto,
    }
