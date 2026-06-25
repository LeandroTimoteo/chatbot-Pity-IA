"""Módulo de síntese de fala (Text-to-Speech) usando gTTS.

Segurança:
- Áudio gerado em diretório temporário seguro
- Idioma validado contra whitelist
- Texto limitado em tamanho para prevenir abuso
"""

import logging
import tempfile
from pathlib import Path

from gtts import gTTS

logger = logging.getLogger(__name__)

# Limites de segurança
MAX_TTS_LENGTH = 1000
ALLOWED_LANGUAGES = {"pt", "en", "es", "fr", "de"}

# Diretório temporário persistente para a sessão
_TEMP_DIR = Path(tempfile.mkdtemp(prefix="pityia_audio_"))


def speak_text(
    texto: str,
    idioma: str = "pt",
    nome_arquivo: str | None = None,
) -> str | None:
    """Gera um arquivo de áudio a partir de texto.

    Args:
        texto: Texto para converter em fala.
        idioma: Código do idioma ("pt", "en", etc.).
        nome_arquivo: Nome do arquivo de saída (opcional).

    Returns:
        Caminho absoluto do arquivo de áudio, ou None em caso de erro.
    """
    try:
        if not texto or not texto.strip():
            logger.warning("Texto vazio recebido para TTS.")
            return None

        # Validação de idioma
        idioma = str(idioma).strip().lower()
        if idioma not in ALLOWED_LANGUAGES:
            logger.warning("Idioma '%s' não suportado, usando 'pt'.", idioma)
            idioma = "pt"

        # Limitar tamanho do texto
        texto_limpo = texto.strip()
        if len(texto_limpo) > MAX_TTS_LENGTH:
            texto_limpo = texto_limpo[:MAX_TTS_LENGTH]
            logger.info("Texto truncado para %d caracteres.", MAX_TTS_LENGTH)

        # Gerar áudio em diretório temporário seguro
        if nome_arquivo:
            # Sanitizar nome do arquivo (remover path traversal)
            safe_name = Path(nome_arquivo).name
            audio_path = _TEMP_DIR / safe_name
        else:
            audio_path = _TEMP_DIR / "resposta_audio.mp3"

        tts = gTTS(text=texto_limpo, lang=idioma)
        tts.save(str(audio_path))

        if audio_path.exists():
            return str(audio_path)

        return None

    except Exception as exc:
        logger.error("Erro ao gerar áudio TTS: %s", exc, exc_info=True)
        return None
