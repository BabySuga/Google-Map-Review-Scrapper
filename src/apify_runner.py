from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


RAW_DATA_DIR = Path("data/raw")


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


def _build_start_urls(urls: list[str]) -> list[dict[str, str]]:
    return [{"url": url} for url in _normalize_urls(urls)]


def _split_keywords(keywords: str) -> list[str]:
    parts = []
    for chunk in keywords.replace("\n", ",").replace(";", ",").split(","):
        value = chunk.strip().lower()
        if value:
            parts.append(value)
    return parts


def filter_reviews(items: list[dict], keywords: str) -> list[dict]:
    terms = _split_keywords(keywords)
    if not terms:
        return items

    filtered_items = []
    for item in items:
        haystack = json.dumps(item, ensure_ascii=False).lower()
        if any(term in haystack for term in terms):
            filtered_items.append(item)
    return filtered_items


def save_raw_reviews(items: list[dict]) -> Path:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RAW_DATA_DIR / f"reviews_{timestamp}.json"
    output_path.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


def run_google_maps_reviews_scraper(
    api_token: str,
    place_urls: list[str],
    keywords: str,
    max_reviews_per_place: int = 1000,
    language: str = "id",
):
    apify_client = _load_apify_client(api_token)

    actor_input = {
        "startUrls": _build_start_urls(place_urls),
        "maxReviews": max_reviews_per_place,
        "reviewsSort": "newest",
        "language": language,
        "reviewsOrigin": "google",
        "personalData": False,
    }

    actor_run = apify_client.actor("compass/google-maps-reviews-scraper").call(
        run_input=actor_input
    )

    dataset_id = actor_run["defaultDatasetId"]
    dataset_items = apify_client.dataset(dataset_id).list_items().items
    raw_file = save_raw_reviews(dataset_items)
    filtered_items = filter_reviews(dataset_items, keywords)

    return {
        "actor_run": actor_run,
        "dataset_id": dataset_id,
        "raw_file": str(raw_file),
        "raw_items": dataset_items,
        "filtered_items": filtered_items,
    }

