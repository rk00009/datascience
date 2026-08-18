import os
import re

from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel

from app.schemas import CompanyProfile


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# AZURE OPENAI
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
# PERFORMANCE CONFIG
# ============================================================

MAX_COMPANY_TEXT = 8000

BATCH_SIZE = 5


# ============================================================
# BATCH RESPONSE
# ============================================================

class CompanyProfileBatch(
    BaseModel
):

    companies: list[CompanyProfile]


# ============================================================
# PROMPT
# ============================================================

COMPANY_EXTRACTION_PROMPT = """

You are a B2B buyer intelligence extraction engine.

The input contains website content from potential commercial
buyers.

Extract accurate structured company information.

Use ONLY information supported by the supplied content.

============================================================
FIELDS
============================================================

Extract:

company_name
website
country
description
buyer_type
products
importing_activity
buying_signals
email
phone
address
contact_page
linkedin

============================================================
BUYER TYPES
============================================================

Allowed:

importer
distributor
wholesaler
food_processor
manufacturer
trading_company
retailer

Only use types supported by evidence.

============================================================
IMPORTANT
============================================================

A company mentioning a product is NOT automatically a buyer.

Look for evidence of:

- importing
- sourcing
- procurement
- wholesale
- distribution
- manufacturing
- trading
- raw-material purchasing
- international suppliers

============================================================
MANUFACTURER
============================================================

Do not classify packaging, storage, logistics or private-label
services as manufacturing.

Manufacturing requires actual production or transformation.

============================================================
BUYING SIGNALS
============================================================

Only include buying signals supported by the website.

Examples:

- imports from international suppliers
- sources raw materials
- procurement activity
- wholesale purchasing
- supplier relationships
- international sourcing
- purchasing requirements

Do not invent active purchasing if the website does not
support it.

============================================================
CONTACT INFORMATION
============================================================

Extract only explicitly available:

email
phone
address
contact page
LinkedIn

Never invent missing information.

============================================================
MISSING DATA
============================================================

If unavailable:

single value -> null
list -> []

importing_activity -> false

============================================================
OUTPUT
============================================================

Return exactly one profile for each supplied company.

Return ONLY CompanyProfileBatch.
"""


# ============================================================
# CLEAN WEBSITE TEXT
# ============================================================

def prepare_company_text(
    scraped_data: dict
) -> str:

    content = (

        scraped_data.get(
            "combined_text"
        )

        or ""

    )


    if not content:
        return ""


    # Remove repeated whitespace.

    content = re.sub(
        r"\s+",
        " ",
        content
    ).strip()


    # Keep prompt small.

    return content[
        :MAX_COMPANY_TEXT
    ]


# ============================================================
# BUILD INPUT
# ============================================================

def build_company_input(
    scraped_data: dict,
    company_id: int
) -> dict:

    website = (
        scraped_data.get(
            "company_url"
        )
        or ""
    )


    return {

        "company_id": company_id,

        "website": website,

        "title": scraped_data.get(
            "title",
            ""
        ),

        "content": prepare_company_text(
            scraped_data
        )

    }


# ============================================================
# SINGLE COMPANY EXTRACTION
# ============================================================

def extract_company_profile(
    scraped_data: dict
) -> CompanyProfile:

    # Don't send failed crawls to Luna.

    if not scraped_data.get(
        "crawl_success"
    ):

        raise ValueError(
            "Cannot extract a failed crawl"
        )


    company_input = build_company_input(
        scraped_data,
        1
    )


    if not company_input["content"]:

        raise ValueError(
            "No website content available"
        )


    user_prompt = f"""

Extract this company.

COMPANY ID:
{company_input["company_id"]}

WEBSITE:
{company_input["website"]}

TITLE:
{company_input["title"]}

WEBSITE CONTENT:
{company_input["content"]}
"""


    response = client.beta.chat.completions.parse(

        model=deployment,

        messages=[

            {
                "role": "system",
                "content":
                COMPANY_EXTRACTION_PROMPT
            },

            {
                "role": "user",
                "content":
                user_prompt
            }

        ],

        response_format=CompanyProfileBatch

        # IMPORTANT:
        # Do NOT add temperature=0.
        # gpt-5.6-luna only supports its default.

    )


    parsed = response.choices[
        0
    ].message.parsed


    if not parsed.companies:

        raise ValueError(
            "Luna returned no company"
        )


    profile = parsed.companies[0]


    # Preserve actual source URL.

    if not profile.website:

        profile.website = (
            company_input["website"]
        )


    return profile


# ============================================================
# BATCH EXTRACTION
# ============================================================

def extract_company_batch(
    scraped_data_list: list[dict]
) -> list[CompanyProfile]:

    # --------------------------------------------------------
    # ONLY SUCCESSFUL CRAWLS
    # --------------------------------------------------------

    valid_data = [

        item

        for item in scraped_data_list

        if item.get(
            "crawl_success"
        )
        and item.get(
            "combined_text"
        )

    ]


    if not valid_data:

        return []


    company_inputs = []


    for index, scraped_data in enumerate(
        valid_data,
        start=1
    ):

        company_inputs.append(

            build_company_input(
                scraped_data,
                index
            )

        )


    # --------------------------------------------------------
    # BUILD COMPACT PROMPT
    # --------------------------------------------------------

    sections = []


    for company in company_inputs:

        sections.append(

            f"""
COMPANY ID: {company["company_id"]}

WEBSITE:
{company["website"]}

TITLE:
{company["title"]}

CONTENT:
{company["content"]}
"""

        )


    user_prompt = """

Extract ALL companies below.

Rules:

1. Return one profile per company.
2. Do not merge companies.
3. Do not invent missing information.
4. Preserve each company's website.

COMPANIES:

""" + "\n".join(
        sections
    )


    response = client.beta.chat.completions.parse(

        model=deployment,

        messages=[

            {
                "role": "system",
                "content":
                COMPANY_EXTRACTION_PROMPT
            },

            {
                "role": "user",
                "content":
                user_prompt
            }

        ],

        response_format=CompanyProfileBatch

        # No temperature parameter.
    )


    parsed = response.choices[
        0
    ].message.parsed


    profiles = parsed.companies


    # --------------------------------------------------------
    # Restore websites if model omitted them
    # --------------------------------------------------------

    website_map = {

        company["company_id"]:
        company["website"]

        for company
        in company_inputs

    }


    for profile in profiles:

        if not profile.website:

            # We don't know the model's company ID here,
            # so don't guess. It remains None/empty.

            pass


    return profiles


# ============================================================
# MULTIPLE COMPANY EXTRACTION
# ============================================================

def extract_multiple_company_profiles(
    scraped_data_list: list[dict]
) -> list[CompanyProfile]:

    # --------------------------------------------------------
    # FILTER FAILED CRAWLS FIRST
    # --------------------------------------------------------

    valid_data = [

        item

        for item in scraped_data_list

        if item.get(
            "crawl_success"
        )
        and item.get(
            "combined_text"
        )

    ]


    if not valid_data:

        print(
            "No successfully crawled companies."
        )

        return []


    print(
        f"Valid companies for extraction: "
        f"{len(valid_data)}"
    )


    all_profiles = []


    # --------------------------------------------------------
    # BATCH INTO GROUPS OF 5
    # --------------------------------------------------------

    for start in range(
        0,
        len(valid_data),
        BATCH_SIZE
    ):

        batch = valid_data[
            start:
            start + BATCH_SIZE
        ]


        batch_number = (
            start // BATCH_SIZE
        ) + 1


        print(
            f"\nExtracting batch "
            f"{batch_number}"
            f" ({len(batch)} companies)"
        )


        try:

            profiles = extract_company_batch(
                batch
            )


            all_profiles.extend(
                profiles
            )


            print(
                f"Extracted: "
                f"{len(profiles)}"
            )


        except Exception as e:

            print(
                f"Batch extraction failed:"
            )

            print(
                str(e)
            )


    print(
        f"\nTotal profiles extracted: "
        f"{len(all_profiles)}"
    )


    return all_profiles