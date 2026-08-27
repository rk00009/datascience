import time

from app.planner import create_search_plan
from app.query_generator import generate_queries
from app.query_ranker import rank_queries
from app.query_deduplicator import remove_duplicate_queries

from app.search_engine import search_multiple_queries
from app.url_filter import classify_urls

from app.web_crawler import crawl_websites
from app.company_extractor import (
    extract_multiple_company_profiles
)

from app.schemas import SERPResultList


def main():

    total_start = time.perf_counter()


    # ========================================================
    # 1. USER INPUT
    # ========================================================

    user_query = input(
        "Enter buyer requirement: "
    )


    # ========================================================
    # 2. SEARCH PLAN
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "CREATING SEARCH PLAN"
    )

    print(
        "=============================="
    )


    start = time.perf_counter()


    search_plan = create_search_plan(
        user_query
    )


    print(
        search_plan.model_dump_json(
            indent=2
        )
    )


    print(
        f"\nTime: "
        f"{time.perf_counter() - start:.2f}s"
    )


    # ========================================================
    # 3. QUERY GENERATION
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "GENERATING SEARCH QUERIES"
    )

    print(
        "=============================="
    )


    start = time.perf_counter()


    generated_queries = generate_queries(
        search_plan
    )


    for query in generated_queries.queries:

        print(
            query.model_dump_json(
                indent=2
            )
        )


    print(
        f"\nTime: "
        f"{time.perf_counter() - start:.2f}s"
    )


    # ========================================================
    # 4. QUERY RANKING
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "RANKING QUERIES"
    )

    print(
        "=============================="
    )


    start = time.perf_counter()


    ranked_queries = rank_queries(
        generated_queries
    )


    for query in ranked_queries.selected_queries:

        print(
            query.model_dump_json(
                indent=2
            )
        )


    print(
        f"\nTime: "
        f"{time.perf_counter() - start:.2f}s"
    )


    # ========================================================
    # 5. DEDUPLICATION
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "REMOVING DUPLICATE QUERIES"
    )

    print(
        "=============================="
    )


    final_queries = remove_duplicate_queries(

        ranked_queries.selected_queries

    )


    print(
        f"Final queries: "
        f"{len(final_queries)}"
    )


    for query in final_queries:

        print(
            f"  - {query.query}"
        )


    # ========================================================
    # 6. SERP SEARCH
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "SERP SEARCH"
    )

    print(
        "=============================="
    )


    start = time.perf_counter()


    query_strings = [

        query.query

        for query in final_queries

    ]


    all_results = search_multiple_queries(

        query_strings,

        num_results=5

    )


    print(
        f"\nSERP results: "
        f"{len(all_results)}"
    )


    print(
        f"SERP Time: "
        f"{time.perf_counter() - start:.2f}s"
    )


    # ========================================================
    # 7. URL CLASSIFICATION
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "CLASSIFYING SERP RESULTS"
    )

    print(
        "=============================="
    )


    start = time.perf_counter()


    serp_data = SERPResultList(
        results=all_results
    )


    classified_urls = classify_urls(
        serp_data
    )


    print(
        f"\nClassified: "
        f"{len(classified_urls.results)}"
    )


    print(
        f"Classification Time: "
        f"{time.perf_counter() - start:.2f}s"
    )


    # ========================================================
    # 8. GET ONLY REAL LEADS
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "SELECTING LEADS"
    )

    print(
        "=============================="
    )


    leads = [

        result

        for result
        in classified_urls.results

        if result.is_lead

    ]


    # Keep MVP small.

    leads = leads[:10]


    print(
        f"Selected leads: "
        f"{len(leads)}"
    )


    for index, lead in enumerate(
        leads,
        start=1
    ):

        print()

        print(
            f"{index}. Lead"
        )

        print(
            f"URL: {lead.url}"
        )

        print(
            f"Domain: {lead.domain}"
        )

        print(
            f"Company Type: {lead.company_type}"
        )

        print(
            f"Lead: {lead.is_lead}"
        )

        print(
            f"Company Candidate: {lead.is_company_candidate}"
        )

        print(
            f"Score: {lead.relevance_score}"
        )

        print(
            f"Reason: {lead.reason}"
        )


    # ========================================================
    # 9. CRAWLING
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "CRAWLING COMPANIES"
    )

    print(
        "=============================="
    )


    start = time.perf_counter()


    lead_urls = [

        lead.url

        for lead in leads

    ]


    scraped_data = crawl_websites(
        lead_urls
    )


    successful_crawls = [

        item

        for item in scraped_data

        if item.get(
            "crawl_success"
        )

    ]


    print(
        f"\nSuccessful crawls: "
        f"{len(successful_crawls)}"
    )


    print(
        f"Crawler Time: "
        f"{time.perf_counter() - start:.2f}s"
    )


    # ========================================================
    # 10. COMPANY EXTRACTION
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "EXTRACTING COMPANY PROFILES"
    )

    print(
        "=============================="
    )


    start = time.perf_counter()


    profiles = extract_multiple_company_profiles(

        scraped_data

    )


    print(
        f"\nProfiles extracted: "
        f"{len(profiles)}"
    )


    print(
        f"Extraction Time: "
        f"{time.perf_counter() - start:.2f}s"
    )


    # ========================================================
    # 11. FINAL RESULTS
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "FINAL BUYER RESULTS"
    )

    print(
        "=============================="
    )


    for index, profile in enumerate(

        profiles,

        start=1

    ):

        print(
            f"\nBUYER {index}"
        )

        print(
            "------------------------------"
        )


        print(
            f"Company: "
            f"{profile.company_name}"
        )


        print(
            f"Website: "
            f"{profile.website}"
        )


        print(
            f"Country: "
            f"{profile.country}"
        )


        print(
            f"Buyer Type: "
            f"{profile.buyer_type}"
        )


        print(
            f"Products: "
            f"{profile.products}"
        )


        print(
            f"Importing Activity: "
            f"{profile.importing_activity}"
        )


        print(
            f"Buying Signals: "
            f"{profile.buying_signals}"
        )


        print(
            f"Email: "
            f"{profile.email}"
        )


        print(
            f"Phone: "
            f"{profile.phone}"
        )


    # ========================================================
    # 12. TOTAL TIME
    # ========================================================

    total_time = (
        time.perf_counter()
        - total_start
    )


    print(
        "\n=============================="
    )

    print(
        "PIPELINE PERFORMANCE"
    )

    print(
        "=============================="
    )


    print(
        f"Total Time: "
        f"{total_time:.2f}s"
    )


    print(
        f"Total Time: "
        f"{total_time / 60:.2f} minutes"
    )


    print(
        "\nPIPELINE COMPLETE"
    )


if __name__ == "__main__":
    main()