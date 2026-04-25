from src.config import APIFY_TOKEN


def main():
    if APIFY_TOKEN:
        print("Apify token is loaded.")
    else:
        print("APIFY_TOKEN is missing.")


if __name__ == "__main__":
    main()
