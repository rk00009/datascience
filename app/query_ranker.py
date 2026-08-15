import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.schemas import RankedQueryList
from app.prompts import QUERY_RANKER_PROMPT


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



def rank_queries(search_queries):


    response = client.beta.chat.completions.parse(

        model=deployment,

        messages=[

            {
                "role":"system",
                "content":QUERY_RANKER_PROMPT
            },

            {
                "role":"user",
                "content":search_queries.model_dump_json()
            }

        ],

        response_format=RankedQueryList
    )


    return response.choices[0].message.parsed