from app.search_engine import search_multiple_queries
from app.url_filter import filter_serp_results


queries = [

    "groundnut kernels importer Germany supplier requirement RFQ",

    "peanut importer Germany bulk purchase procurement international supplier",

    "Erdnüsse Importeur Deutschland Großhandel Einkauf Lieferanten",

]


print(
    "\n=============================="
)

print(
    "SERP TEST"
)

print(
    "=============================="
)


results = search_multiple_queries(

    queries,

    num_results=10

)


print(
    f"\nTotal SERP results: "
    f"{len(results)}"
)


print(
    "\n=============================="
)

print(
    "HARD FILTER"
)

print(
    "=============================="
)


candidates = filter_serp_results(

    results,

    target_market="Germany"

)


print(
    "\n=============================="
)

print(
    "CANDIDATES"
)

print(
    "=============================="
)


for index, result in enumerate(

    candidates,

    start=1

):

    print(
        f"\n{index}. "
        f"{result.get('title')}"
    )

    print(
        f"URL: "
        f"{result.get('url')}"
    )

    print(
        f"Domain: "
        f"{result.get('domain')}"
    )

    print(
        f"Score: "
        f"{result.get('hard_filter_score')}"
    )

    print(
        f"Snippet: "
        f"{result.get('snippet')}"
    )