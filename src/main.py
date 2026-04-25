from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import APIFY_TOKEN
from src.apify_runner import run_google_maps_reviews_scraper
from src.locations import GOOGLE_MAP_URLS


def main():
    if APIFY_TOKEN:
        print("Apify token is loaded.")
    else:
        print("APIFY_TOKEN is missing.")

    print(f"Loaded {len(GOOGLE_MAP_URLS)} location URL(s).")

    if not APIFY_TOKEN:
        return

    if not GOOGLE_MAP_URLS:
        print("No Google Maps place URLs configured in src/locations.py")
        return

    result = run_google_maps_reviews_scraper(
        api_token=APIFY_TOKEN,
        place_urls=GOOGLE_MAP_URLS,
        keywords="beat",
    )
    print("Data from the dataset:", result["raw_items"])
    print(f"Dataset ID: {result['dataset_id']}")


if __name__ == "__main__":
    main()
