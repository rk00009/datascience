from __future__ import annotations

import time

from app.search_engine import search_multiple_queries
from app.url_filter import filter_serp_results


# ============================================================
# CONFIG
# ============================================================

TARGET_MARKET = "Germany"

QUERIES = [
    "peanut importer Germany bulk purchase procurement international supplier",
    "Erdnüsse Importeur Deutschland Großhandel Einkauf Lieferanten",
    "groundnut kernels importer Germany supplier requirement RFQ",
]


SEARCH_PLAN = {
    "original_query": "Find groundnut buyers in Germany",

    "product": "groundnut",

    "product_synonyms": [
        "peanuts",
        "groundnut kernels",
        "peanut kernels",
        "raw peanuts",
        "shelled peanuts",
    ],

    "target_market": TARGET_MARKET,

    "buyer_types": [
        "importer",
        "distributor",
        "wholesaler",
        "food_processor",
        "trading_company",
    ],

    "buying_signals": [
        "product importer",
        "bulk purchase",
        "procurement",
        "sourcing",
        "supplier requirement",
        "RFQ",
        "international supplier",
    ],

    "languages": [
        "English",
        "German",
    ],

    "intent": "buyer_discovery",

    "max_results": 50,

    "max_queries": 8,
}


# ============================================================
# SAFE VALUE READER
# ============================================================

def get_value(obj, *fields, default=None):
    """
    Works with:
        - dict
        - Pydantic model
        - normal Python object
    """

    for field in fields:

        if isinstance(obj, dict):
            value = obj.get(field)

        else:
            value = getattr(
                obj,
                field,
                None
            )

        if value is not None:
            return value

    return default


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("==============================")
    print("SERP TEST")
    print("==============================")

    # --------------------------------------------------------
    # SERP
    # --------------------------------------------------------

    serp_start = time.perf_counter()

    try:

        serp_results = search_multiple_queries(
            QUERIES,
            num_results=10
        )

    except Exception as exc:

        print()
        print("==============================")
        print("SERP FAILED")
        print("==============================")

        print(exc)

        raise

    serp_time = (
        time.perf_counter()
        - serp_start
    )

    print()
    print(
        f"Total SERP results: "
        f"{len(serp_results)}"
    )

    print(
        f"SERP Time: "
        f"{serp_time:.2f}s"
    )

    if not serp_results:

        print()
        print(
            "No SERP results returned."
        )

        return

    # --------------------------------------------------------
    # HARD URL FILTER
    # --------------------------------------------------------

    print()
    print("==============================")
    print("HARD FILTER")
    print("==============================")

    filter_start = time.perf_counter()

    filtered = filter_serp_results(
        serp_results=serp_results,
        search_plan=SEARCH_PLAN,
        target_market=TARGET_MARKET,
        minimum_score=45,
    )

    filter_time = (
        time.perf_counter()
        - filter_start
    )

    # --------------------------------------------------------
    # NORMALIZE FILTER RESPONSE
    # --------------------------------------------------------

    if hasattr(
        filtered,
        "results"
    ):

        candidates = filtered.results

    elif isinstance(
        filtered,
        list
    ):

        candidates = filtered

    else:

        candidates = []

    # --------------------------------------------------------
    # CANDIDATES
    # --------------------------------------------------------

    print()
    print("==============================")
    print("CANDIDATES")
    print("==============================")

    print(
        f"Accepted candidates: "
        f"{len(candidates)}"
    )

    print(
        f"Filter Time: "
        f"{filter_time:.2f}s"
    )

    # --------------------------------------------------------
    # PRINT RESULTS
    # --------------------------------------------------------

    for index, result in enumerate(
        candidates,
        start=1
    ):

        title = get_value(
            result,
            "title",
            default="(no title)"
        )

        url = get_value(
            result,
            "url",
            default="(no url)"
        )

        domain = get_value(
            result,
            "domain",
            default="(unknown)"
        )

        score = get_value(
            result,
            "relevance_score",
            default=0
        )

        is_lead = get_value(
            result,
            "is_lead",
            default=False
        )

        is_company_candidate = get_value(
            result,
            "is_company_candidate",
            default=False
        )

        company_type = get_value(
            result,
            "company_type",
            default=None
        )

        reason = get_value(
            result,
            "reason",
            default=""
        )

        snippet = get_value(
            result,
            "snippet",
            default=""
        )

        print()
        print(
            f"{index}. {title}"
        )

        print(
            f"URL: {url}"
        )

        print(
            f"Domain: {domain}"
        )

        print(
            f"Score: {score}"
        )

        print(
            f"Lead: {is_lead}"
        )

        print(
            f"Company Candidate: "
            f"{is_company_candidate}"
        )

        print(
            f"Company Type: "
            f"{company_type}"
        )

        if reason:
            print(
                f"Reason: {reason}"
            )

        if snippet:
            print(
                f"Snippet: {snippet}"
            )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total_time = (
        time.perf_counter()
        - serp_start
    )

    print()
    print("==============================")
    print("FILTER SUMMARY")
    print("==============================")

    print(
        f"SERP results: "
        f"{len(serp_results)}"
    )

    print(
        f"Accepted candidates: "
        f"{len(candidates)}"
    )

    print(
        f"SERP Time: "
        f"{serp_time:.2f}s"
    )

    print(
        f"Filter Time: "
        f"{filter_time:.2f}s"
    )

    print(
        f"Total Time: "
        f"{total_time:.2f}s"
    )

    print()
    print("==============================")
    print("TEST COMPLETE")
    print("==============================")


if __name__ == "__main__":
    main()