from urllib.parse import urljoin, urlparse, urldefrag

from app.web_scraper import scrape_website


# ============================================================
# IMPORTANT PAGE KEYWORDS
# ============================================================

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


MAX_PAGES = 1


# ============================================================
# NORMALIZE URL
# ============================================================

def normalize_url(url):

    """
    Removes fragments such as:

    #section
    #product-grid
    #contact

    so that the crawler does not treat
    the same webpage as multiple pages.
    """

    url, _ = urldefrag(url)

    parsed = urlparse(url)

    # Remove trailing slash except for homepage
    path = parsed.path.rstrip("/")

    if not path:
        path = ""

    normalized = (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
        f"{path}"
    )

    return normalized


# ============================================================
# SAME DOMAIN CHECK
# ============================================================

def is_same_domain(base_url, link):

    base_domain = urlparse(
        normalize_url(base_url)
    ).netloc.lower()

    link_domain = urlparse(
        normalize_url(link)
    ).netloc.lower()

    return (
        base_domain == link_domain
        or link_domain == ""
    )


# ============================================================
# USEFUL PAGE CHECK
# ============================================================

def is_useful_page(url):

    normalized_url = normalize_url(
        url
    )

    url_lower = normalized_url.lower()

    for keyword in IMPORTANT_KEYWORDS:

        if keyword in url_lower:

            return True

    return False


# ============================================================
# EXTRACT USEFUL INTERNAL LINKS
# ============================================================

def extract_useful_links(
    base_url,
    links
):

    useful_links = []

    base_url = normalize_url(
        base_url
    )


    for link in links:

        # Convert relative URL to absolute URL
        absolute_url = urljoin(
            base_url,
            link
        )


        # Remove #fragment
        absolute_url = normalize_url(
            absolute_url
        )


        # Ignore external websites
        if not is_same_domain(
            base_url,
            absolute_url
        ):
            continue


        # Ignore homepage
        if absolute_url == base_url:

            continue


        # Only keep useful pages
        if not is_useful_page(
            absolute_url
        ):

            continue


        # Avoid duplicates
        if absolute_url not in useful_links:

            useful_links.append(
                absolute_url
            )


        # Stop once we have enough
        if len(useful_links) >= MAX_PAGES:

            break


    return useful_links


# ============================================================
# CRAWL WEBSITE
# ============================================================

def crawl_website(url):

    print(
        f"\nCrawling website: {url}"
    )


    # --------------------------------------------------------
    # Normalize starting URL
    # --------------------------------------------------------

    url = normalize_url(
        url
    )


    # --------------------------------------------------------
    # STEP 1: Scrape homepage
    # --------------------------------------------------------

    homepage_data = scrape_website(
        url
    )


    # --------------------------------------------------------
    # STEP 2: Find useful internal links
    # --------------------------------------------------------

    useful_links = extract_useful_links(

        url,

        homepage_data.get(
            "links",
            []
        )

    )


    print(
        f"\nUseful internal pages found: "
        f"{len(useful_links)}"
    )


    for link in useful_links:

        print(
            f"  → {link}"
        )


    # --------------------------------------------------------
    # STEP 3: Build page list
    # --------------------------------------------------------

    pages_to_scrape = [

        url

    ] + useful_links


    # Remove duplicates while preserving order

    pages_to_scrape = list(
        dict.fromkeys(
            pages_to_scrape
        )
    )


    print(
        f"\nTotal pages to scrape: "
        f"{len(pages_to_scrape)}"
    )


    # --------------------------------------------------------
    # STEP 4: Scrape each page
    # --------------------------------------------------------

    combined_text = ""

    scraped_pages = []


    for page_url in pages_to_scrape:

        print(
            f"\nScraping page: {page_url}"
        )


        # Homepage already scraped
        if page_url == url:

            data = homepage_data

        else:

            data = scrape_website(
                page_url
            )


        scraped_pages.append(
            page_url
        )


        page_text = data.get(
            "text_content",
            ""
        )


        if page_text:

            combined_text += (

                "\n\n"
                "================================"
                "\n"
                f"SOURCE PAGE: {page_url}"
                "\n"
                "================================"
                "\n\n"
                +
                page_text

            )


    # --------------------------------------------------------
    # STEP 5: Return combined result
    # --------------------------------------------------------

    return {

        "company_url": url,

        "pages_scraped": scraped_pages,

        "combined_text": combined_text

    }