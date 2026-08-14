import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"

load_dotenv(
    dotenv_path=env_path,
    override=True
)

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

print("Endpoint:", endpoint)
print("Deployment:", deployment)
print("API Version:", api_version)
print("API Key loaded:", bool(api_key))


# Create Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=api_version
)


# Test request
response = client.chat.completions.create(
    model=deployment,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain what an importer is in one sentence."
        }
    ]
)


print("\nMODEL RESPONSE:")
print(response.choices[0].message.content)