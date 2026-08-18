import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.schemas import (
    SERPResultList,
    URLClassificationList
)


# ============================================================
# ENVIRONMENT
# ============================================================

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# AZURE CLIENT
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
# PROMPT
# ============================================================

URL_CLASSIFICATION_PROMPT = """

You are a B2B buyer discovery URL classifier.

The goal is to identify websites belonging to REAL companies
that could potentially BUY the requested product.

Analyze every supplied SERP result.

A potential buyer can be:

- importer
- distributor
- wholesaler
- food processor
- manufacturer
- trading company
- retailer

Strong buyer evidence includes:

- importing products
- international sourcing
- procurement
- purchasing
- wholesale activity
- distribution
- raw material sourcing
- supplier requirements

Prefer:

- official company websites
- legitimate business directories
- company product pages
- company about pages
- company contact pages

Reject:

- news
- blogs
- Wikipedia
- research papers
- market reports
- government pages
- social media
- generic informational websites
- obvious exporter-only websites
- irrelevant websites

IMPORTANT:

A website mentioning the product does NOT automatically
make it a buyer.

Use the title, URL and snippet to make the classification.

For every input result return:

- company_name
- url
- source_type
- is_lead
- lead_probability
- reason

lead_probability must be between 0 and 100.

Return ONLY the structured URLClassificationList.
"""


# ============================================================
# CLASSIFY URLS
# ============================================================

def classify_urls(
    serp_results: SERPResultList
) -> URLClassificationList:

    if not serp_results.results:

        return URLClassificationList(
            results=[]
        )


    # Keep development workload controlled.
    results = serp_results.results[:50]


    compact_results = []


    for index, result in enumerate(
        results
    ):

        compact_results.append({

            "id": index,

            "title": result.title,

            "url": result.url,

            "snippet": result.snippet

        })


    user_prompt = f"""

Classify the following SERP results.

The original search results represent a buyer discovery
search.

SERP RESULTS:

{compact_results}

Return one classification for each result.
"""


    response = client.beta.chat.completions.parse(

        model=deployment,

        messages=[

            {
                "role": "system",
                "content":
                URL_CLASSIFICATION_PROMPT
            },

            {
                "role": "user",
                "content":
                user_prompt
            }

        ],

        response_format=URLClassificationList,

        

    )


    classified = response.choices[
        0
    ].message.parsed


    # ========================================================
    # LOCAL SORTING
    # ========================================================

    classified.results.sort(

        key=lambda item:
        item.lead_probability,

        reverse=True

    )


    return classified