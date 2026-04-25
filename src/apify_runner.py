def run_google_places_actor(api_token: str, search_strings: list[str], location_query: str):
    try:
        from apify_client import ApifyClient
    except ImportError as exc:
        raise RuntimeError(
            "apify-client is not installed yet. Install it before running this step."
        ) from exc

    apify_client = ApifyClient(api_token)

    actor_input = {
        "searchStringsArray": search_strings,
        "locationQuery": location_query,
        "maxCrawledPlacesPerSearch": 10,
        "language": "en",
    }

    print("Running the Actor...")
    actor_run = apify_client.actor("compass/crawler-google-places").call(run_input=actor_input)
    print("Actor finished:", actor_run)

    dataset_id = actor_run["defaultDatasetId"]
    dataset_items = apify_client.dataset(dataset_id).list_items().items

    return dataset_id, dataset_items

