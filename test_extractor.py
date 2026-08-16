from app.web_scraper import scrape_website
from app.company_extractor import extract_company_profile


url="https://www.atco.de"


scraped_data = scrape_website(url)


profile = extract_company_profile(
    scraped_data
)


print(
    profile.model_dump_json(
        indent=2
    )
)