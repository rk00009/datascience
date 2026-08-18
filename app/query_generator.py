import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.schemas import SearchPlan, SearchQueryList


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
# QUERY GENERATION PROMPT
# ============================================================

QUERY_GENERATION_PROMPT = """

You are a B2B export buyer discovery search-query generator.

Your job is to convert a buyer search plan into highly targeted
Google search queries that can discover REAL potential buyers.

The user is an exporter looking for companies that may BUY the
specified product.

Generate commercially useful search queries.

IMPORTANT RULES:

1. Focus on BUYERS, not sellers.

2. Prioritize:
   - importers
   - distributors
   - wholesalers
   - food processors
   - manufacturers that purchase the product as a raw material
   - trading companies

3. Include strong commercial intent such as:
   - importer
   - procurement
   - sourcing
   - purchasing
   - bulk purchase
   - supplier requirement
   - RFQ
   - buying
   - wholesale

4. Use product synonyms when useful.

5. Use the target country/market in every query.

6. Use the local language when appropriate.

7. Avoid generic queries such as:
   "companies in Germany"
   "groundnut companies"

8. Avoid queries targeting:
   - news
   - market reports
   - research papers
   - government information
   - social media

9. Do NOT generate duplicate or nearly identical queries.

10. Generate no more than 10 queries.

11. Each query should have a distinct purpose.

12. Prioritize HIGH intent queries.

13. Do not invent facts about companies.

Return ONLY the structured SearchQueryList format.
"""


# ============================================================
# QUERY GENERATOR
# ============================================================

def generate_queries(
    search_plan: SearchPlan
) -> SearchQueryList:

    # Keep the prompt compact.
    # We don't need to send unnecessary fields separately.

    user_prompt = f"""
Search Plan:

{search_plan.model_dump_json(indent=2)}

Generate the best search queries for this plan.
Maximum queries: {min(search_plan.max_queries, 10)}
"""


    response = client.beta.chat.completions.parse(

        model=deployment,

        messages=[

            {
                "role": "system",
                "content": QUERY_GENERATION_PROMPT
            },

            {
                "role": "user",
                "content": user_prompt
            }

        ],

        response_format=SearchQueryList,

        

    )


    result = response.choices[0].message.parsed


    # Safety limit
    result.queries = result.queries[
        :min(search_plan.max_queries, 10)
    ]


    return result