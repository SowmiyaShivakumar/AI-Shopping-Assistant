# app/services/log_service.py
# Logs AI search queries, model version, latency, and similarity scores

import logging
from datetime import datetime, timezone

logger = logging.getLogger("ai_search")

# In-memory search history (replace with DB for production)
search_history: list[dict] = []


def log_search(query: str, model_version: str, latency_ms: float, results: list[dict]):
    """Log a search event."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "model_version": model_version,
        "latency_ms": latency_ms,
        "result_count": len(results),
        "top_similarity": results[0]["similarity_score"] if results else None,
        "scores": [r["similarity_score"] for r in results],
    }
    search_history.append(entry)
    logger.info(
        f"[SEARCH] query='{query}' | model={model_version} | "
        f"latency={latency_ms}ms | top_score={entry['top_similarity']}"
    )
    return entry


def get_history() -> list[dict]:
    return search_history
