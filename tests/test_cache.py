"""Testes para o módulo de cache."""

import time
import pytest
from modules.cache import ResponseCache, cached_response, get_cache_stats, clear_cache


class TestResponseCache:
    """Testes da classe ResponseCache."""

    @pytest.fixture
    def cache(self):
        """Fixture que cria um novo cache para cada teste."""
        return ResponseCache(max_items=10, default_ttl=1)

    def test_set_and_get(self, cache):
        """Testa armazenar e recuperar um valor."""
        key = "test_key"
        value = "test_value"
        cache.set(key, value)
        assert cache.get(key) == value

    def test_get_nonexistent(self, cache):
        """Testa recuperar chave que não existe."""
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self, cache):
        """Testa que item expira após TTL."""
        key = "test_key"
        cache.set(key, "value", ttl=1)
        assert cache.get(key) == "value"

        # Esperar TTL expirar
        time.sleep(1.1)
        assert cache.get(key) is None

    def test_generate_key(self, cache):
        """Testa geração de chave hash."""
        key1 = cache._generate_key("prompt1", "pt")
        key2 = cache._generate_key("prompt1", "pt")
        key3 = cache._generate_key("prompt2", "pt")

        assert key1 == key2  # Mesma entrada = mesma chave
        assert key1 != key3  # Entradas diferentes = chaves diferentes

    def test_max_items_limit(self, cache):
        """Testa limite de tamanho do cache."""
        # Preencher cache até o limite
        for i in range(10):
            cache.set(f"key_{i}", f"value_{i}")

        assert len(cache._cache) == 10

        # Adicionar um item deve remover o mais antigo
        cache.set("key_11", "value_11")
        assert len(cache._cache) == 10

    def test_cache_stats(self, cache):
        """Testa estatísticas do cache."""
        cache.set("key1", "value1")
        assert cache.get("key1") is not None  # 1 hit
        assert cache.get("key2") is None  # 1 miss

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert "50.0%" in stats["hit_rate"]

    def test_invalidate(self, cache):
        """Testa invalidação de cache."""
        cache.set("key", "value")
        assert cache.get("key") == "value"

        cache.invalidate("key")
        assert cache.get("key") is None

    def test_clear(self, cache):
        """Testa limpeza completa do cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert len(cache._cache) == 2

        cache.clear()
        assert len(cache._cache) == 0


class TestCachedResponseDecorator:
    """Testes do decorator @cached_response."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Limpa cache antes e depois de cada teste."""
        clear_cache()
        yield
        clear_cache()

    def test_decorator_caches_result(self):
        """Testa que o decorator cacheia o resultado."""
        call_count = 0

        @cached_response(ttl=60)
        def slow_function(prompt: str, idioma: str = "pt") -> str:
            nonlocal call_count
            call_count += 1
            return f"Response for {prompt} in {idioma}"

        # Primeira chamada deve executar a função
        result1 = slow_function("test prompt", idioma="pt")
        assert call_count == 1
        assert result1 == "Response for test prompt in pt"

        # Segunda chamada com mesmos args deve retornar do cache
        result2 = slow_function("test prompt", idioma="pt")
        assert call_count == 1  # Não incrementou
        assert result2 == result1

    def test_decorator_different_languages(self):
        """Testa que prompts com idiomas diferentes têm cache separado."""
        call_count = 0

        @cached_response(ttl=60)
        def get_response(prompt: str, idioma: str = "pt") -> str:
            nonlocal call_count
            call_count += 1
            return f"{prompt}:{idioma}"

        get_response("Hello", idioma="pt")
        get_response("Hello", idioma="en")

        assert call_count == 2  # Ambas as chamadas executaram


class TestCacheGlobalFunctions:
    """Testes das funções globais de cache."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Limpa cache antes e depois de cada teste."""
        clear_cache()
        yield
        clear_cache()

    def test_get_cache_stats(self):
        """Testa função get_cache_stats."""
        @cached_response(ttl=60)
        def dummy(prompt: str, idioma: str = "pt") -> str:
            return "response"

        dummy("test", idioma="pt")
        dummy("test", idioma="pt")
        dummy("other", idioma="pt")

        stats = get_cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 2

    def test_clear_cache_global(self):
        """Testa função clear_cache global."""
        @cached_response(ttl=60)
        def dummy(prompt: str, idioma: str = "pt") -> str:
            return "response"

        dummy("test", idioma="pt")
        assert get_cache_stats()["items"] > 0

        clear_cache()
        assert get_cache_stats()["items"] == 0
