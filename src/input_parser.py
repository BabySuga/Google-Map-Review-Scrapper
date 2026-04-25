def parse_urls(raw_text: str) -> list[str]:
    urls = []
    for line in raw_text.splitlines():
        url = line.strip()
        if url:
            urls.append(url)
    return urls

