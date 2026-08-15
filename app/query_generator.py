import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.schemas import SearchQueryList
from app.prompts import QUERY_GENERATOR_PROMPT


# Load environment variables
load_dotenv()


# Azure OpenAI client
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


def generate_queries(search_plan):

    response = client.beta.chat.completions.parse(

        model=deployment,

        messages=[
            {
                "role": "system",
                "content": QUERY_GENERATOR_PROMPT
            },

            {
                "role": "user",
                "content": search_plan.model_dump_json()
            }
        ],

        response_format=SearchQueryList
    )


    return response.choices[0].message.parsed