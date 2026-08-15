import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.schemas import URLClassificationList
from app.prompts import URL_CLASSIFIER_PROMPT


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



def classify_urls(serp_results):


    response = client.beta.chat.completions.parse(

        model=deployment,

        messages=[

            {
                "role":"system",
                "content":URL_CLASSIFIER_PROMPT
            },

            {
                "role":"user",
                "content":serp_results.model_dump_json()
            }

        ],

        response_format=URLClassificationList

    )


    return response.choices[0].message.parsed