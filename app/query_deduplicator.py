from rapidfuzz import fuzz


def calculate_similarity(query1, query2):

    return fuzz.token_set_ratio(
        query1,
        query2
    )


def remove_duplicate_queries(
        queries,
        threshold=85
):

    unique_queries = []


    for current_query in queries:

        duplicate = False


        for existing_query in unique_queries:

            similarity = calculate_similarity(
                current_query.query,
                existing_query.query
            )


            if similarity >= threshold:
                duplicate = True
                break


        if not duplicate:
            unique_queries.append(
                current_query
            )


    return unique_queries