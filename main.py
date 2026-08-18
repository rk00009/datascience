import time

from app.planner import create_search_plan
from app.query_generator import generate_queries
from app.query_ranker import rank_queries
from app.query_deduplicator import remove_duplicate_queries
from app.search_engine import search_google
from app.url_filter import classify_urls

from app.schemas import SERPResultList


def print_stage_time(stage_name, start_time):

    elapsed = time.perf_counter() - start_time

    print(
        f"\n{stage_name} Time: {elapsed:.2f} seconds"
    )

    return elapsed


def main():

    total_start = time.perf_counter()


    # =====================================================
    # 1. USER INPUT
    # =====================================================

    user_query = input(
        "Enter buyer requirement: "
    )


    # =====================================================
    # 2. SEARCH PLANNER
    # =====================================================

    print("\n==============================")
    print("CREATING SEARCH PLAN")
    print("==============================\n")


    start_time = time.perf_counter()


    search_plan = create_search_plan(
        user_query
    )


    print(
        search_plan.model_dump_json(
            indent=2
        )
    )


    print_stage_time(
        "Search Planner",
        start_time
    )


    # =====================================================
    # 3. QUERY GENERATOR
    # =====================================================

    print("\n==============================")
    print("GENERATING SEARCH QUERIES")
    print("==============================\n")


    start_time = time.perf_counter()


    search_queries = generate_queries(
        search_plan
    )


    for query in search_queries.queries:

        print(
            query.model_dump_json(
                indent=2
            )
        )


    print_stage_time(
        "Query Generator",
        start_time
    )


    # =====================================================
    # 4. QUERY RANKER
    # =====================================================

    print("\n==============================")
    print("RANKING QUERIES")
    print("==============================\n")


    start_time = time.perf_counter()


    ranked_queries = rank_queries(
        search_queries
    )


    for query in ranked_queries.selected_queries:

        print(
            query.model_dump_json(
                indent=2
            )
        )


    print_stage_time(
        "Query Ranker",
        start_time
    )


    # =====================================================
    # 5. QUERY DEDUPLICATION
    # =====================================================

    print("\n==============================")
    print("REMOVING DUPLICATE QUERIES")
    print("==============================\n")


    start_time = time.perf_counter()


    final_queries = remove_duplicate_queries(
        ranked_queries.selected_queries
    )


    print(
        f"Final Unique Queries: "
        f"{len(final_queries)}"
    )


    for query in final_queries:

        print(
            query.model_dump_json(
                indent=2
            )
        )


    print_stage_time(
        "Query Deduplication",
        start_time
    )


    # =====================================================
    # 6. SERP API SEARCH
    # =====================================================

    print("\n==============================")
    print("SEARCHING USING SERP API")
    print("==============================\n")


    start_time = time.perf_counter()


    all_results = []


    for index, query in enumerate(
        final_queries,
        start=1
    ):

        print(
            f"\n[{index}/{len(final_queries)}] "
            f"Searching: {query.query}"
        )


        query_start = time.perf_counter()


        try:

            results = search_google(
                query.query,
                num_results=10
            )


            all_results.extend(
                results
            )


            print(
                f"  Results: {len(results)}"
            )

            print(
                f"  Time: "
                f"{time.perf_counter() - query_start:.2f}s"
            )


        except Exception as e:

            print(
                f"  ERROR: {e}"
            )


    print(
        f"\nTotal SERP Results: "
        f"{len(all_results)}"
    )


    print_stage_time(
        "SERP Search",
        start_time
    )


    # =====================================================
    # 7. URL CLASSIFICATION
    # =====================================================

    print("\n==============================")
    print("CLASSIFYING URLS")
    print("==============================\n")


    start_time = time.perf_counter()


    serp_data = SERPResultList(
        results=all_results
    )


    try:

        classified_urls = classify_urls(
            serp_data
        )


    except Exception as e:

        print(
            f"URL classification failed: {e}"
        )

        return


    print_stage_time(
        "URL Classification",
        start_time
    )


    # =====================================================
    # 8. DISPLAY CLASSIFIED RESULTS
    # =====================================================

    print("\n==============================")
    print("CLASSIFIED RESULTS")
    print("==============================\n")


    for result in classified_urls.results:

        print(
            result.model_dump_json(
                indent=2
            )
        )


    # =====================================================
    # 9. FILTER ACTUAL LEADS
    # =====================================================

    valid_leads = [

        result

        for result in classified_urls.results

        if result.is_lead

    ]


    print("\n==============================")
    print("LEAD SUMMARY")
    print("==============================\n")


    print(
        f"Total SERP Results: "
        f"{len(all_results)}"
    )


    print(
        f"Classified Results: "
        f"{len(classified_urls.results)}"
    )


    print(
        f"Potential Leads: "
        f"{len(valid_leads)}"
    )


    # =====================================================
    # 10. SHOW ONLY VALID LEADS
    # =====================================================

    print("\n==============================")
    print("VALID LEAD URLS")
    print("==============================\n")


    for index, lead in enumerate(
        valid_leads,
        start=1
    ):

        print(
            f"\nLead {index}"
        )

        print(
            f"Company: "
            f"{lead.company_name}"
        )

        print(
            f"URL: "
            f"{lead.url}"
        )

        print(
            f"Type: "
            f"{lead.source_type}"
        )

        print(
            f"Probability: "
            f"{lead.lead_probability}"
        )

        print(
            f"Reason: "
            f"{lead.reason}"
        )


    # =====================================================
    # 11. TOTAL PIPELINE TIME
    # =====================================================

    total_time = (
        time.perf_counter()
        - total_start
    )


    print("\n==============================")
    print("PERFORMANCE SUMMARY")
    print("==============================\n")


    print(
        f"Total Pipeline Time: "
        f"{total_time:.2f} seconds"
    )


    print(
        f"Total Pipeline Time: "
        f"{total_time / 60:.2f} minutes"
    )


    print("\n==============================")
    print("PIPELINE COMPLETE")
    print("==============================")



if __name__ == "__main__":

    main()