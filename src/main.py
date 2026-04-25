from src.config import APIFY_TOKEN
from src.apify_runner import run_google_places_actor
from src.locations import GOOGLE_MAP_URLS


def main():
    if APIFY_TOKEN:
        print("Apify token is loaded.")
    else:
        print("APIFY_TOKEN is missing.")

    print(f"Loaded {len(GOOGLE_MAP_URLS)} location URL(s).")

    if not APIFY_TOKEN:
        return

    dataset_id, dataset_items = run_google_places_actor(
        api_token=APIFY_TOKEN,
        search_strings=["Honda Beat"],
        location_query="Indonesia",
    )
    print("Data from the dataset:", dataset_items)
    print(f"Dataset ID: {dataset_id}")


if __name__ == "__main__":
    main()
