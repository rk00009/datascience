from app.web_scraper import scrape_website


url = "https://www.atco.de"


data = scrape_website(url)


print("\n==============================")
print("PAGE TITLE")
print("==============================")

print(data["title"])


print("\n==============================")
print("WEBSITE CONTENT")
print("==============================")

print(
    data["text_content"][:5000]
)


print("\n==============================")
print("LINKS FOUND")
print("==============================")

print(
    f"Total links: {len(data['links'])}"
)