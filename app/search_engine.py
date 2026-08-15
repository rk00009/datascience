import os

from dotenv import load_dotenv
from serpapi import GoogleSearch


load_dotenv()


SERP_API_KEY = os.getenv(
    "SERPAPI_KEY"
)



def search_google(query, num_results=10):

    params = {

        "engine": "google",

        "q": query,

        "api_key": SERP_API_KEY,

        "num": num_results,

        "gl": "de",

        "hl": "en"

    }


    search = GoogleSearch(params)


    results = search.get_dict()


    organic_results = results.get(
        "organic_results",
        []
    )


    formatted_results = []


    for result in organic_results:

        formatted_results.append({

            "title":
            result.get("title"),

            "url":
            result.get("link"),

            "snippet":
            result.get("snippet")

        })


    return formatted_results