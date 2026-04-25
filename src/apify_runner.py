from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RAW_DATA_DIR = Path("data/raw")
CACHE_DIR = Path("data/cache")
CACHE_INDEX_PATH = CACHE_DIR / "index.json"


def _load_apify_client(api_token: str):
    try:
        from apify_client import ApifyClient
    except ImportError as exc:
        raise RuntimeError(
            "apify-client is not installed yet. Run `python -m pip install -r requirements.txt` first."
        ) from exc

    return ApifyClient(api_token)


def _normalize_urls(urls: list[str]) -> list[str]:
    return [url.strip() for url in urls if url and url.strip()]


def _split_keywords(keywords: str) -> list[str]:
    parts = []
    for chunk in keywords.replace("\n", ",").replace(";", ",").split(","):
        value = chunk.strip().lower()
        if value:
            parts.append(value)
    return parts


def _normalize_input(place_urls: list[str], keywords: str, max_reviews_per_place: int, language: str) -> dict[str, Any]:
    return {
        "place_urls": _normalize_urls(place_urls),
        "keywords": keywords.strip(),
        "max_reviews_per_place": int(max_reviews_per_place),
        "language": language.strip(),
    }


def _cache_key(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _cache_path(cache_key: str) -> Path:
    return CACHE_DIR / f"{cache_key}.json"


def _load_cache_index() -> dict[str, Any]:
    if not CACHE_INDEX_PATH.exists():
        return {}

    try:
        return json.loads(CACHE_INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_cache_index(index: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def _parse_dt(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    candidate = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(candidate)
    except ValueError:
        return None


def _format_dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat()


def _latest_review_datetime(items: list[dict[str, Any]]) -> datetime | None:
    parsed_dates = []
    for item in items:
        published = _parse_dt(item.get("publishedAtDate")) or _parse_dt(item.get("scrapedAt"))
        if published:
            parsed_dates.append(published)
    return max(parsed_dates) if parsed_dates else None


def _build_start_urls(urls: list[str]) -> list[dict[str, str]]:
    return [{"url": url} for url in _normalize_urls(urls)]


def filter_reviews(items: list[dict[str, Any]], keywords: str) -> list[dict[str, Any]]:
    terms = _split_keywords(keywords)
    if not terms:
        return items

    filtered_items = []
    for item in items:
        haystack = json.dumps(item, ensure_ascii=False).lower()
        if any(term in haystack for term in terms):
            filtered_items.append(item)
    return filtered_items


def save_raw_reviews(items: list[dict[str, Any]], cache_key: str | None = None) -> Path:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{cache_key[:8]}" if cache_key else ""
    output_path = RAW_DATA_DIR / f"reviews_{timestamp}{suffix}.json"
    output_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def _load_cached_result(cache_key: str) -> dict[str, Any] | None:
    cache_file = _cache_path(cache_key)
    if not cache_file.exists():
        return None

    try:
        return json.loads(cache_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _store_cache_result(cache_key: str, result: dict[str, Any]) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = _cache_path(cache_key)
    cache_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    index = _load_cache_index()
    index[cache_key] = {
        "cache_file": str(cache_file),
        "dataset_id": result.get("dataset_id"),
        "latest_review_date": result.get("latest_review_date"),
        "saved_at": result.get("saved_at"),
        "input": result.get("input"),
    }
    _save_cache_index(index)
    return cache_file


def run_google_maps_reviews_scraper(
    api_token: str,
    place_urls: list[str],
    keywords: str,
    max_reviews_per_place: int = 1000,
    language: str = "id",
    use_cache: bool = True,
):
    normalized_input = _normalize_input(place_urls, keywords, max_reviews_per_place, language)
    cache_key = _cache_key(normalized_input)

    if use_cache:
        cached_result = _load_cached_result(cache_key)
        if cached_result:
            cached_result["from_cache"] = True
            cached_result["status_code"] = 200
            cached_result["status_label"] = "200 OK"
            cached_result["status_message"] = "Menggunakan cache lokal."
            return cached_result

    apify_client = _load_apify_client(api_token)

    actor_input = {
        "startUrls": _build_start_urls(normalized_input["place_urls"]),
        "maxReviews": normalized_input["max_reviews_per_place"],
        "reviewsSort": "newest",
        "language": normalized_input["language"],
        "reviewsOrigin": "google",
        "personalData": False,
    }

    try:
        actor_run = apify_client.actor("compass/google-maps-reviews-scraper").call(
            run_input=actor_input
        )
    except Exception as exc:
        cached_result = _load_cached_result(cache_key)
        if cached_result:
            cached_result["from_cache"] = True
            cached_result["fallback_used"] = True
            cached_result["status_code"] = 206
            cached_result["status_label"] = "FALLBACK"
            cached_result["status_message"] = f"Apify gagal, pakai cache lokal: {exc}"
            cached_result["error"] = str(exc)
            return cached_result
        raise

    dataset_id = actor_run["defaultDatasetId"]
    dataset_items = apify_client.dataset(dataset_id).list_items().items
    raw_file = save_raw_reviews(dataset_items, cache_key=cache_key)
    filtered_items = filter_reviews(dataset_items, normalized_input["keywords"])
    latest_review_date = _format_dt(_latest_review_datetime(dataset_items))

    result = {
        "from_cache": False,
        "fallback_used": False,
        "cache_key": cache_key,
        "actor_run": actor_run,
        "dataset_id": dataset_id,
        "raw_file": str(raw_file),
        "raw_items": dataset_items,
        "filtered_items": filtered_items,
        "latest_review_date": latest_review_date,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "input": normalized_input,
        "status_code": 200,
        "status_label": "200 OK",
        "status_message": "Scraping selesai dan data baru sudah disimpan.",
    }
    _store_cache_result(cache_key, result)
    return result
