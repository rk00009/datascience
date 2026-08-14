import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from app.schemas import SearchPlan
from app.prompts import SEARCH_PLANNER_PROMPT


load_dotenv()


client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)


deployment = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT"
)



def create_search_plan(user_query):

    response = client.beta.chat.completions.parse(

        model=deployment,

        messages=[

            {
                "role":"system",
                "content":SEARCH_PLANNER_PROMPT
            },

            {
                "role":"user",
                "content":user_query
            }

        ],

        response_format=SearchPlan
    )


    return response.choices[0].message.parsed