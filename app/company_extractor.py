import os

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from dotenv import load_dotenv

from openai import AzureOpenAI

from app.schemas import CompanyProfile


# ============================================================
# ENVIRONMENT
# ============================================================

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
# EXTRACTION PROMPT
# ============================================================

COMPANY_EXTRACTION_PROMPT = """

You are a B2B buyer intelligence extraction agent.

Analyze the supplied company website content.

The objective is to determine whether this company could
potentially BUY products from an exporter.

Extract only information supported by the website.

------------------------------------------------------------
FIELDS
------------------------------------------------------------

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

------------------------------------------------------------
BUYER TYPES
------------------------------------------------------------

Allowed:

- importer
- distributor
- wholesaler
- food_processor
- manufacturer
- trading_company
- retailer

Only assign a type if there is evidence.

------------------------------------------------------------
IMPORTANT MANUFACTURER RULE
------------------------------------------------------------

Do NOT classify a company as a manufacturer merely because
it:

- packages goods
- stores goods
- distributes goods
- provides logistics
- provides private labeling

Manufacturer means the company actually manufactures or
transforms products.

------------------------------------------------------------
BUYING SIGNALS
------------------------------------------------------------

Strong signals include:

- importing
- international suppliers
- procurement
- sourcing
- purchasing
- raw material sourcing
- wholesale buying
- supplier requirements
- trading/import activity

Only report signals supported by the website.

------------------------------------------------------------
CONTACT INFORMATION
------------------------------------------------------------

Only extract contact information explicitly present.

Never invent:

- email
- phone
- address
- LinkedIn

------------------------------------------------------------
PRODUCTS
------------------------------------------------------------

Only list products explicitly supported by the website.

------------------------------------------------------------
IMPORTANT
------------------------------------------------------------

Be conservative.

If information is unavailable:

single field -> null
list field -> []

If importing activity is not supported:

importing_activity -> false

Return ONLY the structured CompanyProfile.
"""


# ============================================================
# SINGLE COMPANY
# ============================================================

def extract_company_profile(
    scraped_data: dict
) -> CompanyProfile:

    website = (

        scraped_data.get(
            "company_url"
        )

        or scraped_data.get(
            "url"
        )

        or ""

    )


    title = scraped_data.get(
        "title",
        ""
    )


    content = (

        scraped_data.get(
            "combined_text"
        )

        or scraped_data.get(
            "text_content"
        )

        or ""

    )


    # Prevent huge prompts
    content = content[
        :15000
    ]


    user_prompt = f"""
COMPANY WEBSITE:
{website}

PAGE TITLE:
{title}

WEBSITE CONTENT:
{content}
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

        response_format=CompanyProfile,

        temperature=0.0

    )


    profile = response.choices[
        0
    ].message.parsed


    # Always preserve the actual source URL.

    if not profile.website:

        profile.website = website


    return profile


# ============================================================
# MULTIPLE COMPANIES
# ============================================================

def extract_multiple_company_profiles(
    scraped_data_list: list[dict]
) -> list[CompanyProfile]:

    valid_data = [

        item

        for item in scraped_data_list

        if item.get(
            "combined_text"
        )

    ]


    if not valid_data:

        return []


    profiles = []


    with ThreadPoolExecutor(
        max_workers=5
    ) as executor:


        future_map = {

            executor.submit(

                extract_company_profile,

                item

            ): item

            for item in valid_data

        }


        for future in as_completed(
            future_map
        ):

            try:

                profile = future.result()

                profiles.append(
                    profile
                )


            except Exception as e:

                item = future_map[
                    future
                ]


                print(
                    "Company extraction failed:",
                    item.get(
                        "company_url",
                        ""
                    ),
                    "->",
                    e
                )


    return profiles