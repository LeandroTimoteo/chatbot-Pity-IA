from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from modules.online import gerar_resposta_online


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
INDEX_FILE = WEB_DIR / "index.html"

app = FastAPI(title="Pity-IA API", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    prompt: str
    idioma: str = "pt"


@app.get("/")
def home() -> FileResponse:
    return FileResponse(INDEX_FILE)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat")
def chat(payload: ChatRequest) -> dict:
    prompt = payload.prompt.strip()
    idioma = payload.idioma.strip().lower()

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt vazio.")
    if idioma not in {"pt", "en"}:
        idioma = "pt"

    resposta = gerar_resposta_online(prompt, idioma)
    texto = resposta.get(idioma, "") if isinstance(resposta, dict) else ""

    return {
        "ok": bool(resposta.get("sucesso")) if isinstance(resposta, dict) else False,
        "idioma": idioma,
        "texto": texto,
        "raw": resposta,
    }

