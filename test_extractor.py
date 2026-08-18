from app.web_crawler import crawl_websites
from app.company_extractor import (
    extract_multiple_company_profiles
)


urls = [

    "https://www.atco.de",

    "https://www.intersnack.de",

    "https://www.henrylamotte.com",

    "https://www.de-vele.de",

    "https://www.august-toepfer.de"

]


print(
    "\n=============================="
)

print(
    "CRAWLING"
)

print(
    "=============================="
)


scraped_data = crawl_websites(
    urls
)


successful = [

    item

    for item in scraped_data

    if item.get(
        "crawl_success"
    )

]


failed = [

    item

    for item in scraped_data

    if not item.get(
        "crawl_success"
    )

]


print(
    f"\nSuccessful crawls: "
    f"{len(successful)}"
)

print(
    f"Failed crawls: "
    f"{len(failed)}"
)


print(
    "\n=============================="
)

print(
    "AI EXTRACTION"
)

print(
    "=============================="
)


profiles = extract_multiple_company_profiles(
    scraped_data
)


print(
    f"\nProfiles extracted: "
    f"{len(profiles)}"
)


for profile in profiles:

    print(
        "\n------------------------------"
    )

    print(
        profile.model_dump_json(
            indent=2
        )
    )
    