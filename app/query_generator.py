import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.schemas import (
    SearchPlan,
    SearchQueryList,
)


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(
    override=True
)


# ============================================================
# AZURE OPENAI CONFIGURATION
# ============================================================

AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT"
)

AZURE_OPENAI_API_KEY = os.getenv(
    "AZURE_OPENAI_API_KEY"
)

AZURE_OPENAI_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT"
)

AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION"
)


missing = []

if not AZURE_OPENAI_ENDPOINT:
    missing.append("AZURE_OPENAI_ENDPOINT")

if not AZURE_OPENAI_API_KEY:
    missing.append("AZURE_OPENAI_API_KEY")

if not AZURE_OPENAI_DEPLOYMENT:
    missing.append("AZURE_OPENAI_DEPLOYMENT")

if not AZURE_OPENAI_API_VERSION:
    missing.append("AZURE_OPENAI_API_VERSION")


if missing:

    raise RuntimeError(
        "Missing Azure OpenAI environment variables: "
        + ", ".join(missing)
    )


# ============================================================
# AZURE OPENAI CLIENT
# ============================================================

client = AzureOpenAI(

    api_key=AZURE_OPENAI_API_KEY,

    azure_endpoint=AZURE_OPENAI_ENDPOINT,

    api_version=AZURE_OPENAI_API_VERSION,

)


# ============================================================
# QUERY GENERATION
# ============================================================

def generate_search_queries(
    search_plan: SearchPlan
) -> SearchQueryList:

    """
    Generate company-focused B2B search queries.

    The objective is to discover actual companies rather
    than RFQ boards, supplier directories, marketplaces,
    exporters and generic information pages.
    """

    prompt = f"""
You are an expert B2B export buyer-research analyst.

Generate search-engine queries that discover REAL COMPANIES
that could BUY the requested product.

SEARCH PLAN
============

Original query:
{search_plan.original_query}

Product:
{search_plan.product}

Product synonyms:
{search_plan.product_synonyms}

Target market:
{search_plan.target_market}

Buyer types:
{search_plan.buyer_types}

Buying signals:
{search_plan.buying_signals}

Keywords:
{search_plan.keywords}

Languages:
{search_plan.languages}

Intent:
{search_plan.intent}


OBJECTIVE
=========

Find actual companies operating in the target market.

Priority buyer types:

- importers
- wholesalers
- distributors
- food manufacturers
- food processors
- snack manufacturers
- food ingredient companies
- commodity traders
- trading companies


IMPORTANT
=========

Prioritize queries that discover actual company websites.

Avoid queries primarily containing:

- RFQ
- buy requirements
- buying leads
- supplier requirements
- supplier directories
- buyer directories
- supplier marketplaces
- B2B marketplaces
- exporter lists
- supplier lists
- trade-data websites
- generic market reports
- generic product articles


WHY
===

These terms frequently produce marketplaces, directories,
supplier websites, buying-lead platforms and articles rather
than actual prospective buyer companies.


QUERY STRATEGY
==============

Combine:

1. Product
2. Target market
3. Buyer/company type
4. Commercial terminology


ENGLISH TERMS
=============

Use terms such as:

- importer
- wholesaler
- distributor
- food manufacturer
- food processor
- snack manufacturer
- food ingredients
- trading company
- commodity trader
- nut importer
- food company


GERMAN TERMS
============

For Germany, useful terms include:

- Importeur
- Großhandel
- Händler
- Lebensmittelhersteller
- Lebensmittelindustrie
- Lebensmittelzutaten
- Snackhersteller
- Handelsunternehmen
- Agrarhandel
- Nussimporteur
- Erdnussimporteur
- Lebensmittelverarbeiter


GOOD EXAMPLES
=============

Germany peanut importer company

Germany peanut wholesaler GmbH

Germany peanut food distributor

Germany food ingredient distributor peanuts

Germany snack manufacturer peanuts

Germany food manufacturer peanuts

Germany agricultural trading company peanuts

Germany nut importer company

Erdnuss Importeur Deutschland GmbH

Erdnuss Großhandel Deutschland Unternehmen

Erdnuss Händler Deutschland

Lebensmittelhersteller Erdnüsse Deutschland

Snackhersteller Erdnüsse Deutschland

Lebensmittelindustrie Erdnüsse Deutschland

Handelsunternehmen Deutschland Erdnüsse

Nussimporteur Deutschland


BAD EXAMPLES
============

Do NOT generate:

peanut RFQ Germany

peanut buy requirements Germany

peanut supplier requirement Germany

peanut suppliers Germany

peanut exporters Germany

peanut supplier directory Germany

peanut buyers directory Germany

peanut buying leads Germany

peanut marketplace Germany


LANGUAGE
========

Use both English and local-language queries when useful.

For Germany, generate both English and German queries.

Do not mechanically translate every query.


DIVERSITY
=========

Create different discovery angles.

Examples:

Importer:
Germany peanut importer company

Wholesaler:
Germany peanut wholesaler GmbH

Distributor:
Germany peanut food distributor

Food manufacturer:
Germany snack manufacturer peanuts

Food processor:
Germany food processor peanuts

Trading company:
Germany commodity trading company peanuts

German importer:
Erdnuss Importeur Deutschland GmbH

German manufacturer:
Lebensmittelhersteller Erdnüsse Deutschland


QUERY COUNT
===========

Generate 8 to 12 queries.

Prefer 10 queries.

Avoid near-duplicates.


BUYER TYPE
==========

Assign the most appropriate buyer_type to each query.

Use buyer types from the SearchPlan whenever possible.

Examples:

importer
wholesaler
distributor
food_processor
trading_company


PRIORITY
========

Use only:

high
medium
low


QUALITY CHECK
=============

Every query should:

1. Contain the relevant product.
2. Target the requested market.
3. Target a real company or buyer type.
4. Have a reasonable chance of finding a company website.
5. Avoid marketplaces.
6. Avoid directories.
7. Avoid generic information pages.
8. Avoid supplier-only searches.
9. Be meaningfully different from the other queries.

Return ONLY the structured SearchQueryList.
"""


    try:

        response = client.beta.chat.completions.parse(

            model=AZURE_OPENAI_DEPLOYMENT,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate high-quality B2B "
                        "company-discovery search queries."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            response_format=SearchQueryList,

        )

        parsed = (
            response
            .choices[0]
            .message
            .parsed
        )

        if parsed is None:

            raise RuntimeError(
                "Azure OpenAI returned no parsed query result."
            )

        return parsed

    except Exception as exc:

        raise RuntimeError(
            f"Azure OpenAI query generation failed: {exc}"
        ) from exc


# ============================================================
# COMPATIBILITY WRAPPER
# ============================================================

def generate_queries(
    search_plan: SearchPlan
) -> SearchQueryList:

    return generate_search_queries(
        search_plan
    )