import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.schemas import (
    SearchQueryList,
    RankedQueryList
)


load_dotenv()


# ============================================================
# AZURE OPENAI CLIENT
# ============================================================

client = AzureOpenAI(

    api_version=os.getenv(
        "AZURE_OPENAI_API_VERSION"
    ),

    azure_endpoint=os.getenv(
        "AZURE_OPENAI_ENDPOINT"
    ),

    api_key=os.getenv(
        "AZURE_OPENAI_API_KEY"
    )
)


deployment = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT"
)


# ============================================================
# RANKING PROMPT
# ============================================================

QUERY_RANKING_PROMPT = """

You are a B2B export buyer-discovery query ranking agent.

Your job is to rank search queries based on their ability to
discover REAL potential BUYERS.

The exporter wants to find companies that may purchase the
specified product.

Evaluate each query using these factors:

1. PRODUCT RELEVANCE
Does the query clearly target the required product?

2. MARKET RELEVANCE
Does it target the correct country/market?

3. BUYER INTENT
Does it specifically target:
- importers
- distributors
- wholesalers
- food processors
- manufacturers
- trading companies?

4. COMMERCIAL INTENT
Does it contain strong signals such as:
- procurement
- sourcing
- purchasing
- bulk purchase
- supplier requirement
- RFQ
- buying?

5. DISCOVERY VALUE
Is the query likely to produce actual company websites or
business directories rather than generic informational pages?

SCORING:

90-100 = Excellent buyer discovery query
80-89  = Strong query
70-79  = Useful but less specific
60-69  = Weak
Below 60 = Poor

IMPORTANT:

Reject or assign a low score to queries that mainly target:

- market reports
- news
- research papers
- government information
- social media
- generic product information
- suppliers/exporters selling the product

Do NOT change the query text.

Do NOT invent new queries.

Rank the provided queries only.

Keep the strongest queries.

Prefer diversity:
Do not keep five queries that all target exactly the same
buyer type and intent.

Return ONLY the structured RankedQueryList format.
"""


# ============================================================
# QUERY RANKER
# ============================================================

def rank_queries(
    search_queries: SearchQueryList
) -> RankedQueryList:


    user_prompt = f"""
Search queries to evaluate:

{search_queries.model_dump_json(indent=2)}

Rank these queries from strongest to weakest.

Return the best queries first.
"""


    response = client.beta.chat.completions.parse(

        model=deployment,

        messages=[

            {
                "role": "system",
                "content": QUERY_RANKING_PROMPT
            },

            {
                "role": "user",
                "content": user_prompt
            }

        ],

        response_format=RankedQueryList,

        temperature=0.0

    )


    result = response.choices[0].message.parsed


    # Sort locally as an additional safety measure.
    # This avoids trusting the model's ordering.

    result.selected_queries.sort(

        key=lambda x: x.relevance_score,

        reverse=True

    )


    # Keep only the queries marked as useful.

    result.selected_queries = [

        query

        for query in result.selected_queries

        if query.keep

    ]


    # Safety limit

    result.selected_queries = (
        result.selected_queries[:10]
    )


    return result