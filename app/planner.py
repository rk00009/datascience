import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.schemas import SearchPlan


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
# SEARCH PLANNER PROMPT
# ============================================================

SEARCH_PLANNER_PROMPT = """

You are a B2B export buyer discovery planning agent.

Your task is to convert a user's buyer requirement into a
compact and accurate search plan.

The goal is to help an exporter discover REAL companies that
may BUY the requested product in the requested market.

Extract only information useful for buyer discovery.

------------------------------------------------------------
PRODUCT
------------------------------------------------------------

Identify the main product.

Generate 3-5 useful commercial synonyms.

Example:

groundnut
→ peanuts
→ peanut kernels
→ groundnut kernels

Do not generate unrelated products.

------------------------------------------------------------
TARGET MARKET
------------------------------------------------------------

Identify the target country or market.

If the user says:

"buyers in Germany"

target_market = Germany

country = Germany

If the user specifies multiple countries, preserve them
accurately.

------------------------------------------------------------
SELLER ORIGIN
------------------------------------------------------------

If the user specifies where the exporter/seller is located,
extract it.

If not specified:

seller_origin = null

Do NOT invent a seller origin.

------------------------------------------------------------
BUYER TYPES
------------------------------------------------------------

Select only relevant buyer categories.

Possible categories:

- importer
- distributor
- wholesaler
- food_processor
- manufacturer
- trading_company
- retailer

For agricultural/food commodities, prioritize:

importer
distributor
wholesaler
food_processor
trading_company

Do not include every category automatically.

------------------------------------------------------------
BUYING SIGNALS
------------------------------------------------------------

Generate concise commercial buying signals.

Examples:

- product importer
- bulk purchase
- procurement
- sourcing
- supplier requirement
- RFQ
- raw material sourcing
- international supplier

Maximum 7 signals.

------------------------------------------------------------
KEYWORDS
------------------------------------------------------------

Generate useful search concepts that can later be converted
into Google/SERP queries.

Each keyword should combine:

PRODUCT + BUYER INTENT + MARKET

Example:

peanut importer Germany
peanut procurement Germany
groundnut wholesaler Germany

Maximum 10 keywords.

------------------------------------------------------------
LANGUAGES
------------------------------------------------------------

Return:

1. English

2. The dominant local language of the target market

For Germany:

English
German

Do not invent unnecessary languages.

------------------------------------------------------------
INTENT
------------------------------------------------------------

Choose exactly one:

buyer_discovery
importer_discovery
active_buyer_search
supplier_search

Use:

buyer_discovery
→ when the request generally asks for buyers

importer_discovery
→ when importers are the primary target

active_buyer_search
→ when the request indicates active purchasing,
procurement, RFQ, supplier requirements, etc.

supplier_search
→ only when the user is explicitly looking for suppliers

------------------------------------------------------------
RESULT LIMITS
------------------------------------------------------------

Use:

max_results = 50

for a normal MVP search.

Use:

max_queries = 8

Do not generate excessive queries.

------------------------------------------------------------
IMPORTANT
------------------------------------------------------------

The output must describe the USER'S requirement.

Do not invent:

- countries
- products
- buyer types
- buying activity
- seller origin

Return ONLY the structured SearchPlan.
"""


# ============================================================
# SEARCH PLANNER
# ============================================================

def create_search_plan(
    user_query: str
) -> SearchPlan:

    user_prompt = f"""
User buyer requirement:

{user_query}

Create the search plan.
"""


    response = client.beta.chat.completions.parse(

        model=deployment,

        messages=[

            {
                "role": "system",
                "content": SEARCH_PLANNER_PROMPT
            },

            {
                "role": "user",
                "content": user_prompt
            }

        ],

        response_format=SearchPlan,

        temperature=0.0

    )


    plan = response.choices[0].message.parsed


    # ========================================================
    # SAFETY LIMITS
    # ========================================================

    plan.product_synonyms = (
        plan.product_synonyms[:5]
    )


    plan.buying_signals = (
        plan.buying_signals[:7]
    )


    plan.keywords = (
        plan.keywords[:10]
    )


    plan.max_results = min(
        max(plan.max_results, 10),
        50
    )


    plan.max_queries = min(
        max(plan.max_queries, 5),
        8
    )


    return plan