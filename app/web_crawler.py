from urllib.parse import urljoin, urlparse

from app.web_scraper import scrape_website



# Pages that contain useful company information

IMPORTANT_KEYWORDS = [

    # English
    "about",
    "company",
    "product",
    "products",
    "service",
    "contact",
    "imprint",

    # German
    "uber",
    "ueber",
    "unternehmen",
    "produkte",
    "sortiment",
    "kontakt",
    "impressum"

]


MAX_PAGES = 5



def is_same_domain(base_url, link):

    base_domain = urlparse(base_url).netloc

    link_domain = urlparse(link).netloc


    return (
        base_domain == link_domain
        or link_domain == ""
    )



def is_useful_page(url):

    url_lower = url.lower()


    for keyword in IMPORTANT_KEYWORDS:

        if keyword in url_lower:
            return True


    return False



def extract_useful_links(
        base_url,
        links
):

    useful_links = []


    for link in links:

        absolute_url = urljoin(
            base_url,
            link
        )


        if not is_same_domain(
            base_url,
            absolute_url
        ):
            continue



        if is_useful_page(
            absolute_url
        ):

            if absolute_url not in useful_links:

                useful_links.append(
                    absolute_url
                )


    return useful_links[:MAX_PAGES]



def crawl_website(url):


    print(
        f"\nCrawling website: {url}"
    )


    # First scrape homepage

    homepage_data = scrape_website(
        url
    )


    pages = [

        url

    ]



    useful_links = extract_useful_links(

        url,

        homepage_data["links"]

    )



    pages.extend(
        useful_links
    )



    combined_text = ""



    scraped_pages = []



    for page in pages:


        print(
            f"Scraping page: {page}"
        )


        data = scrape_website(
            page
        )


        scraped_pages.append(
            page
        )


        combined_text += (

            "\n\n"
            +
            data["text_content"]

        )



    return {

        "company_url": url,

        "pages_scraped": scraped_pages,

        "combined_text": combined_text

    }