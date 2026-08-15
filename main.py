from app.planner import create_search_plan
from app.query_generator import generate_queries
from app.query_ranker import rank_queries
from app.query_deduplicator import remove_duplicate_queries
from app.search_engine import search_google
from app.url_filter import classify_urls

from app.schemas import SERPResultList



def main():


    # =========================================
    # 1. USER INPUT
    # =========================================

    user_query = input(
        "Enter buyer requirement: "
    )


    print("\n==============================")
    print("CREATING SEARCH PLAN")
    print("==============================\n")



    # =========================================
    # 2. SEARCH PLANNER
    # =========================================

    search_plan = create_search_plan(
        user_query
    )


    print(
        search_plan.model_dump_json(
            indent=2
        )
    )



    print("\n==============================")
    print("GENERATING SEARCH QUERIES")
    print("==============================\n")



    # =========================================
    # 3. QUERY GENERATOR
    # =========================================

    search_queries = generate_queries(
        search_plan
    )


    for query in search_queries.queries:

        print(
            query.model_dump_json(
                indent=2
            )
        )



    print("\n==============================")
    print("RANKING QUERIES")
    print("==============================\n")



    # =========================================
    # 4. QUERY RANKER
    # =========================================

    ranked_queries = rank_queries(
        search_queries
    )


    for query in ranked_queries.selected_queries:

        print(
            query.model_dump_json(
                indent=2
            )
        )



    print("\n==============================")
    print("REMOVING DUPLICATE QUERIES")
    print("==============================\n")



    # =========================================
    # 5. QUERY DEDUPLICATION
    # =========================================

    final_queries = remove_duplicate_queries(
        ranked_queries.selected_queries
    )


    print(
        f"Unique Queries: {len(final_queries)}"
    )


    for query in final_queries:

        print(
            query.model_dump_json(
                indent=2
            )
        )



    print("\n==============================")
    print("SERP SEARCH")
    print("==============================\n")



    # =========================================
    # 6. SERP API SEARCH
    # =========================================

    all_results = []


    for query in final_queries:


        print(
            f"Searching: {query.query}"
        )


        results = search_google(
            query.query,
            num_results=10
        )


        all_results.extend(
            results
        )



    print(
        f"\nTotal SERP Results: {len(all_results)}"
    )



    print("\n==============================")
    print("URL CLASSIFICATION")
    print("==============================\n")



    # =========================================
    # 7. URL CLASSIFIER
    # =========================================

    serp_data = SERPResultList(
        results=all_results
    )


    classified_urls = classify_urls(
        serp_data
    )



    for url in classified_urls.results:

        print(
            url.model_dump_json(
                indent=2
            )
        )



    print("\n==============================")

    valid_leads = [

        url for url in classified_urls.results

        if url.is_lead

    ]


    print(
        f"Potential Leads Found: {len(valid_leads)}"
    )

    print("==============================")



if __name__ == "__main__":

    main()