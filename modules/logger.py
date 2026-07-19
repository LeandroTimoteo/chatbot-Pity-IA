"""Sistema de logging centralizado e estruturado para Pity-IA.

Fornece configuração de logging profissional com:
- Rotação de logs
- Formatação estruturada
- Níveis apropriados por módulo
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

# Diretório de logs
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Formato estruturado
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Obtém ou cria um logger com configuração profissional.

    Args:
        name: Nome do logger (geralmente __name__)
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Nome do arquivo de log (opcional)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)

    # Evitar duplicação de handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Handler para console (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Handler para arquivo (com rotação)
    if log_file:
        log_path = LOGS_DIR / log_file
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,  # Manter 5 backups
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)  # Arquivo sempre recebe DEBUG
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Evitar propagação para root logger
    logger.propagate = False

    return logger


def setup_logging(debug: bool = False) -> None:
    """Configura logging global para toda a aplicação.

    Args:
        debug: Se True, usa DEBUG level em vez de INFO
    """
    level = logging.DEBUG if debug else logging.INFO

    # Logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Handler para console
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Handler para arquivo
    file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


# Logger padrão do módulo
logger = get_logger(__name__, log_file="app.log")
