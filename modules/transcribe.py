"""Módulo de transcrição de áudio (Speech-to-Text) usando SpeechRecognition.

Segurança:
- Valida existência e tamanho do arquivo de áudio
- Limite de 10 MB para prevenir abuso
- Tratamento robusto de exceções
"""

from pathlib import Path

from modules.logger import get_logger

logger = get_logger(__name__, log_file="app.log")

try:
    import speech_recognition as sr
except ImportError:
    sr = None
    logger.warning("SpeechRecognition não instalado. Transcrição indisponível.")

# Limites de segurança
MAX_AUDIO_SIZE_MB = 10
MAX_AUDIO_SIZE_BYTES = MAX_AUDIO_SIZE_MB * 1024 * 1024


def transcribe_audio(audio_path: str, language: str = "pt-BR") -> str:
    """Transcreve um arquivo de áudio em texto.

    Args:
        audio_path: Caminho para o arquivo de áudio.
        language: Código do idioma para transcrição (ex: "pt-BR", "en-US").

    Returns:
        Texto transcrito ou mensagem de erro.
    """
    if sr is None:
        return "⚠️ Reconhecimento de voz indisponível (dependência SpeechRecognition não instalada)."

    # Validar caminho do arquivo
    path = Path(audio_path)
    if not path.exists():
        logger.error("Arquivo de áudio não encontrado: %s", audio_path)
        return "⚠️ Arquivo de áudio não encontrado."

    if not path.is_file():
        logger.error("Caminho não é um arquivo: %s", audio_path)
        return "⚠️ Caminho inválido para áudio."

    # Validar tamanho do arquivo
    file_size = path.stat().st_size
    if file_size > MAX_AUDIO_SIZE_BYTES:
        logger.warning(
            "Arquivo de áudio muito grande: %.1f MB (max: %d MB)",
            file_size / (1024 * 1024),
            MAX_AUDIO_SIZE_MB,
        )
        return f"⚠️ Arquivo de áudio muito grande (max {MAX_AUDIO_SIZE_MB} MB)."

    if file_size == 0:
        return "⚠️ Arquivo de áudio está vazio."

    # Validar idioma
    language = str(language).strip()
    if not language:
        language = "pt-BR"

    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(str(path)) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio, language=language)
        return text

    except sr.UnknownValueError:
        return "⚠️ Não foi possível entender o áudio."
    except sr.RequestError as exc:
        logger.error("Erro no serviço de reconhecimento: %s", exc)
        return f"⚠️ Erro no serviço de reconhecimento: {exc}"
    except Exception as exc:
        logger.error("Erro ao processar áudio: %s", exc, exc_info=True)
        return f"⚠️ Erro ao processar o áudio: {exc}"
