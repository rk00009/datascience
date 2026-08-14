import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"

load_dotenv(
    dotenv_path=env_path,
    override=True
)

print("Endpoint:", repr(os.getenv("AZURE_OPENAI_ENDPOINT")))
print("Deployment:", repr(os.getenv("AZURE_OPENAI_DEPLOYMENT")))
print("API Version:", repr(os.getenv("AZURE_OPENAI_API_VERSION")))
print("API Key loaded:", bool(os.getenv("AZURE_OPENAI_API_KEY")))

