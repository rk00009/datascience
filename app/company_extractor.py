import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.schemas import CompanyProfile
from app.prompts import COMPANY_EXTRACTION_PROMPT


load_dotenv()


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



def extract_company_profile(scraped_data):


    # Combine important website information

    website_information = f"""

Website URL:
{scraped_data.get('url')}


Page Title:
{scraped_data.get('title')}


Website Content:

{scraped_data.get('text_content')}

"""


    response = client.beta.chat.completions.parse(

        model=deployment,


        messages=[

            {
                "role": "system",

                "content": COMPANY_EXTRACTION_PROMPT

            },


            {
                "role": "user",

                "content": website_information

            }

        ],


        response_format=CompanyProfile

    )


    profile = response.choices[0].message.parsed



    # Ensure website is always populated

    if not profile.website:

        profile.website = scraped_data.get(
            "url",
            ""
        )


    return profile