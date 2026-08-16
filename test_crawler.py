from app.web_crawler import crawl_website



url = "https://www.atco.de"


result = crawl_website(
    url
)


print("\n====================")
print("PAGES SCRAPED")
print("====================")


for page in result["pages_scraped"]:

    print(page)



print("\n====================")
print("COMBINED CONTENT")
print("====================")


print(
    result["combined_text"][:5000]
)