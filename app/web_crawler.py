import asyncio
from urllib.parse import urljoin, urlparse, urldefrag

from playwright.async_api import async_playwright


# ============================================================
# CONFIGURATION
# ============================================================

MAX_INTERNAL_PAGES = 1
MAX_CONCURRENT_SITES = 5

PAGE_TIMEOUT = 8000
CONTENT_TIMEOUT = 2500

MAX_TEXT_LENGTH = 12000


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
# URL HELPERS
# ============================================================

def normalize_url(url: str) -> str:

    if not url:
        return ""

    # Remove #fragment
    url, _ = urldefrag(url)

    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    domain = parsed.netloc.lower()

    path = parsed.path.rstrip("/")

    if not path:
        path = ""

    return f"{scheme}://{domain}{path}"


def get_domain(url: str) -> str:

    normalized = normalize_url(url)

    return urlparse(
        normalized
    ).netloc.lower().replace(
        "www.",
        ""
    )


def get_company_root(url: str) -> str:

    normalized = normalize_url(url)

    parsed = urlparse(
        normalized
    )

    return (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
    )


def same_domain(
    base_url: str,
    target_url: str
) -> bool:

    return (
        get_domain(base_url)
        ==
        get_domain(target_url)
    )


# ============================================================
# LINK SELECTION
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
        for keyword in IMPORTANT_KEYWORDS
    )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(
    text: str
) -> str:

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = " ".join(
            line.split()
        )

        if len(line) < 3:
            continue

        lines.append(line)

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

    except Exception as e:

        print(
            f"  Page load failed: "
            f"{url}"
        )

        print(
            f"  Reason: {e}"
        )

        return {
            "success": False,
            "url": url,
            "title": "",
            "text_content": "",
            "links": []
        }


    # Give JS-heavy pages a tiny amount of time.
    # Do NOT use networkidle.

    try:

        await page.wait_for_timeout(
            300
        )

    except Exception:
        pass


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
                    const selector of selectors
                ) {

                    document
                        .querySelectorAll(selector)
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
    # CONTENT
    # ========================================================

    text = ""


    try:

        main = page.locator(
            "main"
        )

        if await main.count():

            text = await main.inner_text(
                timeout=CONTENT_TIMEOUT
            )

        else:

            text = await page.locator(
                "body"
            ).inner_text(
                timeout=CONTENT_TIMEOUT
            )

    except Exception:

        try:

            text = await page.locator(
                "body"
            ).inner_text(
                timeout=CONTENT_TIMEOUT
            )

        except Exception:

            text = ""


    text = clean_text(
        text
    )


    # ========================================================
    # LINKS
    # ========================================================

    links = []


    try:

        elements = await page.locator(
            "a"
        ).all()


        for element in elements:

            try:

                href = await element.get_attribute(
                    "href"
                )

                if not href:
                    continue

                anchor_text = await element.inner_text()

            except Exception:

                continue


            absolute_url = normalize_url(
                urljoin(
                    url,
                    href
                )
            )


            if not absolute_url:
                continue


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


    # A page with no text is not useful.

    if not text:

        return {
            "success": False,
            "url": url,
            "title": title,
            "text_content": "",
            "links": links
        }


    return {
        "success": True,
        "url": url,
        "title": title,
        "text_content": text,
        "links": links
    }


# ============================================================
# CRAWL ONE WEBSITE
# ============================================================

async def crawl_single_website(
    browser,
    url: str
) -> dict:

    original_url = url

    url = normalize_url(
        url
    )


    if not url:

        return {
            "company_url": original_url,
            "company_domain": "",
            "crawl_success": False,
            "pages_scraped": [],
            "combined_text": "",
            "title": "",
            "links": []
        }


    context = None
    page = None


    try:

        context = await browser.new_context(

            ignore_https_errors=True,

            viewport={
                "width": 1280,
                "height": 720
            }

        )


        page = await context.new_page()


        # ====================================================
        # HOMEPAGE
        # ====================================================

        homepage = await scrape_page(
            page,
            url
        )


        if not homepage["success"]:

            return {
                "company_url": url,
                "company_domain": get_domain(url),
                "crawl_success": False,
                "pages_scraped": [],
                "combined_text": "",
                "title": "",
                "links": []
            }


        pages = [
            homepage
        ]


        # ====================================================
        # ONE USEFUL INTERNAL PAGE
        # ====================================================

        useful_pages = homepage[
            "links"
        ][:MAX_INTERNAL_PAGES]


        if useful_pages:

            second_page = await scrape_page(
                page,
                useful_pages[0]
            )


            if second_page["success"]:

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
{page_data["url"]}

PAGE TITLE:
{page_data["title"]}

CONTENT:
{page_data["text_content"]}
"""

            )


        combined_text = clean_text(

            "\n\n".join(
                combined_parts
            )

        )


        if not combined_text:

            return {
                "company_url": url,
                "company_domain": get_domain(url),
                "crawl_success": False,
                "pages_scraped": [],
                "combined_text": "",
                "title": homepage["title"],
                "links": homepage["links"]
            }


        return {
            "company_url": url,
            "company_domain": get_domain(url),
            "crawl_success": True,
            "pages_scraped": [
                page_data["url"]
                for page_data in pages
            ],
            "combined_text": combined_text,
            "title": homepage["title"],
            "links": homepage["links"]
        }


    except Exception as e:

        print(
            f"  Crawler error: "
            f"{url}"
        )

        print(
            f"  Reason: {e}"
        )


        return {
            "company_url": url,
            "company_domain": get_domain(url),
            "crawl_success": False,
            "pages_scraped": [],
            "combined_text": "",
            "title": "",
            "links": []
        }


    finally:

        try:

            if page:
                await page.close()

        except Exception:
            pass


        try:

            if context:
                await context.close()

        except Exception:
            pass


# ============================================================
# MULTI WEBSITE CRAWLER
# ============================================================

async def crawl_websites_async(
    urls: list[str]
) -> list[dict]:

    # --------------------------------------------------------
    # Normalize + domain deduplicate
    # --------------------------------------------------------

    unique_urls = []

    seen_domains = set()


    for url in urls:

        normalized = normalize_url(
            url
        )

        if not normalized:
            continue


        domain = get_domain(
            normalized
        )


        if not domain:
            continue


        # One company = one domain.

        if domain in seen_domains:
            continue


        seen_domains.add(
            domain
        )

        unique_urls.append(
            normalized
        )


    if not unique_urls:
        return []


    print(
        f"\nUnique company domains: "
        f"{len(unique_urls)}"
    )


    semaphore = asyncio.Semaphore(
        MAX_CONCURRENT_SITES
    )


    async with async_playwright() as p:

        # ====================================================
        # ONE BROWSER INSTANCE
        # ====================================================

        browser = await p.chromium.launch(
            headless=True
        )


        async def crawl_with_limit(
            company_url
        ):

            async with semaphore:

                return await crawl_single_website(
                    browser,
                    company_url
                )


        results = await asyncio.gather(

            *[
                crawl_with_limit(url)
                for url in unique_urls
            ]

        )


        await browser.close()


    successful = [
        result
        for result in results
        if result.get("crawl_success")
    ]


    failed = [
        result
        for result in results
        if not result.get("crawl_success")
    ]


    print(
        f"\nCrawler Results"
    )

    print(
        f"Successful: {len(successful)}"
    )

    print(
        f"Failed: {len(failed)}"
    )


    return results


# ============================================================
# PUBLIC MULTI-SITE FUNCTION
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
# PUBLIC SINGLE-SITE FUNCTION
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
            "company_domain": get_domain(url),
            "crawl_success": False,
            "pages_scraped": [],
            "combined_text": "",
            "title": "",
            "links": []
        }


    return results[0]