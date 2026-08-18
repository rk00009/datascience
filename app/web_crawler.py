import asyncio

from urllib.parse import (
    urljoin,
    urlparse,
    urldefrag
)

from playwright.async_api import (
    async_playwright
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_INTERNAL_PAGES = 1

MAX_CONCURRENT_SITES = 5

PAGE_TIMEOUT = 10000

MAX_TEXT_LENGTH = 15000


IMPORTANT_KEYWORDS = [

    # English
    "about",
    "company",
    "product",
    "products",
    "contact",
    "service",
    "services",
    "imprint",

    # German
    "ueber",
    "uber",
    "unternehmen",
    "produkte",
    "sortiment",
    "kontakt",
    "dienstleistung",
    "dienstleistungen",
    "impressum"
]


# ============================================================
# URL NORMALIZATION
# ============================================================

def normalize_url(
    url: str
) -> str:

    # Remove #fragment
    url, _ = urldefrag(
        url
    )

    parsed = urlparse(
        url
    )

    path = parsed.path.rstrip("/")


    if not path:

        path = ""


    return (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
        f"{path}"
    )


# ============================================================
# DOMAIN CHECK
# ============================================================

def same_domain(
    base_url: str,
    target_url: str
) -> bool:

    base_domain = urlparse(
        normalize_url(
            base_url
        )
    ).netloc.lower()


    target_domain = urlparse(
        normalize_url(
            target_url
        )
    ).netloc.lower()


    return (
        base_domain == target_domain
    )


# ============================================================
# USEFUL PAGE DETECTION
# ============================================================

def useful_link(
    url: str,
    anchor_text: str = ""
) -> bool:

    combined = (
        url.lower()
        + " "
        + anchor_text.lower()
    )


    return any(

        keyword in combined

        for keyword
        in IMPORTANT_KEYWORDS

    )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(
    text: str
) -> str:

    lines = []


    for line in text.splitlines():

        line = " ".join(
            line.split()
        )


        if len(line) < 3:
            continue


        lines.append(
            line
        )


    cleaned = "\n".join(
        lines
    )


    return cleaned[
        :MAX_TEXT_LENGTH
    ]


# ============================================================
# SCRAPE ONE PAGE
# ============================================================

async def scrape_page(
    page,
    url: str
) -> dict:

    print(
        f"  Scraping: {url}"
    )


    try:

        await page.goto(

            url,

            wait_until="domcontentloaded",

            timeout=PAGE_TIMEOUT

        )


        # Small wait for dynamic content.
        await page.wait_for_timeout(
            400
        )


    except Exception as e:

        print(
            f"  Page load warning: {e}"
        )


    # ========================================================
    # REMOVE UNNECESSARY ELEMENTS
    # ========================================================

    try:

        await page.evaluate(
            """
            () => {

                const selectors = [

                    'script',
                    'style',
                    'noscript',
                    'svg',
                    'iframe',

                    'nav',
                    'footer',

                    '[id*="cookie"]',
                    '[class*="cookie"]',

                    '[id*="consent"]',
                    '[class*="consent"]',

                    '[role="dialog"]',
                    '[role="alertdialog"]'

                ];


                for (
                    const selector
                    of selectors
                ) {

                    document
                        .querySelectorAll(
                            selector
                        )
                        .forEach(
                            element =>
                            element.remove()
                        );

                }

            }
            """
        )

    except Exception:
        pass


    # ========================================================
    # TITLE
    # ========================================================

    try:

        title = await page.title()

    except Exception:

        title = ""


    # ========================================================
    # MAIN CONTENT
    # ========================================================

    text = ""


    try:

        main = page.locator(
            "main"
        )


        if await main.count():

            text = await main.inner_text(
                timeout=2000
            )

        else:

            text = await page.locator(
                "body"
            ).inner_text(
                timeout=3000
            )


    except Exception:

        try:

            text = await page.locator(
                "body"
            ).inner_text(
                timeout=3000
            )

        except Exception:

            text = ""


    text = clean_text(
        text
    )


    # ========================================================
    # FIND INTERNAL LINKS
    # ========================================================

    links = []


    try:

        elements = await page.locator(
            "a"
        ).all()


        for element in elements:

            href = await element.get_attribute(
                "href"
            )


            if not href:
                continue


            try:

                anchor_text = await element.inner_text()

            except Exception:

                anchor_text = ""


            absolute_url = normalize_url(

                urljoin(
                    url,
                    href
                )

            )


            if not same_domain(
                url,
                absolute_url
            ):

                continue


            if absolute_url == normalize_url(
                url
            ):

                continue


            if not useful_link(
                absolute_url,
                anchor_text
            ):

                continue


            if absolute_url not in links:

                links.append(
                    absolute_url
                )


    except Exception:
        pass


    return {

        "url": url,

        "title": title,

        "text_content": text,

        "links": links

    }


# ============================================================
# CRAWL ONE COMPANY
# ============================================================

async def crawl_single_website(
    browser,
    url: str
) -> dict:

    url = normalize_url(
        url
    )


    context = await browser.new_context(
        ignore_https_errors=True
    )


    page = await context.new_page()


    try:

        # ====================================================
        # PAGE 1 — HOMEPAGE
        # ====================================================

        homepage = await scrape_page(
            page,
            url
        )


        pages = [
            homepage
        ]


        # ====================================================
        # PAGE 2 — ONE USEFUL PAGE
        # ====================================================

        useful_pages = homepage[
            "links"
        ][
            :MAX_INTERNAL_PAGES
        ]


        if useful_pages:

            second_page = await scrape_page(

                page,

                useful_pages[0]

            )


            pages.append(
                second_page
            )


        # ====================================================
        # COMBINE CONTENT
        # ====================================================

        combined_parts = []


        for page_data in pages:

            combined_parts.append(

                f"""
SOURCE PAGE:
{page_data['url']}

TITLE:
{page_data['title']}

CONTENT:
{page_data['text_content']}
"""

            )


        combined_text = clean_text(

            "\n\n".join(
                combined_parts
            )

        )


        return {

            "company_url": url,

            "pages_scraped": [

                item["url"]

                for item in pages

            ],

            "combined_text":
            combined_text,

            "title":
            homepage["title"],

            "links":
            homepage["links"]

        }


    except Exception as e:

        print(
            f"  Crawl failed: "
            f"{url} -> {e}"
        )


        return {

            "company_url": url,

            "pages_scraped": [],

            "combined_text": "",

            "title": "",

            "links": []

        }


    finally:

        await page.close()

        await context.close()


# ============================================================
# MULTI-COMPANY CRAWLER
# ============================================================

async def crawl_websites_async(
    urls: list[str]
) -> list[dict]:

    urls = list(
        dict.fromkeys(

            normalize_url(url)

            for url in urls

            if url

        )
    )


    if not urls:

        return []


    semaphore = asyncio.Semaphore(
        MAX_CONCURRENT_SITES
    )


    async with async_playwright() as p:

        # ONE browser for all websites
        browser = await p.chromium.launch(
            headless=True
        )


        async def crawl_with_limit(
            url
        ):

            async with semaphore:

                return await crawl_single_website(

                    browser,

                    url

                )


        results = await asyncio.gather(

            *[
                crawl_with_limit(url)
                for url in urls
            ]

        )


        await browser.close()


    return results


# ============================================================
# SYNCHRONOUS WRAPPER
# ============================================================

def crawl_websites(
    urls: list[str]
) -> list[dict]:

    return asyncio.run(

        crawl_websites_async(
            urls
        )

    )


# ============================================================
# SINGLE WEBSITE WRAPPER
# ============================================================

def crawl_website(
    url: str
) -> dict:

    results = crawl_websites(
        [url]
    )


    if not results:

        return {

            "company_url": url,

            "pages_scraped": [],

            "combined_text": "",

            "title": "",

            "links": []

        }


    return results[0]