"""Testes para o módulo online (integração com IA)."""

import pytest
from unittest.mock import patch, MagicMock
from modules.online import (
    _sanitize_prompt,
    _sanitize_idioma,
    _trim_history,
    MAX_PROMPT_LENGTH,
)


class TestPromptSanitization:
    """Testes para sanitização de prompts."""

    def test_sanitize_prompt_valid(self):
        """Testa sanitização de prompt válido."""
        prompt = "  Qual é a capital do Brasil?  "
        result = _sanitize_prompt(prompt)
        assert result == "Qual é a capital do Brasil?"

    def test_sanitize_prompt_empty(self):
        """Testa que prompt vazio lança ValueError."""
        with pytest.raises(ValueError, match="Prompt não pode ser vazio"):
            _sanitize_prompt("")

    def test_sanitize_prompt_whitespace_only(self):
        """Testa que prompt com só espaços lança ValueError."""
        with pytest.raises(ValueError, match="Prompt não pode ser vazio"):
            _sanitize_prompt("   ")

    def test_sanitize_prompt_too_long(self):
        """Testa que prompt muito longo é truncado."""
        long_prompt = "a" * (MAX_PROMPT_LENGTH + 100)
        result = _sanitize_prompt(long_prompt)
        assert len(result) == MAX_PROMPT_LENGTH

    def test_sanitize_prompt_not_string(self):
        """Testa que input não-string lança ValueError."""
        with pytest.raises(ValueError, match="Prompt deve ser uma string"):
            _sanitize_prompt(123)

    def test_sanitize_prompt_special_chars(self):
        """Testa sanitização com caracteres especiais."""
        prompt = "Explique: função => lambda, @decorator, #hash"
        result = _sanitize_prompt(prompt)
        assert result == prompt


class TestIdiomaValidation:
    """Testes para validação de idioma."""

    def test_sanitize_idioma_pt(self):
        """Testa que 'pt' é validado."""
        assert _sanitize_idioma("pt") == "pt"
        assert _sanitize_idioma("PT") == "pt"
        assert _sanitize_idioma("  Pt  ") == "pt"

    def test_sanitize_idioma_en(self):
        """Testa que 'en' é validado."""
        assert _sanitize_idioma("en") == "en"
        assert _sanitize_idioma("EN") == "en"
        assert _sanitize_idioma("  En  ") == "en"

    def test_sanitize_idioma_invalid(self):
        """Testa que idioma inválido volta para padrão."""
        assert _sanitize_idioma("fr") == "pt"
        assert _sanitize_idioma("") == "pt"
        assert _sanitize_idioma("invalid") == "pt"


class TestHistoryTrimming:
    """Testes para trimming de histórico."""

    def test_trim_history_within_limit(self):
        """Testa que histórico dentro do limite não é modificado."""
        history = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Message 1"},
            {"role": "assistant", "content": "Response 1"},
        ]
        result = _trim_history(history, max_messages=10)
        assert len(result) == 3
        assert result == history

    def test_trim_history_exceeds_limit(self):
        """Testa que histórico longo é trimado."""
        history = [
            {"role": "system", "content": "System"},
        ]
        for i in range(1, 21):
            history.append({"role": "user", "content": f"Message {i}"})

        result = _trim_history(history, max_messages=5)
        assert len(result) == 5
        assert result[0]["role"] == "system"  # System prompt preservado

    def test_trim_history_preserves_system_prompt(self):
        """Testa que system prompt é sempre preservado."""
        history = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Message 1"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Response 2"},
        ]
        result = _trim_history(history, max_messages=2)
        assert len(result) == 2
        assert result[0]["role"] == "system"
        assert result[1]["content"] == "Response 2"

    def test_trim_history_empty(self):
        """Testa trimming de histórico vazio."""
        result = _trim_history([], max_messages=10)
        assert result == []


class TestSystemPrompts:
    """Testes para system prompts."""

    def test_system_prompts_exist(self):
        """Testa que system prompts existem para ambos idiomas."""
        from modules.online import SYSTEM_PROMPTS
        assert "pt" in SYSTEM_PROMPTS
        assert "en" in SYSTEM_PROMPTS
        assert SYSTEM_PROMPTS["pt"]["role"] == "system"
        assert SYSTEM_PROMPTS["en"]["role"] == "system"

    def test_system_prompts_not_empty(self):
        """Testa que system prompts têm conteúdo."""
        from modules.online import SYSTEM_PROMPTS
        assert len(SYSTEM_PROMPTS["pt"]["content"]) > 0
        assert len(SYSTEM_PROMPTS["en"]["content"]) > 0
