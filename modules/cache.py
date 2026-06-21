"""Sistema de cache eficiente para Pity-IA.

Implementa cache em memória com suporte a TTL (Time-To-Live) e limite de tamanho.
Otimizado para respostas de IA e histórico de conversas.
"""

import hashlib
import json
import time
from typing import Any, Optional
from functools import wraps

from logger import get_logger

logger = get_logger(__name__, log_file="cache.log")


class ResponseCache:
    """Cache em memória com TTL e limite de tamanho."""

    def __init__(self, max_items: int = 1000, default_ttl: int = 3600):
        """Inicializa o cache.

        Args:
            max_items: Número máximo de itens em cache
            default_ttl: TTL padrão em segundos (1 hora)
        """
        self.max_items = max_items
        self.default_ttl = default_ttl
        self._cache: dict[str, dict[str, Any]] = {}
        self._hits = 0
        self._misses = 0

    def _generate_key(self, prompt: str, idioma: str = "pt") -> str:
        """Gera chave hash para um prompt."""
        content = f"{prompt}:{idioma}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Armazena um valor no cache.

        Args:
            key: Chave de cache
            value: Valor a ser armazenado
            ttl: TTL em segundos (usa default se None)
        """
        ttl = ttl or self.default_ttl

        # Remover itens expirados se necessário
        if len(self._cache) >= self.max_items:
            self._cleanup_expired()

        # Se ainda está cheio, remover item mais antigo
        if len(self._cache) >= self.max_items:
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k]["timestamp"],
            )
            logger.debug(f"Cache cheio. Removendo chave mais antiga: {oldest_key[:8]}...")
            del self._cache[oldest_key]

        self._cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl,
            "hits": 0,
        }
        logger.debug(f"Cache SET: {key[:8]}... (TTL: {ttl}s)")

    def get(self, key: str) -> Optional[Any]:
        """Recupera um valor do cache.

        Args:
            key: Chave de cache

        Returns:
            Valor em cache ou None se expirado/não encontrado
        """
        if key not in self._cache:
            self._misses += 1
            logger.debug(f"Cache MISS: {key[:8]}...")
            return None

        entry = self._cache[key]
        age = time.time() - entry["timestamp"]

        # Verificar se expirou
        if age > entry["ttl"]:
            logger.debug(f"Cache EXPIRED: {key[:8]}... (age: {age:.1f}s, ttl: {entry['ttl']}s)")
            del self._cache[key]
            self._misses += 1
            return None

        entry["hits"] += 1
        self._hits += 1
        logger.debug(
            f"Cache HIT: {key[:8]}... (age: {age:.1f}s, hits: {entry['hits']})"
        )
        return entry["value"]

    def invalidate(self, key: str) -> None:
        """Remove uma chave do cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache INVALIDATE: {key[:8]}...")

    def clear(self) -> None:
        """Limpa todo o cache."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache CLEAR: {count} itens removidos")

    def _cleanup_expired(self) -> None:
        """Remove itens expirados do cache."""
        now = time.time()
        expired_keys = [
            key
            for key, entry in self._cache.items()
            if now - entry["timestamp"] > entry["ttl"]
        ]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.debug(f"Cache CLEANUP: {len(expired_keys)} itens expirados removidos")

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatísticas do cache."""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        return {
            "items": len(self._cache),
            "max_items": self.max_items,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_requests": total_requests,
        }


# Instância global de cache
_response_cache = ResponseCache(max_items=1000, default_ttl=3600)


def cached_response(ttl: Optional[int] = None):
    """Decorator para cachear respostas de funções.

    Args:
        ttl: TTL em segundos (usa default do cache se None)

    Example:
        @cached_response(ttl=1800)
        def get_ai_response(prompt: str, idioma: str) -> str:
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extrai prompt e idioma dos argumentos
            prompt = kwargs.get("prompt") or (args[0] if args else "")
            idioma = kwargs.get("idioma", "pt") or (args[1] if len(args) > 1 else "pt")

            # Gera chave de cache
            key = _response_cache._generate_key(prompt, idioma)

            # Tenta recuperar do cache
            cached = _response_cache.get(key)
            if cached is not None:
                return cached

            # Executa função
            result = func(*args, **kwargs)

            # Armazena no cache
            _response_cache.set(key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


def get_cache_stats() -> dict[str, Any]:
    """Retorna estatísticas do cache global."""
    return _response_cache.get_stats()


def clear_cache() -> None:
    """Limpa o cache global."""
    _response_cache.clear()


def invalidate_response(prompt: str, idioma: str = "pt") -> None:
    """Invalida cache de uma resposta específica."""
    key = _response_cache._generate_key(prompt, idioma)
    _response_cache.invalidate(key)
