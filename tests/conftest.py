"""Configuração e fixtures compartilhadas para testes."""

import sys
from pathlib import Path

# Adicionar diretório modules ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def pytest_configure(config):
    """Configura pytest."""
    pass
