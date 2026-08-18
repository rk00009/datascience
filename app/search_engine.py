import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from dotenv import load_dotenv

load_dotenv()


SERP_API_KEY = os.getenv("SERP_API_KEY")

SERP_API_URL = "https://serpapi.com/search.json"

MAX_WORKERS = 5
DEFAULT_RESULTS = 5


def search_google(
    query: str,
    num_results: int = DEFAULT_RESULTS
) -> list[dict]:

    if not SERP_API_KEY:
        raise ValueError(
            "SERP_API_KEY is missing from .env"
        )

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
        "num": min(num_results, 10),
        "hl": "en"
    }

    response = requests.get(
        SERP_API_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for item in data.get(
        "organic_results",
        []
    ):

        url = item.get("link")

        if not url:
            continue

        results.append({
            "title": item.get(
                "title",
                ""
            ),
            "url": url,
            "snippet": item.get(
                "snippet",
                ""
            )
        })

    return results


def search_multiple_queries(
    queries: list[str],
    num_results: int = DEFAULT_RESULTS
) -> list[dict]:

    """
    Execute multiple SERP searches concurrently.
    """

    all_results = []


    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = {

            executor.submit(
                search_google,
                query,
                num_results
            ): query

            for query in queries

        }


        for future in as_completed(
            futures
        ):

            query = futures[future]

            try:

                results = future.result()

                print(
                    f"SERP completed: "
                    f"{query} "
                    f"-> {len(results)} results"
                )

                all_results.extend(
                    results
                )

            except Exception as e:

                print(
                    f"SERP failed: "
                    f"{query} -> {e}"
                )


    # ========================================================
    # REMOVE DUPLICATE URLS
    # ========================================================

    unique_results = []

    seen_urls = set()


    for result in all_results:

        url = result["url"]

        # Remove fragments
        clean_url = url.split("#")[0]

        # Remove trailing slash
        clean_url = clean_url.rstrip("/")


        if clean_url in seen_urls:
            continue


        seen_urls.add(
            clean_url
        )


        result["url"] = clean_url

        unique_results.append(
            result
        )


    return unique_results